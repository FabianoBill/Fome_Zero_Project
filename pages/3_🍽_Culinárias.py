import pandas as pd
import numpy as np
import inflection
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Culinária', page_icon='🍽', layout='wide')

df = pd.read_csv('dataset/zomato.csv')
df1 = df.copy()

############################################## FUNÇÕES #########################################
def country_name(country_id):
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    return COUNTRIES[country_id]

# Criação do Tipo de Categoria de Comida
def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"
    
def rename_columns(dataframe): #Renomear as colunas do DataFrame removendo os espaços
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df1.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df1.columns = cols_new
    return df1

def color_name(color_code): # Criação do nome das Cores
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    return COLORS[color_code]

################################################### Limpesa #############################################

df1 = df1.drop_duplicates() # Removendo as linhas duplicadas
df1=df1.dropna() # Removendo NaNs
rename_columns(df1)  #Renomeando as colunas do DataFrame removendo os espaços

for i in range(len(df1.columns)): # strip em todas as colunas de strings
    if type(df1.iloc[0,i])==str:
        df1.iloc[:,i]=df1.iloc[:,i].str.strip()

country = []  # Criando uma nova coluna com os nomes dos países
for i in df1['country_code']:
    nome = country_name(i)  # passando o método country_name() em todas as linhas
    country.append(nome)
df1['country'] = country

price_type = []  # Criando uma nova coluna com os tipos de preço
for i in df1['price_range']:
    nome = create_price_type(i) # passando o método create_price_type() em todas as linhas
    price_type.append(nome)
df1['price_type'] = price_type


rating_colour = []  # Criando uma nova coluna com os tipos de preço
for i in df1['rating_color']:
    nome = color_name(i) # passando o método color_name() em todas as linhas
    rating_colour.append(nome)  
df1['rating_colour'] = rating_colour

# Mantendo somente o primeiro tipo de culinária
df1['cuisines'] = df1['cuisines'].astype(str).apply(lambda x: x.split(',')[0]) 

df1 = df1.drop('switch_to_order_menu', axis=1)  # A coluna 'Switch to order menu' tem apenas um valor e deve ser removida.
#df1 = df1.drop('country_code', axis=1)
#df1 = df1.drop('rating_color', axis=1)


###############################  BARRA LATERAL  ################################

image = Image.open('zomato.png')

col1, col2 = st.sidebar.columns([1, 4], gap="small")
col1.image(image, width=35)
col2.header(" Fome Zero")

st.sidebar.markdown("## Filtros")

paises = st.sidebar.multiselect(
    "Escolha os paises que deseja visualizar:",
    df1.loc[:, "country"].unique().tolist(),
    default=["Australia", "Brazil", "South Africa", "United States of America",],
)

top_n = st.sidebar.slider(
    "Selecione a quantidade de Restaurantes que deseja visualizar", 1, 20, 10
)

culinarias = st.sidebar.multiselect("Escolha os Tipos de Culinária ", df1.loc[:, "cuisines"].unique().tolist(), default=["Home-made", "BBQ", "Japanese", "Brazilian", "Arabian", "American", "Italian"])


####################################################### Perguntas Tipos de Culinária ###############################################

st.markdown("# :knife_fork_plate: Tipos de Culinárias")
st.markdown(f"## Melhores restaurantes dos principais tipos culinários")

col1, col2, col3, col4, col5  = st.columns(5)

with col1:
    italiana = (df1.loc[df1['cuisines']=='Italian', ['country', 'city', 'restaurant_name', 'aggregate_rating']]
    .groupby(['country', 'city', 'restaurant_name'])
    .mean()
    .reset_index()
    .sort_values('aggregate_rating', ascending=False))
    col1.metric(f'Italiana: {italiana.iloc[0,2]}', 
                f'{italiana.iloc[0,3]}/5.0',
                help=f"""
            País: {italiana.iloc[0,0]}\n
            Cidade: {italiana.iloc[0,1]}\n
                        """)

