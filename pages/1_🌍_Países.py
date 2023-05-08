import pandas as pd
import numpy as np
import inflection
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Países', page_icon='🏳', layout="wide")

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

st.markdown("# 🌍 Países")

with st.container():
    paises_reg = (df1.loc[df1['country'].isin(paises), ['country', 'restaurant_id']]
                      .groupby('country')
                      .count()
                      .sort_values('restaurant_id', ascending=False)
                      .reset_index()
                 )
    st.plotly_chart(px.bar(paises_reg, 
                x="country", 
                y="restaurant_id",
                text="restaurant_id",
                title="Quantidade de Restaurantes Registrados por País",
                labels={"country": "Paises",
                        "restaurant_id": "Quantidade de Restaurantes"}, 

                          ), use_container_width=True
                   )
    
with st.container():
# qtd de cidades registradas em cada país    
    cidade_reg = (
                    df1.loc[df1["country"].isin(paises), ["city", "country"]]
                    .groupby("country")
                    .nunique()
                    .sort_values("city", ascending=False)
                    .reset_index()
    )

    st.plotly_chart(px.bar(
                    cidade_reg,
                    x="country",
                    y="city",
                    text="city",
                    title="Quantidade de Cidades Registradas por País",
                    labels={
                        "country": "Paises",
                        "city": "Quantidade de Cidades",
                    }
    ), use_container_width=True
                   )







with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        # Média de avaliação por país
        m = (df1.loc[df1["country"].isin(paises), ['country','votes']]
                 .groupby('country')
                 .mean()
                 .sort_values('votes', ascending=False)
                 .reset_index())
        
        st.plotly_chart(px.bar(
                    m,
                    x="country",
                    y="votes",
                    text="votes",
                    text_auto=".2f",
                    title="Média por País",
                    labels={"country": "Paises", "votes": "Média"}
                            ), use_container_width=True
                       )
        
    with col2:
        # Média de preço por prato
        preco = (df1.loc[df1["country"].isin(paises), ['country', 'average_cost_for_two']]
                 .groupby('country')
                 .mean()
                 .reset_index()
                 .sort_values('country'))
        
        st.plotly_chart(px.bar(
                    preco,
                    x="country",
                    y="average_cost_for_two",
                    text="average_cost_for_two",
                    text_auto=".2f",
                    title="Preço médio de prato p/2 por País",
                    labels={"country": "Paises", "average_cost_for_two": "Preço do prato p/2"}
                            ), use_container_width=True
                       )