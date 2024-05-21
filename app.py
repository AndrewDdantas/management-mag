import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread as gs
import pandas as pd
import altair as alt

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

st.write('Total_$')
st.write(fmt_num(db['valor_total'].sum(),'REAL'))

st.write('Peças')
st.write(fmt_num(db['QT_ESTOQUE'].sum(),'NORMAL'))

st.write("Sku's")
st.write(fmt_num(db['IT_AJUSTADO'].nunique(),'NORMAL'))



# Fetch the 'LOG' worksheet and convert it to a DataFrame
log_worksheet = sheet.worksheet('LOG')
log_data = log_worksheet.get_all_values()
log = pd.DataFrame(log_data[1:], columns=log_data[0])  # Set the first row as column headers
log['VALOR'] = log['VALOR'].str.replace(',', '.').astype(float)
log['PRODUTOS'] = log['PRODUTOS'].str.replace(',', '.').astype(float)

AGING = log.groupby(['DATA','AGING']).agg({'PRODUTOS':'sum', 'VALOR':'sum'}).reset_index()
AGING_2 = AGING
AGING_2['PRODUTOS'] = AGING_2['PRODUTOS'].apply(fmt_num, tipo='NORMAL')
AGING_2['VALOR'] = AGING_2['VALOR'].apply(fmt_num, tipo='REAL')

AREA = log.groupby(['DATA','CD_AREA_ARMAZ']).agg({'PRODUTOS':'sum', 'VALOR':'sum'}).reset_index()
AREA_2 = AREA
AREA_2['PRODUTOS'] = AREA_2['PRODUTOS'].apply(fmt_num, tipo='NORMAL')
AREA_2['VALOR'] = AREA_2['VALOR'].apply(fmt_num, tipo='REAL')

st.dataframe(AREA_2)

chart_valor = alt.Chart(AGING).mark_bar().encode(
    x=alt.X('DATA:N', title='Data'),
    y=alt.Y('VALOR:Q', title='Valor'),
    color='AGING:N',
    tooltip=['DATA','AGING', 'VALOR']
).properties(
    width=400,
    height=400,
    title='Valor by Aging'
)

chart_produtos = alt.Chart(AGING).mark_bar().encode(
    x=alt.X('DATA:N', title='Data'),
    y=alt.Y('PRODUTOS:Q', title='Produtos'),
    color='AGING:N',
    tooltip=['DATA','AGING', 'PRODUTOS']
).properties(
    width=400,
    height=400,
    title='Produtos by Aging'
)

# Combine the charts
combined_chart = alt.hconcat(chart_valor, chart_produtos)

# Display the combined chart in Streamlit
st.altair_chart(combined_chart)


st.dataframe(AREA)

chart_valor = alt.Chart(AREA).mark_bar().encode(
    x=alt.X('DATA:N', title='Data'),
    y=alt.Y('VALOR:Q', title='Valor'),
    color='CD_AREA_ARMAZ:N',
    tooltip=['DATA','CD_AREA_ARMAZ', 'VALOR']
).properties(
    width=400,
    height=400,
    title='Valor by Aging'
)

chart_produtos = alt.Chart(AREA).mark_bar().encode(
    x=alt.X('DATA:N', title='Data'),
    y=alt.Y('PRODUTOS:Q', title='Produtos'),
    color='CD_AREA_ARMAZ:N',
    tooltip=['DATA','CD_AREA_ARMAZ', 'PRODUTOS']
).properties(
    width=400,
    height=400,
    title='Produtos by Aging'
)

# Combine the charts
combined_chart = alt.hconcat(chart_valor, chart_produtos)

# Display the combined chart in Streamlit
st.altair_chart(combined_chart)