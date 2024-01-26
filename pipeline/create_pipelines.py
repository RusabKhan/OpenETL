import extra_streamlit_components as stx
import streamlit as st
from utils.local_connection_utils import read_connection_configs, read_config, store_pipeline_config
from utils.generic_utils import extract_connections_db_or_api, fetch_metadata, set_page_config, check_missing_values
from utils.schema_utils import get_datatypes_and_default_values
from utils.sqlalchemy_engine_utils import SQLAlchemyEngine
import pandas as pd
import json
from datetime import date

set_page_config(page_title="Create Pipeline", page_icon=None,
                initial_sidebar_state="expanded", layout="wide", menu_items={})

tab_items = [
    stx.TabBarItemData(id=1, title="Connections",
                       description="Select Source & Target"),
    stx.TabBarItemData(id=2, title="Compute", description="Spark Settings"),
    stx.TabBarItemData(id=3, title="Schedule", description="Finish"),
]

val = stx.tab_bar(
    data=tab_items, default=st.session_state.pipeline_tab_val, return_type=int)
# (steps=["Select Source & Target", "Spark Settings", "Finish"])
source_type = "Database"
con_type = ["Database", "API"]

configs = read_connection_configs()


spark_config = {}
hadoop_config = {}

disable_dates = True
disable_frequency = False

integration_name = ""
schedule_time = ""
frequencey = ""
schedule_date = ""
no_source = False

source_int_schema =0


slide_col1, slide_col2 = st.columns([4, 1])


with slide_col2:
    sub_col1, sub_col2 = st.columns(2, gap="small")
    with sub_col1:
        if st.button("Back") and int(val) > 1:
            st.session_state.pipeline_tab_val = val-1
            st.experimental_rerun()
    with sub_col2:
        if st.button("Next") and int(val) < len(tab_items):
            st.session_state.pipeline_tab_val = val+1
            st.experimental_rerun()


def spark_work(spark_config, hadoop_config, integration_name, is_frequency, selected_dates, schedule_time, schedule_dates, frequency, mapping, target_table, source_table, target_schema, source_schema):
    """
    @MeSSAGE FOR RAJAL NAQVI
    yeh method 1 alag file m rkh kar utils m spark utils ki waha use krna h. isy dagsster se schedule kia jaega 1 method nh
    hoga apko demo deny k liye likha h bs. frequency p dates nh hnge current date k hisab se calculate hojaige like
    weekly m aj ki date se agly hafty p chlega monthly m aj k 30 ddays bdh etc.
    """

    print(spark_config, hadoop_config, integration_name, is_frequency,
          selected_dates, schedule_time, schedule_dates, frequency, mapping)
    print("WIP")
    mapping_df = get_datatypes_and_default_values(mapping)
    print(mapping_df)


if val == 1:
    source = ""
    source_div = st.expander("Source", expanded=True)
    with source_div:
        source_schema = ""
        source_tables = ""

        options = []
        subcol1, subcol2 = st.columns([3, 1])
        with subcol2:
            source_type = st.radio(
                "Source Type", con_type, index=st.session_state.source_type_index)
            st.session_state.source_type_index = con_type.index(source_type)
            options = extract_connections_db_or_api(source_type, configs)
        with subcol1:
            source = st.selectbox("Source", options=options,
                                  index=st.session_state.source_selected_index)
            st.session_state.source_selected_index = options.index(
                source) if source is not None else 0

        table_col, schema_col = st.columns([2, 3])
        metadata = fetch_metadata(source)
        source_schema = metadata['schema']
        no_source = True if source_schema is not None else False
        source_tables = metadata['tables']

        with table_col:
            source_int_schema = st.selectbox(
                "Source Schema", source_schema, index=st.session_state.source_selected_schema_index,disabled=no_source)
            if source_int_schema is not None:
                st.session_state.source_selected_schema_index = source_schema.index(
                    source_int_schema) 
                st.session_state.source_selected_schema = source_int_schema
        with schema_col:
            if source_int_schema is not None:
                if len(source_tables[st.session_state.source_selected_schema_index]) < st.session_state.source_selected_table_index:
                    st.session_state.source_selected_table_index = 0
                source_int_tables = st.selectbox(
                    "Source Table", source_tables[st.session_state.source_selected_schema_index], index=st.session_state.source_selected_table_index)
                st.session_state.source_selected_table_index = source_tables[st.session_state.source_selected_schema_index].index(
                    source_int_tables)
                st.session_state.source_selected_tables = source_int_tables

    target_div = st.expander("Target")
    with target_div:
        target_schema = ""
        target_tables = ""

        options = []
        subcol1, subcol2 = st.columns([3, 1])
        with subcol2:
            target_type = st.radio(
                "Target Type", con_type, index=st.session_state.target_type_index)
            st.session_state.target_type_index = con_type.index(target_type)
            options = extract_connections_db_or_api(target_type, configs)
        with subcol1:
            target = st.selectbox("Target", options=options,
                                  index=st.session_state.target_selected_index)
            st.session_state.target_selected_index = options.index(
                target) if target is not None else 0

        table_col, schema_col = st.columns([2, 3])
        metadata = fetch_metadata(target)
        target_schema = metadata['schema']
        target_tables = metadata['tables']

        with table_col:
            target_int_schema = st.selectbox(
                "Target Schema", target_schema, index=st.session_state.target_selected_schema_index)
            st.session_state.target_selected_schema_index = target_schema.index(
                target_int_schema)
            st.session_state.target_selected_schema = target_int_schema
        with schema_col:
            target_int_tables = st.selectbox(
                "Target Table", target_tables[st.session_state.target_selected_schema_index], index=st.session_state.target_selected_table_index)
            st.session_state.target_selected_table_index = target_tables[st.session_state.target_selected_schema_index].index(
                target_int_tables)
            st.session_state.target_selected_tables = target_int_tables


