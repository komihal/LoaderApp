import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import apiclient.discovery
import streamlit as st
import time


def link_to_id():
    st.session_state["spreadsheet_id"] = st.session_state["link"]
    st.sidebar.success("ссылка обновлена на: " + "https://docs.google.com/spreadsheets/d/" + st.session_state[
        "spreadsheet_id"], icon="✅")

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
    
    uploaded_mors = st.file_uploader("Загрузка начнется после перетаскивания файла в бокс ⬇⬇⬇:")

    col2, col3 = st.columns([3, 1])
    with col2:
        st.text_input(
            "Путь к гугл файлу: ", value="",
            max_chars=None, key="link", type="default", autocomplete=None, on_change=None,
            args=None, kwargs=None, placeholder="при необходимости введите новый  гугл ID spreadsheet", disabled=False,
            label_visibility="collapsed")
    with col3:
        st.button("Обновить", on_click=link_to_id)
    st.info("* при добавлении ID новой гугл-таблицы, откройте к ней доступ для служебного аккаунта: "
             "account@databasealpha.iam.gserviceaccount.com , иначе загрузка не выполнится!")
    if uploaded_mors:
        df = pd.read_excel(uploaded_mors)
        mors = df
        # находим в верхней строке морс и оброезаем документ +6 строками
        column_number = mors.columns.get_loc('МОРС')
        mors = mors.iloc[:, :column_number + 6]

        # задаём значения столбцов
        mors.columns = mors.iloc[0]
        mors = mors[1:]
        base = mors

        mors = mors.astype({
        'Сумма': 'float',
        'За период': 'float', 
        'На конец периода': 'float', 
        'Сумма нач. ост.': 'float', 
        'Сумма приход': 'float',
        'Сумма расход': 'float', 
        })

        # Находим индексы интересующих колонок
        start_col_index = mors.columns.get_loc("Банковский счет строка")
        end_col_index = mors.columns.get_loc("Сумма")

        # Инициализируем переменную для хранения текущего значения
        current_value = np.nan

        # Список индексов для удаления
        rows_to_delete = []
        # Итерация по строкам DataFrame
        for index, row in mors.iterrows():
            # Проверяем, есть ли значение в "Банковский счёт договора" и только NaN в последующих колонках
            if pd.notna(row['Банковский счет строка']) and row.iloc[start_col_index + 1:end_col_index].isna().all():
                # Обновляем текущее значение и отмечаем строку для удаления
                current_value = row['Банковский счет строка']
                rows_to_delete.append(index)
            # Заполняем новую колонку текущим значением
            mors.at[index, 'Объект'] = current_value

        # Удаляем отмеченные строки
        mors.drop(rows_to_delete, inplace=True)

        # # Сбрасываем индекс после удаления строк
        # mors.reset_index(drop=True, inplace=True)

        mors_filled = mors.fillna("")
        # mors_filled = mors_filled.drop(0)

        # Выгрузка отчёта Морс после обработки
        mors_filled.to_excel('edited_mors.xlsx')
        df = mors_filled 

        # Преобразование DataFrame в список значений с индексами
        df.reset_index(inplace=True)
        data_to_send = [df.columns.tolist()] + df.values.tolist()

        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                ['https://www.googleapis.com/auth/spreadsheets',
                 'https://www.googleapis.com/auth/drive'])
            httpAuth = credentials.authorize(httplib2.Http())
            service = apiclient.discovery.build('sheets', 'v4', http=httpAuth)

            response_date = service.spreadsheets().values().update(
                spreadsheetId=st.session_state["spreadsheet_id"],
                range='A1:EE',
                valueInputOption='USER_ENTERED',  # Изменено с RAW на USER_ENTERED
                body=dict(
                    majorDimension='ROWS',
                    values=data_to_send)
            ).execute()
            st.success("файл обновлен по ссылке: " + "https://docs.google.com/spreadsheets/d/" + st.session_state[
                "spreadsheet_id"], icon="✅")
            my_bar = st.progress(0)
        except:
            st.error("Не фартануло! Не верный ID таблицы или доступ служебному аккаунту account@databasealpha.iam.gserviceaccount.com не предоставлен!")
    else:
        st.info("* после загрузки файла дождитесь уведомления.")

