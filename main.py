from pydrive.auth import GoogleAuth
import requests
from io import BytesIO
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery
import streamlit as st


# # 1. Download the XLSX data.
# file_id = "13VbBxnNTMnqNXoefB5ASs3TYAnm5mxDQ"  # <--- Please set the file ID of XLSX file.
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media"
# res = requests.get(url, headers={"Authorization": "Bearer " + gauth.attr['credentials'].access_token})
#
# # 2. The downloaded XLSX data is read with `pd.read_excel`.
# sheet = "TDSheet"

def link_to_id():
    st.session_state["spreadsheet_id"] = st.session_state["link"]

if "spreadsheet_id" not in st.session_state:
    st.session_state["spreadsheet_id"] = '1O0qVHr2vkTjpGDyOao1gT1ULPDDYbYCjj0mC8fhnVVA'
if "link" not in st.session_state:
    st.session_state["link"] = ""

CREDENTIALS_FILE = "cred_service.json"

tab1, tab2, tab3 = st.tabs(["Загрузка морс", "Загрузка статусов", "Загрузка еще чего-нибудь"])
if st.session_state["link"] == "":
    st.sidebar.write("Текущая ссылка на файл spreadsheet: " + "https://docs.google.com/spreadsheets/d/" + st.session_state["spreadsheet_id"])
else:
    st.sidebar.write("Текущая ссылка на файл spreadsheet: " + "https://docs.googlei.com/spreadsheets/d/" + st.session_state["link"])

with tab1:

    uploaded_mors = st.file_uploader("Загрузите морс")

    col2, col3 = st.columns([3, 1])
    with col2:
        st.text_input(
            "Путь к гугл файлу: ", value="",
            max_chars=None, key="link", type="default", autocomplete=None, on_change=None,
            args=None, kwargs=None, placeholder="при необходимости введите новый  гугл ID spreadsheet", disabled=False,
            label_visibility="collapsed")
    with col3:
        st.button("Обновить", on_click=link_to_id)
    st.write("* при добавлении ID нового файла, заблаговременно откройте к нему доступ для служебного аккаунта: "
             "account@databasealpha.iam.gserviceaccount.com")
    if uploaded_mors:

        df = pd.read_excel(uploaded_mors)
        df.columns = df.iloc[7] # название столбцов
        df = df.dropna(axis=1, how='all')  # дроп пустых
        df = df.drop(df.index[0:8])  # дроп первых 8
        except_list = np.append(df["Объекты строительства"].unique()[1:], ["Итого",
                                                                           "Недостаточно прав для детализации"])  # список исключения для рядов (итого, назв об, недосткаточно)
        df = df[~df['№ заявки на оплату'].isin(except_list)]  # дроп списка
        df.drop(df.tail(3).index, inplace=True)  # дроп хвост
        df = df.dropna(axis=1, how='all') # сброс нулевых
        df = df.iloc[:, :-26]  # дроп правых столбцов
        df = df.reset_index() # сброс индексов
        df.index = df.index + 1 # нумерация индексов
        df = df.drop(["index"], axis=1) # нумерация индексов
        df = df.fillna("")

        try:
            st.write("ссылка"+st.session_state["spreadsheet_id"])
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive'])
            httpAuth = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

            response_date = service.spreadsheets().values().update(
                spreadsheetId=st.session_state["spreadsheet_id"],
                range='A1:EE',
                valueInputOption='RAW',
                body=dict(
                    majorDimension='ROWS',
                    values=df.values.tolist()[:])
            ).execute()
            st.write("файл обновлен по ссылке: " + "https://docs.google.com/spreadsheets/d/" + st.session_state["spreadsheet_id"])
        except:
            st.write("Неудача!!! попробуй поменять ID таблицы или открыть доступ к ней служебному аккаунту account@databasealpha.iam.gserviceaccount.com")
    else:
        st.write("")

