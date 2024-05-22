import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread as gs
import pandas as pd
from io import StringIO
import altair as alt
from datetime import datetime, timedelta



def to_csv(df):
    output = StringIO()
    df.to_csv(output, index=False)
    processed_data = output.getvalue()
    return processed_data


def color_negative_red_positive_green(val):
    try:
        val = float(val.replace('.', '').replace(',', '.'))
    except ValueError:
        return ''
    color = 'red' if val > 0 else 'green'
    return f'color: {color}'


def fmt_num(valor, tipo, casas=0):
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


st.set_page_config(
    page_title="GERENCIAMENTO",
    page_icon=":chart_with_upwards_trend:",
    layout="wide", 
    initial_sidebar_state="auto",
)

update = (datetime.now() - timedelta(hours=3)).strftime('%d/%m/%Y')

st.title('Gestão Bloqueios CDs')
st.write(f'Update: '+update)

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = gs.authorize(credentials)


sheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1SlnFPqnbVkwEh3Gt56lNxIadE2tfUfQy-KsFn4Xx5l4/edit#gid=1350786165')

db_worksheet = sheet.worksheet('DB')
db_data = db_worksheet.get_all_values()
db = pd.DataFrame(db_data[1:], columns=db_data[0])
db['valor_total'] = db['valor_total'].str.replace(',', '.').astype(float)
db['QT_ESTOQUE'] = db['QT_ESTOQUE'].str.replace(',', '.').astype(float)

col1, col2, col3 = st.columns(3)


col1_emp = col1.empty()
col2_emp = col2.empty()
col3_emp = col3.empty()

st.divider()

log_worksheet = sheet.worksheet('LOG')
log_data = log_worksheet.get_all_values()
log = pd.DataFrame(log_data[1:], columns=log_data[0]) 
log['VALOR'] = log['VALOR'].str.replace(',', '.').astype(float)
log['PRODUTOS'] = log['PRODUTOS'].str.replace(',', '.').astype(float)

c1,c2 = st.columns(2)
emp = c1.selectbox('Empresa' ,['Todos'] + db['CD_EMPRESA'].drop_duplicates().values.tolist() )

agings = c2.selectbox('Aging' ,['Todos'] + db['aging'].drop_duplicates().values.tolist() )

areas = c1.selectbox('Área' ,['Todos'] + db['DS_AREA_ARMAZ_y'].drop_duplicates().values.tolist() )

tipos = c2.selectbox('Tipo Endereço' ,['Todos'] + db['TIPO_ENDEREÇO'].drop_duplicates().values.tolist() )

if emp != 'Todos':
    log = log.loc[log['CD_EMPRESA'] == emp]
    db = db.loc[db['CD_EMPRESA'] == emp]
else:
    log = log
    db = db

if agings != 'Todos':
    log = log.loc[log['AGING'] == agings]
    db = db.loc[db['aging'] == agings]
else:
    log = log
    db = db

if areas != 'Todos':
    log = log.loc[log['CD_AREA_ARMAZ'] == areas]
    db = db.loc[db['DS_AREA_ARMAZ_y'] == areas]
else:
    log = log
    db = db

if tipos != 'Todos':
    log = log.loc[log['TIPO_ENDEREÇO'] == tipos]
    db = db.loc[db['TIPO_ENDEREÇO'] == tipos]
else:
    log = log
    db = db

col1, col2 = st.columns([2,1])

total = fmt_num(db['valor_total'].sum(),'REAL')
col1_emp.subheader(f'Custo Total: {total}')

pecas = fmt_num(db['QT_ESTOQUE'].sum(),'NORMAL')
col2_emp.subheader(f'Peças: {pecas}')

sku = fmt_num(db['IT_AJUSTADO'].nunique(),'NORMAL')
col3_emp.subheader(f"Sku's: {sku}")


pivot_table_empresa = pd.pivot_table(log,'VALOR','CD_EMPRESA','DATA','sum')
recent_dates = sorted(pivot_table_empresa.columns, key=lambda x: pd.to_datetime(x, dayfirst=True), reverse=False)[:5]
pivot_table_empresa = pivot_table_empresa[recent_dates]
if len(recent_dates) >= 2:
    pivot_table_empresa['Diferença'] = pivot_table_empresa[recent_dates[-1]] - pivot_table_empresa[recent_dates[-2]]
