"""
scd_utils.py
============
Slowly Changing Dimension (SCD) implementations — fully PySpark native.

Design principles
-----------------
* ALL merge logic runs in Spark (no Pandas, handles large loads).
* Target is read via Spark JDBC so the same connection/driver is reused.
* The merged Spark DataFrame is returned to run_pipeline_target() which
  writes it back via spark_class.write_via_spark() — no second write path.
* Join keys are auto-detected from the target table's primary keys via
  SQLAlchemy inspection (first load = no target yet, so all source columns
  act as identity until PKs are defined by the DB after first write).
* scd_id (UUID string) is generated as a surrogate row key for SCD2/6,
  separate from the business PK.
* SCD4 history table is always {target_table}_history, written in append mode.
* Write mode returned alongside the DataFrame so run_pipeline_target knows
  whether to OVERWRITE or APPEND.

Supported types
---------------
    SCD0  — Insert new rows only, never update.
    SCD1  — Upsert: overwrite changed rows, no history.
    SCD2  — Full row history via effective dates + is_current flag.
    SCD3  — Current + previous column per tracked column.
    SCD4  — Main table = current state; {table}_history = all versions.
    SCD6  — Hybrid of SCD1 + SCD2 + SCD3 (full traceability).

Public API
----------
    merged_df, write_mode, extra_writes = apply_scd(
        scd_type, source_df, spark_session,
        engine, target_table, schema_name,
        con_string, driver, logger
    )

    extra_writes: list of (df, table_name, mode) for SCD4 history table.
    write_mode  : "overwrite" for SCD0/1/2/3/6 main table,
                  "append"    for SCD4 history.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Tuple

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, BooleanType, TimestampType

from sqlalchemy.engine import Engine
from sqlalchemy import inspect as sa_inspect

from openetl_utils.enums import SCDType

_log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

_HIGH_DATE  = "9999-12-31 23:59:59"
_SCD_ID_COL = "scd_id"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _logger(logger):
    return logger or _log


def _get_join_keys(engine: Engine, table_name: str, schema: str, logger) -> Optional[List[str]]:
    """
    Inspect the target table's primary key columns via SQLAlchemy.
    Returns None if the table does not yet exist (first load).
    """
    log = _logger(logger)
    try:
        insp = sa_inspect(engine)
        if not insp.has_table(table_name, schema=schema):
            log.info(f"[SCD] Table {schema}.{table_name} does not exist yet — first load.")
            return None
        pk_cols = insp.get_pk_constraint(table_name, schema=schema).get("constrained_columns", [])
        if pk_cols:
            log.info(f"[SCD] Detected primary keys for {table_name}: {pk_cols}")
            return pk_cols
        log.warning(f"[SCD] No primary key found on {table_name}. All rows treated as new.")
        return None
    except Exception as e:
        log.warning(f"[SCD] PK inspection failed for {table_name}: {e}")
        return None


def _read_target_spark(
    spark_session: SparkSession,
    con_string: str,
    driver: str,
    table_name: str,
    schema: str,
) -> Optional[DataFrame]:
    """Read the existing target table via Spark JDBC. Returns None on first load."""
    try:
        full_table = f"{schema}.{table_name}" if schema else table_name
        df = (
            spark_session.read.format("jdbc")
            .option("url", con_string)
            .option("dbtable", full_table)
            .option("driver", driver)
            .load()
        )
        if df.head(1):
            return df
        return None
    except Exception:
        return None


def _non_key_cols(df: DataFrame, join_keys: List[str], reserved: List[str] = None) -> List[str]:
    skip = set(join_keys) | set(reserved or [])
    return [c for c in df.columns if c not in skip]


def _changed_condition(non_key_cols: List[str], src_alias: str = "src", tgt_alias: str = "tgt"):
    """Spark Column expression: any non-key column differs between src and tgt."""
    if not non_key_cols:
        return F.lit(False)
    conditions = [
        ~F.col(f"{src_alias}.{c}").cast("string").eqNullSafe(
            F.col(f"{tgt_alias}.{c}").cast("string")
        )
        for c in non_key_cols
    ]
    result = conditions[0]
    for c in conditions[1:]:
        result = result | c
    return result


def _uuid_udf():
    return F.udf(lambda: str(uuid.uuid4()), StringType())


def _add_scd2_cols(
    df: DataFrame,
    eff_col: str, end_col: str, is_cur_col: str,
    now_str: str, is_current: bool = True,
) -> DataFrame:
    end_val = _HIGH_DATE if is_current else now_str
    return (
        df
        .withColumn(_SCD_ID_COL, _uuid_udf()())
        .withColumn(eff_col,     F.lit(now_str).cast(TimestampType()))
        .withColumn(end_col,     F.lit(end_val).cast(TimestampType()))
        .withColumn(is_cur_col,  F.lit(is_current))
    )


# ─────────────────────────────────────────────────────────────────────────────
# SCD0 — Insert new rows only, never touch existing
# ─────────────────────────────────────────────────────────────────────────────

def _scd0(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    logger,
) -> Tuple[DataFrame, str]:
    log = _logger(logger)
    log.info("[SCD0] Insert-only merge.")

    if target_df is None or join_keys is None:
        log.info("[SCD0] First load — writing all source rows.")
        return source_df, "overwrite"

    # Only rows whose key is not already in the target
    new_rows = source_df.alias("src").join(
        target_df.select(join_keys).alias("tgt"),
        on=join_keys,
        how="left_anti",
    )
    # Preserve everything already in target; append only genuinely new rows
    merged = target_df.unionByName(new_rows, allowMissingColumns=True)
    log.info("[SCD0] Done.")
    return merged, "overwrite"


# ─────────────────────────────────────────────────────────────────────────────
# SCD1 — Upsert: overwrite changed rows, no history
# ─────────────────────────────────────────────────────────────────────────────

def _scd1(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    logger,
) -> Tuple[DataFrame, str]:
    log = _logger(logger)
    log.info("[SCD1] Upsert (overwrite) merge.")

    if target_df is None or join_keys is None:
        log.info("[SCD1] First load — writing all source rows.")
        return source_df, "overwrite"

    # Target rows with no matching key in source — keep them as-is
    untouched = target_df.alias("tgt").join(
        source_df.select(join_keys).alias("src"),
        on=join_keys,
        how="left_anti",
    )
    # Source rows replace any matching target row; new source rows are inserted
    merged = untouched.unionByName(source_df, allowMissingColumns=True)
    log.info("[SCD1] Done.")
    return merged, "overwrite"


# ─────────────────────────────────────────────────────────────────────────────
# SCD2 — Full row history with effective dates + is_current + scd_id
# ─────────────────────────────────────────────────────────────────────────────

def _scd2(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    eff_col: str, end_col: str, is_cur_col: str,
    logger,
) -> Tuple[DataFrame, str]:
    log = _logger(logger)
    log.info("[SCD2] Row-history merge.")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if target_df is None or join_keys is None:
        log.info("[SCD2] First load — all rows inserted as active.")
        return _add_scd2_cols(source_df, eff_col, end_col, is_cur_col, now_str, True), "overwrite"

    reserved   = [_SCD_ID_COL, eff_col, end_col, is_cur_col]
    non_keys   = _non_key_cols(source_df, join_keys, reserved)
    active_tgt = target_df.filter(F.col(is_cur_col) == True)
    hist_tgt   = target_df.filter(F.col(is_cur_col) == False)

    # Detect changed rows (source key exists in active target, values differ)
    joined      = source_df.alias("src").join(active_tgt.alias("tgt"), on=join_keys, how="left")
    changed_src = joined.filter(
        F.col(f"tgt.{join_keys[0]}").isNotNull() & _changed_condition(non_keys)
    ).select([F.col(f"src.{c}") for c in source_df.columns])

    # Detect new rows (source key not present at all in active target)
    new_src = source_df.alias("src").join(
        active_tgt.select(join_keys).alias("tgt"), on=join_keys, how="left_anti"
    )

    changed_keys = changed_src.select(join_keys).distinct()

    # Expire changed active rows
    expired = (
        active_tgt.alias("tgt")
        .join(changed_keys.alias("chg"), on=join_keys, how="inner")
        .select([F.col(f"tgt.{c}") for c in active_tgt.columns])
        .withColumn(end_col,    F.lit(now_str).cast(TimestampType()))
        .withColumn(is_cur_col, F.lit(False))
    )

    # Active rows that are unchanged — carry forward untouched
    unchanged_active = active_tgt.alias("tgt").join(
        changed_keys.alias("chg"), on=join_keys, how="left_anti"
    )

    # Insert new active rows for changed + brand-new keys
    to_insert   = changed_src.unionByName(new_src, allowMissingColumns=True)
    new_active  = _add_scd2_cols(to_insert, eff_col, end_col, is_cur_col, now_str, True)

    merged = (
        hist_tgt
        .unionByName(expired,          allowMissingColumns=True)
        .unionByName(unchanged_active, allowMissingColumns=True)
        .unionByName(new_active,       allowMissingColumns=True)
    )
    log.info("[SCD2] Done.")
    return merged, "overwrite"


# ─────────────────────────────────────────────────────────────────────────────
# SCD3 — Current + previous value per tracked column
# ─────────────────────────────────────────────────────────────────────────────

def _scd3(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    tracked_cols: Optional[List[str]],
    prev_prefix: str,
    logger,
) -> Tuple[DataFrame, str]:
    log = _logger(logger)
    log.info("[SCD3] Column-history merge.")

    non_keys = _non_key_cols(source_df, join_keys or [])
    tracked  = tracked_cols if tracked_cols else non_keys

    if target_df is None or join_keys is None:
        log.info("[SCD3] First load — writing with null previous_ columns.")
        init_df = source_df
        for col in tracked:
            init_df = init_df.withColumn(f"{prev_prefix}{col}", F.lit(None).cast(StringType()))
        return init_df, "overwrite"

    # Target rows with no matching key in source — carry forward untouched
    untouched = target_df.alias("tgt").join(
        source_df.select(join_keys).alias("src"), on=join_keys, how="left_anti"
    )

    # For matching rows: pull old current values to populate previous_
    # Join source onto target to get old values side by side
    joined = source_df.alias("src").join(target_df.alias("tgt"), on=join_keys, how="inner")

    # Build select list: all source columns + previous_ from target current values
    select_cols = [F.col(f"src.{c}").alias(c) for c in source_df.columns]
    for col in tracked:
        if col in target_df.columns:
            select_cols.append(F.col(f"tgt.{col}").cast(StringType()).alias(f"{prev_prefix}{col}"))
        else:
            select_cols.append(F.lit(None).cast(StringType()).alias(f"{prev_prefix}{col}"))

    # Preserve any existing previous_ columns from target that we are not re-tracking
    existing_prev = [
        c for c in target_df.columns
        if c.startswith(prev_prefix) and c not in [f"{prev_prefix}{t}" for t in tracked]
    ]
    for col in existing_prev:
        select_cols.append(F.col(f"tgt.{col}").alias(col))

    updated = joined.select(select_cols)

    # New rows — null previous_ columns
    new_rows = source_df.alias("src").join(
        target_df.select(join_keys).alias("tgt"), on=join_keys, how="left_anti"
    )
    for col in tracked:
        new_rows = new_rows.withColumn(f"{prev_prefix}{col}", F.lit(None).cast(StringType()))

    merged = (
        untouched
        .unionByName(updated,  allowMissingColumns=True)
        .unionByName(new_rows, allowMissingColumns=True)
    )
    log.info("[SCD3] Done.")
    return merged, "overwrite"


# ─────────────────────────────────────────────────────────────────────────────
# SCD4 — Main table = current state; {target}_history = all versions
# ─────────────────────────────────────────────────────────────────────────────

def _scd4(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    history_table: str,
    ts_col: str,
    logger,
) -> Tuple[DataFrame, str, list]:
    """
    Returns (main_df, main_write_mode, extra_writes).
    extra_writes = [(history_df, history_table_name, write_mode)]
    """
    log = _logger(logger)
    log.info(f"[SCD4] History-table merge. History → {history_table}")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if target_df is None or join_keys is None:
        log.info("[SCD4] First load — seeding both main and history tables.")
        hist_df = (
            source_df
            .withColumn(ts_col,     F.lit(now_str).cast(TimestampType()))
            .withColumn(_SCD_ID_COL, _uuid_udf()())
        )
        return source_df, "overwrite", [(hist_df, history_table, "overwrite")]

    non_keys = _non_key_cols(source_df, join_keys, [ts_col, _SCD_ID_COL])

    joined      = source_df.alias("src").join(target_df.alias("tgt"), on=join_keys, how="left")
    changed_src = joined.filter(
        F.col(f"tgt.{join_keys[0]}").isNotNull() & _changed_condition(non_keys)
    ).select([F.col(f"src.{c}") for c in source_df.columns])

    new_src = source_df.alias("src").join(
        target_df.select(join_keys).alias("tgt"), on=join_keys, how="left_anti"
    )

    # Main table: SCD1 upsert (only current state, no history)
    untouched = target_df.alias("tgt").join(
        source_df.select(join_keys).alias("src"), on=join_keys, how="left_anti"
    )
    main_df = (
        untouched
        .unionByName(changed_src, allowMissingColumns=True)
        .unionByName(new_src,     allowMissingColumns=True)
    )

    # History: append changed + new rows stamped with timestamp + scd_id
    to_history = (
        changed_src.unionByName(new_src, allowMissingColumns=True)
        .withColumn(ts_col,      F.lit(now_str).cast(TimestampType()))
        .withColumn(_SCD_ID_COL, _uuid_udf()())
    )

    log.info("[SCD4] Done.")
    return main_df, "overwrite", [(to_history, history_table, "append")]


# ─────────────────────────────────────────────────────────────────────────────
# SCD6 — Hybrid: SCD2 rows + SCD1 current_ backfill + SCD3 previous_ column
# ─────────────────────────────────────────────────────────────────────────────

def _scd6(
    source_df: DataFrame,
    target_df: Optional[DataFrame],
    join_keys: Optional[List[str]],
    eff_col: str, end_col: str, is_cur_col: str,
    tracked_cols: Optional[List[str]],
    prev_prefix: str, cur_prefix: str,
    logger,
) -> Tuple[DataFrame, str]:
    log = _logger(logger)
    log.info("[SCD6] Hybrid (SCD1+2+3) merge.")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    reserved = [_SCD_ID_COL, eff_col, end_col, is_cur_col]
    non_keys = _non_key_cols(source_df, join_keys or [], reserved)
    tracked  = tracked_cols if tracked_cols else non_keys

    if target_df is None or join_keys is None:
        log.info("[SCD6] First load.")
        init_df = source_df
        for col in tracked:
            init_df = (
                init_df
                .withColumn(f"{cur_prefix}{col}",  F.col(col).cast(StringType()))
                .withColumn(f"{prev_prefix}{col}", F.lit(None).cast(StringType()))
            )
        return _add_scd2_cols(init_df, eff_col, end_col, is_cur_col, now_str, True), "overwrite"

    active_tgt = target_df.filter(F.col(is_cur_col) == True)
    hist_tgt   = target_df.filter(F.col(is_cur_col) == False)

    # Detect changes against active rows only
    joined      = source_df.alias("src").join(active_tgt.alias("tgt"), on=join_keys, how="left")
    changed_src = joined.filter(
        F.col(f"tgt.{join_keys[0]}").isNotNull() & _changed_condition(tracked)
    ).select([F.col(f"src.{c}") for c in source_df.columns])

    new_src = source_df.alias("src").join(
        active_tgt.select(join_keys).alias("tgt"), on=join_keys, how="left_anti"
    )

    changed_keys = changed_src.select(join_keys).distinct()

    # ── Type1 backfill helper: update current_ cols on any row set ───────────
    def backfill_current(rows_df: DataFrame) -> DataFrame:
        """Join latest source values for changed keys onto rows_df → update current_."""
        src_cur = changed_src.select(
            join_keys + [F.col(c).cast(StringType()).alias(f"_nc_{c}") for c in tracked]
        )
        out = rows_df.join(src_cur, on=join_keys, how="left")
        for col in tracked:
            cur_col_name = f"{cur_prefix}{col}"
            out = out.withColumn(
                cur_col_name,
                F.coalesce(F.col(f"_nc_{col}"),
                           F.col(cur_col_name).cast(StringType()) if cur_col_name in rows_df.columns
                           else F.lit(None).cast(StringType()))
            ).drop(f"_nc_{col}")
        return out

    # Historical rows for changed keys — backfill current_
    hist_for_changed = (
        hist_tgt.alias("h")
        .join(changed_keys.alias("c"), on=join_keys, how="inner")
        .select([F.col(f"h.{col}") for col in hist_tgt.columns])
    )
    hist_for_changed   = backfill_current(hist_for_changed)
    hist_untouched     = hist_tgt.alias("h").join(changed_keys.alias("c"), on=join_keys, how="left_anti")

    # Expire changed active rows + backfill current_
    expired = (
        active_tgt.alias("tgt")
        .join(changed_keys.alias("chg"), on=join_keys, how="inner")
        .select([F.col(f"tgt.{c}") for c in active_tgt.columns])
        .withColumn(end_col,    F.lit(now_str).cast(TimestampType()))
        .withColumn(is_cur_col, F.lit(False))
    )
    expired = backfill_current(expired)

    # Unchanged active rows — carry forward
    unchanged_active = active_tgt.alias("tgt").join(
        changed_keys.alias("chg"), on=join_keys, how="left_anti"
    )

    # New active rows: current_ = source value; previous_ = last known current_ from active target
    prev_lookup = active_tgt.select(
        join_keys +
        [F.col(f"{cur_prefix}{c}").cast(StringType()).alias(f"_prev_{c}")
         for c in tracked if f"{cur_prefix}{c}" in active_tgt.columns]
    )

    to_insert = changed_src.unionByName(new_src, allowMissingColumns=True)
    to_insert = to_insert.join(prev_lookup, on=join_keys, how="left")

    for col in tracked:
        to_insert = to_insert.withColumn(f"{cur_prefix}{col}", F.col(col).cast(StringType()))
        prev_src = f"_prev_{col}"
        to_insert = to_insert.withColumn(
            f"{prev_prefix}{col}",
            F.col(prev_src) if prev_src in to_insert.columns else F.lit(None).cast(StringType())
        )
        if prev_src in to_insert.columns:
            to_insert = to_insert.drop(prev_src)

    new_active = _add_scd2_cols(to_insert, eff_col, end_col, is_cur_col, now_str, True)

    merged = (
        hist_untouched
        .unionByName(hist_for_changed, allowMissingColumns=True)
        .unionByName(expired,          allowMissingColumns=True)
        .unionByName(unchanged_active, allowMissingColumns=True)
        .unionByName(new_active,       allowMissingColumns=True)
    )
    log.info("[SCD6] Done.")
    return merged, "overwrite"


# ─────────────────────────────────────────────────────────────────────────────
# Public entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def apply_scd(
    scd_type: SCDType,
    source_df: DataFrame,
    spark_session: SparkSession,
    engine: Engine,
    target_table: str,
    con_string: str,
    driver: str,
    schema_name: str = "public",
    # SCD2 / SCD6
    effective_date_col: str           = "effective_start_date",
    end_date_col: str                 = "effective_end_date",
    is_current_col: str               = "is_current",
    # SCD3 / SCD6
    tracked_cols: Optional[List[str]] = None,
    previous_prefix: str              = "previous_",
    current_prefix: str               = "current_",
    # SCD4
    change_timestamp_col: str         = "change_timestamp",
    logger                            = None,
) -> Tuple[DataFrame, str, list]:
    """
    Run SCD merge entirely in Spark and return the result for the caller to write.

    Returns
    -------
    merged_df    : Final Spark DataFrame — write this to target_table.
    write_mode   : "overwrite" — pass to spark_class.write_via_spark().
    extra_writes : List of (df, table_name, mode) for additional tables
                   (only SCD4 history). Empty list for all other types.

    Parameters
    ----------
    scd_type             : SCDType enum value (SCD0 … SCD6).
    source_df            : Incoming Spark DataFrame from the pipeline.
    spark_session        : Active SparkSession.
    engine               : SQLAlchemy Engine — used only for PK inspection.
    target_table         : Target table name (no schema prefix).
    con_string           : JDBC connection string for reading the target.
    driver               : JDBC driver class string.
    schema_name          : DB schema. Default "public".
    effective_date_col   : [SCD2/6] Row-validity start column.
    end_date_col         : [SCD2/6] Row-validity end column.
    is_current_col       : [SCD2/6] Active-row boolean flag.
    tracked_cols         : [SCD3/6] Columns to snapshot with previous_ values.
                           None → all non-key, non-metadata columns.
    previous_prefix      : [SCD3/6] Prefix for previous-value columns.
    current_prefix       : [SCD6]   Prefix for current-value columns.
    change_timestamp_col : [SCD4]   Timestamp added to history rows.
    logger               : Optional logger; falls back to module logger.

    Raises
    ------
    ValueError           : Missing join keys in source DF.
    NotImplementedError  : Unsupported SCDType.
    """
    log = _logger(logger)

    # ── 1. Auto-detect join keys from target table PKs ────────────────────────
    join_keys = _get_join_keys(engine, target_table, schema_name, log)
    if join_keys:
        missing = [k for k in join_keys if k not in source_df.columns]
        if missing:
            raise ValueError(
                f"[SCD] Primary key column(s) {missing} are not in the source DataFrame. "
                f"Available columns: {source_df.columns}"
            )

    # ── 2. Read existing target via Spark JDBC ────────────────────────────────
    target_df = _read_target_spark(spark_session, con_string, driver, target_table, schema_name)
    if target_df is not None:
        log.info(f"[SCD] Read existing target — {target_df.count()} rows.")
    else:
        log.info("[SCD] No existing target data — first load.")

    # ── 3. Delegate to SCD type implementation ────────────────────────────────
    log.info(f"[SCD] {scd_type.code.upper()} — {scd_type.description}")
    log.info(f"[SCD] Steps: {scd_type.steps}")

    extra_writes = []

    if scd_type == SCDType.SCD0:
        merged_df, write_mode = _scd0(source_df, target_df, join_keys, log)

    elif scd_type == SCDType.SCD1:
        merged_df, write_mode = _scd1(source_df, target_df, join_keys, log)

    elif scd_type == SCDType.SCD2:
        merged_df, write_mode = _scd2(
            source_df, target_df, join_keys,
            effective_date_col, end_date_col, is_current_col, log
        )

    elif scd_type == SCDType.SCD3:
        merged_df, write_mode = _scd3(
            source_df, target_df, join_keys,
            tracked_cols, previous_prefix, log
        )

    elif scd_type == SCDType.SCD4:
        history_table = f"{target_table}_history"
        merged_df, write_mode, extra_writes = _scd4(
            source_df, target_df, join_keys,
            history_table, change_timestamp_col, log
        )

    elif scd_type == SCDType.SCD6:
        merged_df, write_mode = _scd6(
            source_df, target_df, join_keys,
            effective_date_col, end_date_col, is_current_col,
            tracked_cols, previous_prefix, current_prefix, log
        )

    else:
        raise NotImplementedError(f"[SCD] SCDType '{scd_type}' is not implemented.")

    return merged_df, write_mode, extra_writes