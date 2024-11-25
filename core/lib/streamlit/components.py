import time

import streamlit as st
from streamlit.components.v1 import html as html_st


def run_js_script(js_script: str) -> None:
    SLEEP_TIME = 0.5
    temp = st.empty()
    with temp:
        html_st(js_script, height=0)
        time.sleep(SLEEP_TIME)

    temp.empty()