pivot_table_empresa = pivot_table_empresa.sort_values(recent_dates[-1], ascending=False)
pivot_table_empresa = pivot_table_empresa.applymap(fmt_num, tipo='NORMAL')
styled_pivot_table_empresa = pivot_table_empresa.style.applymap(color_negative_red_positive_green, subset=['Diferença'])
col1.subheader('Evolução Cds')
col1.dataframe(styled_pivot_table_empresa)



pivot_table_aging = pd.pivot_table(log,'VALOR','AGING','DATA','sum')
recent_dates = sorted(pivot_table_aging.columns, key=lambda x: pd.to_datetime(x, dayfirst=True), reverse=False)[:5]
pivot_table_aging = pivot_table_aging[recent_dates]
if len(recent_dates) >= 2:
    pivot_table_aging['Diferença'] = pivot_table_aging[recent_dates[-1]] - pivot_table_aging[recent_dates[-2]]
pivot_table_aging = pivot_table_aging.sort_values(recent_dates[-1], ascending=False)
pivot_table_aging = pivot_table_aging.applymap(fmt_num, tipo='NORMAL')
styled_pivot_table_aging = pivot_table_aging.style.applymap(color_negative_red_positive_green, subset=['Diferença'])
col1.subheader('Evolução Aging')
col1.dataframe(styled_pivot_table_aging)


pivot_table_area = pd.pivot_table(log,'VALOR','CD_AREA_ARMAZ','DATA','sum')
recent_dates = sorted(pivot_table_area.columns, key=lambda x: pd.to_datetime(x, dayfirst=True), reverse=False)[:5]
pivot_table_area = pivot_table_area[recent_dates]
if len(recent_dates) >= 2:
    pivot_table_area['Diferença'] = pivot_table_area[recent_dates[-1]] - pivot_table_area[recent_dates[-2]]
pivot_table_area = pivot_table_area.sort_values(recent_dates[-1], ascending=False)
pivot_table_area = pivot_table_area.applymap(fmt_num, tipo='NORMAL')
styled_pivot_table_area = pivot_table_area.style.applymap(color_negative_red_positive_green, subset=['Diferença'])
col1.subheader('Evolução Áreas')
col1.dataframe(styled_pivot_table_area)

tipo_endereco = log.groupby(['DATA','TIPO_ENDEREÇO']).agg({'VALOR':'sum'}).reset_index()
tipo_endereco = tipo_endereco.loc[tipo_endereco['DATA'] == recent_dates[-1]]

aging = log.groupby(['DATA','AGING']).agg({'VALOR':'sum'}).reset_index()
aging = aging.loc[aging['DATA'] == recent_dates[-1]]

val = aging['VALOR'].sum()
aging['%'] = aging['VALOR'] / val
aging['AGING'] = aging['AGING'] +" - "+ aging['VALOR'].apply(lambda x: fmt_num(x / val, tipo='PORCENTAGEM'))


chart = alt.Chart(aging).mark_arc(innerRadius=50).encode(
    theta=alt.Theta(field="%", type="quantitative"),
    color=alt.Color(field="AGING", type="nominal", legend=alt.Legend(
        title="Aging Categories",
        titleFontSize=14,
        labelFontSize=12,
        orient='right',
        direction='vertical'
    ))
).properties(
    title="Distribuição de Valores por Aging"
)


chart_tipo = alt.Chart(tipo_endereco).mark_bar().encode(
    x='VALOR:Q',
    y=alt.Y('TIPO_ENDEREÇO:N', sort='-x')  # Ordena do maior para o menor valor
).properties(
    title="Tipos de Endereços"
)

chart_tipo_text = chart_tipo.mark_text(
    align='right',  # Centraliza o texto horizontalmente
    baseline='middle',  # Centraliza o texto verticalmente
    dx=0  # Sem deslocamento horizontal
).encode(
    text=alt.Text('VALOR:Q', format=',.0f'),
    color=alt.condition(
        alt.datum.VALOR > 75,  # Condição para alterar a cor do texto
        alt.value('white'),  # Texto branco para valores maiores que 75
        alt.value('black')   # Texto preto para valores menores ou iguais a 75
    )
)


chart_tipo = chart_tipo+chart_tipo_text

col2.subheader('Tipos de Endereços')
col2.altair_chart(chart_tipo)


final_chart = chart 

col2.subheader('Aging')
col2.altair_chart(final_chart)

button = st.button('GERAR CSV')

if button:
    with st.spinner('Gerando arquivo.'):
        csv_data = to_csv(db)
        st.download_button(
            label="Baixar dados como CSV",
            data=csv_data,
            file_name='dados.csv',
            mime='text/csv'
        )



