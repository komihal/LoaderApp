# from pydrive.auth import GoogleAuth
# import requests
# from io import BytesIO
# import pandas as pd
# import numpy as np
# from oauth2client.service_account import ServiceAccountCredentials
# import httplib2
# import apiclient.discovery
import streamlit as st

col2, col3 = st.columns([3,1])

with col2:
    st.text_input(
        "Путь к гугл файлу: ", value="",
        max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None,
        args=None, kwargs=None, placeholder="введите ID гугл spreadsheet", disabled=False, label_visibility="collapsed")
with col3:
    st.button("Обновить")

if st.button:
    st.session_state["spreadsheet_id"] = st.text_input
