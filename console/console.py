import logging
import streamlit as st
from datetime import datetime


class StreamlitHandler(logging.Handler):
    def __init__(self):
        super(StreamlitHandler, self).__init__()

    def format(self, record):
        # Customize the log record format here
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} - {record.levelname}: {record.msg}"

    def emit(self, record):
        try:
            new_log = self.format(record) + '\n'
            if 'log_data' not in st.session_state:
                st.session_state.log_data = ""
            st.session_state.log_data += new_log
        except Exception as e:
            self.handleError(record)

    def flush(self):
        pass  # Override the flush method to prevent the handler from flushing

def get_logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = StreamlitHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def download_logs():
    return st.session_state.log_data

logger = get_logger()

st.text_area(label="", value=st.session_state.get('log_data', ""), height=300, max_chars=None, key=None)
st.download_button('Download Logs', data=st.session_state.get('log_data', ""), file_name='logs.txt', mime='text/plain')
