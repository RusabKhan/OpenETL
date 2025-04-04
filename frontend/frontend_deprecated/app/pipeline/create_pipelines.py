import streamlit as st

from utils.deprecated.api_utils import send_request
from utils.enums import *
import pandas as pd

# Initialize values
final_values = {
    "Source": {
        "connection_type": "",
        "source": "",
        "schema": "",
        "table": ""
    },
    "Target": {
        "connection_type": "",
        "source": "",
        "schema": "",
        "table": ""
    }
}

target_type = ConnectionType.DATABASE.value
con_type = [
    ConnectionType.DATABASE.value,
    ConnectionType.API.value]

database_configs = send_request('connector/get_created_connections',
                                method=APIMethod.POST,
                                timeout=10,
                                json={"connector_type": ConnectionType.DATABASE.value, "connector_name": None})

api_configs = send_request('connector/get_created_connections',
                                method=APIMethod.POST,
                                timeout=10,
                                json={"connector_type": ConnectionType.API.value, "connector_name": None})

database_configs_names = []
api_configs_names = []

for config in database_configs:
    database_configs_names.append(config["connection_name"])
for config in api_configs:
    api_configs_names.append(config["connection_name"])

source_target, spark, finish = st.tabs(["Select Source & Target", "Spark Config", "Finish"])

spark_config = {}
hadoop_config = {}

disable_dates = True
disable_frequency = False

integration_name = ""
schedule_time = ""
frequencey = ""
schedule_date = ""
no_source = False

schedule_dates = []

slide_col1, slide_col2 = st.columns([4, 1])



def render_section(section):
    con_type_temp = con_type[:]
    if section.lower() == 'target':
        con_type_temp.remove('api')

    with source_target:
        source_div = st.expander(section, expanded=True)
        with source_div:
            options = []
            subcol1, subcol2 = st.columns([3, 1])
            with subcol2:
                final_values[section]["connection_type"] = st.radio(
                    f"{section} Type", con_type_temp)
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
            req_body = {"connector_name": final_values[section]["source"], "auth_options": auth_options, "connector_type": final_values[section]["connection_type"]}
            connection_name = final_values[section]["source"]
            connection_type = final_values[section]["connection_type"]
            for options in auth_options:
                if options["connection_name"] == connection_name:
                    auth_options = options
                    break

            body = {"connector_name": connection_name, "auth_options": auth_options, "connector_type": connection_type}
            metadata = send_request("connector/fetch_metadata/"
                         , method=APIMethod.POST, timeout=10,
                         json=body)

            #metadata = fetch_metadata(connection_name, auth_options, connection_type)

            source_schema = metadata.keys()
            no_source = False if source_schema else True

            with table_col:
                final_values[section]["connector_type"] = connection_type
                final_values[section]["schema"] = st.selectbox(
                    f"{section} Schema", source_schema, disabled=no_source)

            if final_values[section]["schema"]:
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
    spark_col, hadoop_col = st.columns(2)

    with spark_col:
        data = {
            'Configuration': [
                'spark.driver.memory',
                'spark.executor.memory',
                'spark.executor.cores',
                'spark.executor.instances',
                "spark.app.name",
            ],
            'Average Setting': [
                '1g',
                '1g',
                '1',
                '1',
                f"{final_values['Source']['source']}_to_{final_values['Target']['source']}",
            ]
        }

        spark_col.header("Enter Spark Configuration")
        df = pd.DataFrame(data)
        _config_spark = st.data_editor(df, num_rows="dynamic", key="spark_config")
        spark_config = _config_spark.set_index('Configuration')['Average Setting'].to_dict()

    with hadoop_col:
        data = {
            'Configuration': [],
            'Average Setting': []
        }
        df = pd.DataFrame(data)

        hadoop_col.header("Enter Hadoop Configuration")
        _config_hadoop = st.data_editor(df, num_rows="dynamic")
        hadoop_config = _config_hadoop.set_index('Configuration')['Average Setting'].to_dict()

with finish:
    integration_name_value = final_values["Source"]["source"] + "_" + final_values["Source"]["table"] + "_to_" + final_values["Target"]["source"] + "_" + final_values["Target"]["table"]
    integration_name = st.text_input("Enter unique integration name", key="integration_name", value=integration_name_value)
    col1, col2 = st.columns(2)

    with col1:
        schedule_type = st.radio("Select Schedule Type", ["Frequency", "Selected Dates"])
        if schedule_type == "Selected Dates":
            disable_dates = False
            disable_frequency = True

        frequencey = st.selectbox("Select frequency", ["Weekly", "Monthly", "Daily", "Weekends", "Weekday"], disabled=disable_frequency)
        integration_type = st.radio("Select integration type", IntegrationType.__members__.values())

    with col2:
        schedule_date = st.date_input("Schedule dates", disabled=disable_dates)
        schedule_time = st.time_input("Schedule time")
        if schedule_date not in schedule_dates:
            schedule_dates.append(schedule_date)

    selected_dates = st.multiselect("Selected Dates", options=schedule_dates, default=schedule_dates, disabled=disable_dates)

    gap, button_col = st.columns([4, 1])

    with button_col:
        submit = st.button("Create Integration")
        if submit:
            formatted_dates = [date.strftime('%Y-%m-%d') for date in selected_dates]
            for config in database_configs:
                if config["connection_name"] == final_values["Source"]["source"]:
                    source_connection_id = config["id"]
                if config["connection_name"] == final_values["Target"]["source"]:
                    target_connection_id = config["id"]

            for config in api_configs:
                if config["connection_name"] == final_values["Source"]["source"]:
                    source_connection_id = config["id"]
                if config["connection_name"] == final_values["Target"]["source"]:
                    target_connection_id = config["id"]

            pipeline_dict = {'spark_config': spark_config, 'hadoop_config': hadoop_config,
                             'integration_name': integration_name,
                             'integration_type': integration_type.value,
                             "target_table": final_values["Target"]["table"],
                             "source_table": final_values["Source"]["table"],
                             "target_schema": final_values["Target"]["schema"],
                             "source_schema": final_values["Source"]["schema"],
                             "target_connection": target_connection_id,
                             "source_connection": source_connection_id,
                             "schedule_date": formatted_dates,
                             "schedule_time": schedule_time.strftime('%H:%M:%S'),
                             "frequency": frequencey,
                             }
            if send_request('pipeline/create_integration', method=APIMethod.POST, timeout=10, json=pipeline_dict):
                st.success("Integration Created Successfully")
            else:
                st.error("Failed to create integration")