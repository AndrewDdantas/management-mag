import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread as gs
import pandas as pd

st.set_page_config(
    page_title="GERENCIAMENTO",
    page_icon=":chart_with_upwards_trend:",
    layout="wide", 
    initial_sidebar_state="auto",
)

def fmt_num(valor, tipo, casas=0): # Função para formatar números.
    if isinstance(valor,str):
        return ''
    if tipo == 'REAL':
        return "R$ {:,.0f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')
    if tipo == 'CUBAGEM':
        return "{:,.1f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')
    if tipo == 'NORMAL':
        return "{:,.0f}".format(valor).replace(',', 'X').replace('.', ',').replace('X', '.')
    if tipo == "PORCENTAGEM":
        return f"{{:.{casas}%}}".format(valor).replace('.',',')

# Define the scope and authenticate
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = gs.authorize(credentials)

# Open the Google Sheets document
sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1SlnFPqnbVkwEh3Gt56lNxIadE2tfUfQy-KsFn4Xx5l4/edit#gid=1350786165')

# Fetch the 'DB' worksheet and convert it to a DataFrame
db_worksheet = sheet.worksheet('DB')
db_data = db_worksheet.get_all_values()
db = pd.DataFrame(db_data[1:], columns=db_data[0])  # Set the first row as column headers
db['valor_total'] = db['valor_total'].str.replace(',', '.').astype(float)
db['QT_ESTOQUE'] = db['QT_ESTOQUE'].str.replace(',', '.').astype(float)

col1, col2, col3 = st.columns(3)

col1_emp = col1.empty()
col2_emp = col2.empty()
col3_emp = col3.empty()

# Fetch the 'LOG' worksheet and convert it to a DataFrame
log_worksheet = sheet.worksheet('LOG')
log_data = log_worksheet.get_all_values()
log = pd.DataFrame(log_data[1:], columns=log_data[0])  # Set the first row as column headers
log['VALOR'] = log['VALOR'].str.replace(',', '.').astype(float)
log['PRODUTOS'] = log['PRODUTOS'].str.replace(',', '.').astype(float)

emp = st.selectbox('Empresa' ,['Todos'] + db['CD_EMPRESA'].drop_duplicates().values.tolist() )

if emp != 'Todos':
    log = log.loc[log['CD_EMPRESA'] == emp]
    db = db.loc[db['CD_EMPRESA'] == emp]
else:
    log = log
    db = db

total = fmt_num(db['valor_total'].sum(),'REAL')
col1_emp.subheader(f'Custo Total: {total}')

pecas = fmt_num(db['QT_ESTOQUE'].sum(),'NORMAL')
col2_emp.subheader(f'Peças: {pecas}')

sku = fmt_num(db['IT_AJUSTADO'].nunique(),'NORMAL')
col3_emp.subheader(f"Sku's: {sku}")



AGING = log.groupby(['DATA','AGING']).agg({'PRODUTOS':'sum', 'VALOR':'sum'}).sort_values('VALOR', ascending=False).reset_index()
AGING_AJUS = AGING
AGING_AJUS['VALOR'] = AGING_AJUS['VALOR'].apply(fmt_num, tipo='REAL') 
AGING_AJUS['PRODUTOS'] = AGING_AJUS['PRODUTOS'].apply(fmt_num, tipo='NORMAL') 

AREA = log.groupby(['DATA','CD_AREA_ARMAZ']).agg({'PRODUTOS':'sum', 'VALOR':'sum'}).sort_values('VALOR', ascending=False).reset_index()
AREA_AJUS = AREA
AREA_AJUS['VALOR'] = AREA_AJUS['VALOR'].apply(fmt_num, tipo='REAL') 
AREA_AJUS['PRODUTOS'] = AREA_AJUS['PRODUTOS'].apply(fmt_num, tipo='NORMAL') 

EMPRESA = log.groupby(['DATA','CD_EMPRESA']).agg({'PRODUTOS':'sum', 'VALOR':'sum'}).sort_values('VALOR', ascending=False).reset_index()
EMPRESA_AJUS = EMPRESA
EMPRESA_AJUS['VALOR'] = EMPRESA_AJUS['VALOR'].apply(fmt_num, tipo='REAL') 
EMPRESA_AJUS['PRODUTOS'] = EMPRESA_AJUS['PRODUTOS'].apply(fmt_num, tipo='NORMAL') 

st.divider()
col1, col2, col3 = st.columns(3)
col1.subheader('Empresas')
col1.dataframe(EMPRESA_AJUS, hide_index=True)
col2.subheader('Aging')
col2.dataframe(AGING_AJUS, hide_index=True)
col3.subheader('Areas')
col3.dataframe(AREA_AJUS, hide_index=True)