elif val == 2:

    _config_spark = ""
    _config_hadoop = ""

    spark_col, hadoop_col = st.columns(2)

    with spark_col:
        data = {
            'Configuration': [
                'spark.driver.memory',
                'spark.executor.memory',
                'spark.executor.cores',
                'spark.executor.instances',

            ],
            'Average Setting': [
                '2g',
                '2g',
                '2',
                '2',
            ]
        }

        spark_col.header("Enter Spark Configuration")
        df = pd.DataFrame(data)
        _config_spark = st.experimental_data_editor(
            df, num_rows="dynamic", key="spark_config")
        spark_config = _config_spark.set_index(
            'Configuration')['Average Setting'].to_dict()

    with hadoop_col:
        data = {
            'Configuration': [
                'spark.hadoop.fs.s3a.access.key',
                'spark.hadoop.fs.s3a.secret.key',
                'spark.hadoop.fs.s3a.endpoint',
                'spark.hadoop.fs.s3a.impl',
            ],
            'Average Setting': [
                None,
                None,
                None,
                None
            ]
        }
        df = pd.DataFrame(data)

        hadoop_col.header("Enter Hadoop Configuration")
        _config_hadoop = st.experimental_data_editor(df, num_rows="dynamic")
        hadoop_config = _config_hadoop.set_index(
            'Configuration')['Average Setting'].to_dict()

    mapping = st.text_input(
        label="Mapping", value="https://docs.google.com/spreadsheets/d/1576toIMaiKuFWShf-lzHMY6JYGEz-Ke3dGjYqa6n0sc/")
    disregard_spark_config = all(
        value is None for value in spark_config.values())
    disregard_hadoop_config = all(
        value is None for value in hadoop_config.values())

    st.session_state.integration_mapping_config = mapping
    st.session_state.integration_spark_config = spark_config if disregard_spark_config is False else {}
    st.session_state.integration_hadoop_config = hadoop_config if disregard_hadoop_config is False else {}

if val == 3:

    submit = False
    integration_name = st.text_input("Enter unique integration name")
    col1, col2 = st.columns(2)
    options = []

    with col1:
        schedule_type = st.radio("Select Schedule Type", [
                                 "Frequency", "Selected Dates"])
        if schedule_type == "Selected Dates":
            disable_dates = False
            disable_frequency = True

        frequencey = st.selectbox("Select frequency", [
                                  "Weekly", "Monthly", "Daily", "Weekends", "Weekday"], disabled=disable_frequency)

    with col2:
        schedule_date = st.date_input("Schedule dates", disabled=disable_dates)
        schedule_time = st.time_input("Schedule time")
        if schedule_date not in st.session_state.integration_selected_dates:
            st.session_state.integration_selected_dates.append(schedule_date)

    selected_dates = st.multiselect("Selected Dates", options=st.session_state.integration_selected_dates,
                                    default=st.session_state.integration_selected_dates, disabled=disable_dates)

    gap, button_col = st.columns([4, 1])

    with button_col:
        submit = st.button("Create Integration")

    if submit:

        formatted_dates = [date.strftime('%Y-%m-%d')
                           for date in selected_dates]

        miss = check_missing_values(**{
            'spark_config': st.session_state.integration_spark_config,
            'hadoop_config': st.session_state.integration_hadoop_config,
            'integration_name': integration_name,
            'is_frequency': disable_frequency,
            'selected_dates': formatted_dates,
            'schedule_time': schedule_time.strftime('%H:%M:%S'),
            'frequency': frequencey,
            'schedule_dates': schedule_date.strftime('%Y-%m-%d'),
            "run_details": {},
            "mapping": st.session_state.integration_mapping_config,
            "target_table": st.session_state.target_selected_tables,
            "source_table": st.session_state.source_selected_tables,
            "target_schema": st.session_state.target_selected_schema,
            "source_table": st.session_state.source_selected_schema
        })

        if miss[0]:
            st.error("Missing value for: "+miss[1])
            st.stop()

        pipeline_json = {
            'spark_config': st.session_state.integration_spark_config,
            'hadoop_config': st.session_state.integration_hadoop_config,
            'integration_name': integration_name,
            'is_frequency': disable_frequency,
            'selected_dates': formatted_dates,
            'schedule_time': schedule_time.strftime('%H:%M:%S'),
            'frequency': frequencey,
            'schedule_dates': schedule_date.strftime('%Y-%m-%d'),
            "run_details": {f"{date.today()}":{"rows_read": 0, "rows_write": 0, "start_time": "00:00:00", "end_time": "00:00:00","status":"Not Started"}},
            "mapping": st.session_state.integration_mapping_config,
            "target_table": st.session_state.target_selected_tables,
            "source_table": st.session_state.source_selected_tables,
            "target_schema": st.session_state.target_selected_schema,
            "source_schema": st.session_state.source_selected_schema
        }
        stored = store_pipeline_config(pipeline_json)
        if not stored[0]:
            st.error(stored[1])
        else:
            st.success("Integration Created Successfully")
            spark_work(**stored[1])
