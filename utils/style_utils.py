import streamlit as st


def load_css(filename="css/style.css",pagename="Haku"):
    try:
        with open(filename) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        st.experimental_rerun()
            
