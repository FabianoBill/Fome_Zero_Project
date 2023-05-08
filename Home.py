# Problema de Negócio

# A empresa Fome Zero é uma marketplace de restaurantes que disponibiliza informações como endereço, tipo de culinária servida, disponibilidade de reservas,  entregas, nota de avaliação dos serviços e produtos do restaurante, dentre outras informações.

# CEO Kleiton Guerra 
# Como o objetivo de  etender melhor o negócio para conseguir tomar as melhores decisões estratégicas e alavancar ainda mais a empresa, e para isso,  foi feita uma análise nos dados gerando dashboards

import pandas as pd
import numpy as np
import inflection
import folium
from folium.plugins import MarkerCluster
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(page_title='Home', page_icon='🎲', layout="wide")

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
# There is at least one row in the 'Cuisines' column that contains a float value instead of a string value.
# As a float does not have the 'split' method, this causes an AttributeError.
#To fix this error, it is necessary to ensure that all values in the 'Cuisines' column are strings
# add ***.astype(str)*** to the code

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
    default=["Australia", "Brazil", "South Africa", "United States of America"],
)


# st.sidebar.markdown("### Dados Tratados")
# processed_data = pd.read_csv("./data/processed/data.csv")
# st.sidebar.download_button(
#     label="Download",
#     data=processed_data.to_csv(index=False, sep=";"),
#     file_name="data.csv",
#     mime="text/csv",
# )



################################################################################
#############################   CONTEÚDO   #####################################
################################################################################

st.header('Fome Zero')
st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')
st.markdown('''### Temos as seguintes marcas dentro da nossa plataforma:''')


col1, col2, col3, col4, col5  = st.columns(5)
with col1:
    col1.metric('Restaurantes Cadastrados', df1['restaurant_id'].nunique())
    
with col2:
    col2.metric('Países Cadastrados', df1['country_code'].nunique())  
    
with col3:
    col3.metric('Cidades Cadastradas', df1['city'].sort_values().nunique())
    
with col4:
    col4.metric('Avaliações Feitas', df1['votes'].sum())
    
with col5:
    col5.metric('Tipos de Culinárias', df1['cuisines'].nunique())    

        

##################################################  MAPA  ###########################################################

df2 = df1.loc[:, ['latitude', 'longitude', 'restaurant_name', 'average_cost_for_two', 'cuisines', 'aggregate_rating', 'rating_colour', 'country']]

map_df = df2.loc[df2['country'].isin(paises), :]

mapa = folium.Map()  # criar um mapa folium

marcadores = []  # criar uma lista vazia para os marcadores

marker_cluster = MarkerCluster().add_to(mapa) # criar um grupo de marcadores 

for index, row in map_df.iterrows(): # percorrer cada linha do DataFrame
    popup_html = f"<b>{row['restaurant_name']}</b><br><br>"\
                 f"<b>Culinária:</b> {row['cuisines']}<br>"\
                 f"<b>Preço:</b> {row['average_cost_for_two']},00<br>"\
                 f"<b>Avaliação:</b> {row['aggregate_rating']}/5.0"
    
    icone = folium.Icon(color=row['rating_colour'])
    # criar um marcador para cada localização
    marcador = (folium.Marker([row['latitude'], row['longitude']],
                              popup=popup_html, icon=icone))
    marcadores.append(marcador) # adicionar o marcador à lista de marcadores

for marker in marcadores: # adicionar todos os marcadores ao grupo de marcadores
    marker.add_to(marker_cluster)
    
folium_static(mapa, width=1024, height=768)