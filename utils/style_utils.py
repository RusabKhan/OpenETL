import streamlit as st


def load_css(filename="css/style.css",pagename="Haku"):
    with open(filename) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
            