with col2:
    americana = (df1.loc[df1['cuisines']=='American', ['country', 'city', 'restaurant_name', 'aggregate_rating']]
    .groupby(['country', 'city', 'restaurant_name'])
    .mean()
    .reset_index()
    .sort_values('aggregate_rating', ascending=False))
    col2.metric(f'Americana: {americana.iloc[0,2]}', 
                f'{americana.iloc[0,3]}/5.0',
                help=f"""
            País: {americana.iloc[0,0]}\n
            Cidade: {americana.iloc[0,1]}\n
                        """)

with col3:
    arabe = (df1.loc[df1['cuisines']=='Arabian', ['country', 'city', 'restaurant_name', 'aggregate_rating']]
    .groupby(['country', 'city', 'restaurant_name'])
    .mean()
    .reset_index()
    .sort_values('aggregate_rating', ascending=False))
    col3.metric(f'Árabe: {arabe.iloc[0,2]}', 
                f'{arabe.iloc[0,3]}/5.0',
                help=f"""
            País: {arabe.iloc[0,0]}\n
            Cidade: {arabe.iloc[0,1]}\n
                        """)

with col4:
    japonesa = (df1.loc[df1['cuisines']=='Japanese', ['country', 'city', 'restaurant_name', 'aggregate_rating']]
    .groupby(['country', 'city', 'restaurant_name'])
    .mean()
    .reset_index()
    .sort_values('aggregate_rating', ascending=False))
    col4.metric(f'Japonesa: {japonesa.iloc[0,2]}', 
                f'{japonesa.iloc[0,3]}/5.0',
                help=f"""
            País: {japonesa.iloc[0,0]}\n
            Cidade: {japonesa.iloc[0,1]}\n
                        """)

with col5:
    caseira = (df1.loc[df1['cuisines']=='Home-made', ['country', 'city', 'restaurant_name', 'aggregate_rating']]
    .groupby(['country', 'city', 'restaurant_name'])
    .mean()
    .reset_index()
    .sort_values('aggregate_rating', ascending=False))
    col5.metric(f'Caseira: {caseira.iloc[0,2]}', 
                f'{caseira.iloc[0,3]}/5.0',
                help=f"""
            País: {caseira.iloc[0,0]}\n
            Cidade: {caseira.iloc[0,1]}\n
                        """)
st.markdown(f"## Top {top_n} Restaurantes")
    

cols = [
    "restaurant_id",
    "restaurant_name",
    "country",
    "city",
    "cuisines",
    "average_cost_for_two",
    "aggregate_rating",
    "votes",
]

lines = (df1["cuisines"].isin(culinarias)) & (df1["country"].isin(paises))

st.dataframe(df1.loc[lines, cols].sort_values(["aggregate_rating", "restaurant_id"], ascending=[False, True]).head(top_n))




lines = df1["country"].isin(paises)
melhores = (df1.loc[lines, ['cuisines', 'aggregate_rating']]
                .groupby('cuisines')
                .mean()
                .sort_values('aggregate_rating', ascending=False)
                .reset_index()
                .head(top_n)
           )
fig1 = (px.bar(
    melhores,
    x="cuisines",
    y="aggregate_rating",
    text="aggregate_rating",
    text_auto=".2f",
    title=f"Top {top_n} melhores tipos de culinárias",
    labels={
        "cuisines": "Tipo de Culinária",
        "aggregate_rating": "Avaliação Média"
    }
))
st.plotly_chart(fig1, use_container_width=True)  
        


piores = (df1.loc[lines, ['cuisines', 'aggregate_rating']]
                .groupby('cuisines')
                .mean()
                .sort_values('aggregate_rating')
                .reset_index()
                .head(top_n)
         )

fig2 = (px.bar(
    piores,
    x="cuisines",
    y="aggregate_rating",
    text="aggregate_rating",
    text_auto=".2f",
    title=f"Top {top_n} piores tipos de culinárias",
    labels={
        "cuisines": "Tipo de Culinária",
        "aggregate_rating": "Avaliação Média"
    }
))

st.plotly_chart(fig2, use_container_width=True)  