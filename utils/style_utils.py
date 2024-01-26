import streamlit as st


def load_css(filename="css/style.css",pagename="Haku"):
    with open(filename) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
            
    # st.set_page_config(page_title=pagename, page_icon=None,initial_sidebar_state="expanded", layout="wide", menu_items={
    #     'Get Help': 'https://www.extremelycoolapp.com/help',
    #     'Report a bug': "https://www.extremelycoolapp.com/bug",
    #     'About': "# This is a header. This is an *extremely* cool app!"
    # }
    # )