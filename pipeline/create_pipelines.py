import streamlit as st
from utils.local_connection_utils import read_all_connection_configs, read_connection_config
from utils.airflow_utils import create_airflow_dag
from utils.generic_utils import extract_connections_db_or_api, check_missing_values, set_page_config
from utils.enums import *
import pandas as pd
import json
from datetime import date
from utils.connector_utils import get_created_connections, fetch_metadata


set_page_config(page_title="Create ETL", page_icon=None, initial_sidebar_state="expanded",
                layout="wide", menu_items={}, page_style_state_variable="pipeline_create_pipeline")

target_type = ConnectionType.DATABASE.value
con_type = [
    ConnectionType.DATABASE.value,
    ConnectionType.API.value]

database_configs = get_created_connections(ConnectionType.DATABASE.value)
api_configs = get_created_connections(ConnectionType.API.value)


database_configs_names = [config["connection_name"]
                          for config in database_configs]
api_configs_names = [config["connection_name"] for config in api_configs]

source_target, spark, finish = st.tabs(
    ["Select Source & Target", "Spark Config", "Finish"])

val = 1

spark_config = {}
hadoop_config = {}

disable_dates = True
disable_frequency = False

integration_name = ""
schedule_time = ""
frequencey = ""
schedule_date = ""
no_source = False

schema = 0

schedule_dates = []

slide_col1, slide_col2 = st.columns([4, 1])

final_values = {}


def render_section(section):

    con_type.remove('api') if section.lower() == 'target' else None
    final_values[section] = {}
    with source_target:
        source = ""
        source_div = st.expander(section, expanded=True)
        with source_div:
            source_schema = ""
            source_tables = ""

            options = []
            subcol1, subcol2 = st.columns([3, 1])
            with subcol2:
                final_values[section]["connection_type"] = st.radio(
                    f"{section} Type", con_type)
                if final_values[section]["connection_type"] == ConnectionType.DATABASE.value:
                    options = database_configs_names
                    auth_options = database_configs

                elif final_values[section]["connection_type"] == ConnectionType.API.value:
                    options = api_configs_names
                    auth_options = api_configs

            with subcol1:
                final_values[section]["source"] = st.selectbox(
                    label=section, options=options)

            table_col, schema_col = st.columns([2, 3])
            metadata = fetch_metadata(
                final_values[section]["source"], auth_options, final_values[section]["connection_type"])
            source_schema = metadata.keys()
            no_source = False if source_schema is not None else True

            with table_col:
                final_values[section]["schema"] = st.selectbox(
                    f"{section} Schema", source_schema, disabled=no_source)
            if final_values[section]["schema"] is not None:
                with schema_col:
                    if section == "Source":
                        final_values[section]["table"] = st.selectbox(
                            f"{section} Tables", metadata[final_values[section]["schema"]], disabled=no_source)
                    else:
                        new_or_existing = st.radio(
                            f"{section} Tables", ["New", "Existing"])
                        if new_or_existing == "Existing":
                            final_values[section]["table"] = st.selectbox(
                                f"{section} Tables", metadata[final_values[section]["schema"]], disabled=no_source)
                        else:
                            final_values[section]["table"] = st.text_input(
                                f"{section} Tables", disabled=no_source)


render_section("Source")
render_section("Target")

with spark:

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
                "spark.master",
                "spark.app.name",

            ],
            'Average Setting': [
                '1g',
                '1g',
                '1',
                '1',
                "local[*]",
                f"{final_values['Source']['source']}_to_{final_values['Target']['source']}",
            ]
        }

        spark_col.header("Enter Spark Configuration")
        df = pd.DataFrame(data)
        _config_spark = st.data_editor(
            df, num_rows="dynamic", key="spark_config")
        spark_config = _config_spark.set_index(
            'Configuration')['Average Setting'].to_dict()

    with hadoop_col:
        data = {
            'Configuration': [
            ],
            'Average Setting': [
            ]
        }
        df = pd.DataFrame(data)

        hadoop_col.header("Enter Hadoop Configuration")
        _config_hadoop = st.data_editor(df, num_rows="dynamic")
        hadoop_config = _config_hadoop.set_index(
            'Configuration')['Average Setting'].to_dict()


with finish:

    submit = False
    integration_name_value =final_values["Source"]["source"]+"_" +final_values["Source"]["table"] + "_to_" + final_values["Target"]["source"]+"_"+final_values["Target"]["table"]
    integration_name = st.text_input("Enter unique integration name",
                                     key="integration_name",
                                     value=integration_name_value)
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
        if schedule_date not in schedule_dates:
            schedule_dates.append(schedule_date)

    selected_dates = st.multiselect("Selected Dates", options=schedule_dates,
                                    default=schedule_dates, disabled=disable_dates)

    gap, button_col = st.columns([4, 1])

    with button_col:
        submit = st.button("Create Integration")
        if submit:

            formatted_dates = [date.strftime('%Y-%m-%d')
                               for date in selected_dates]

            pipeline_dict = {
                'spark_config': spark_config,
                'hadoop_config': hadoop_config,
                'integration_name': integration_name,
                'is_frequency': disable_frequency,
                'selected_dates': formatted_dates,
                'schedule_time': schedule_time.strftime('%H:%M:%S'),
                'frequency': frequencey,
                'schedule_dates': schedule_date.strftime('%Y-%m-%d'),
                "run_details": {f"{date.today()}": {"rows_read": 0, "rows_write": 0, "start_time": "00:00:00", "end_time": "00:00:00", "status": "Not Started"}},
                "target_table": final_values["Target"]["table"],
                "source_table": final_values["Source"]["table"],
                "target_schema": final_values["Target"]["schema"],
                "source_schema": final_values["Source"]["schema"],
                "target_connection_name": final_values["Target"]["source"],
                "source_connection_name": final_values["Source"]["source"],
                "target_type": final_values["Target"]["connection_type"],
                "source_type": final_values["Source"]["connection_type"]
            }

            miss = check_missing_values(**pipeline_dict)

            if miss[0]:
                st.error("Missing value for: "+miss[1])
                st.stop()

            stored = create_airflow_dag(pipeline_dict)
            if not stored:
                st.error("Unable to create integration. Please try again.")
            else:
                st.success("Integration Created Successfully")
                # spark_work(**stored[1])
