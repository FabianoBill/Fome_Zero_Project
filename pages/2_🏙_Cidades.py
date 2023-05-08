import pandas as pd
import numpy as np
import inflection
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Cidades', page_icon='📫', layout='wide')

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
    default=["Australia", "Brazil", "South Africa", "United States of America",],
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

st.markdown("# 🏙 Cidades")

cidade_rest = (df1.loc[df1['country'].isin(paises), ['city', 'country', 'restaurant_id']]
                   .groupby(['country','city'])
                   .count()
                   .sort_values(['restaurant_id', 'country'], ascending=False)
                   .reset_index()
                   )

st.plotly_chart(px.bar(cidade_rest.head(10), 
                x="city", 
                y="restaurant_id",
                text="restaurant_id",
                color="country",
                title="Top 10 das cidades com mais restaurantes cadastrados",
                labels={"city": "Cidades",
                        "restaurant_id": "Quantidade de Restaurantes",
                       "country": "País"}, 

                          ), use_container_width=True
                   )


# Top 7 das cidades com média de avaliação acima de 4

cidade_acima = (df1.loc[(df1["aggregate_rating"] >= 4) & (df1["country"].isin(paises)), ["restaurant_id", "country", "city"]]
                    .groupby(["country", "city"])
                    .count()
                    .sort_values(["restaurant_id", "city"], ascending=[False, True])
                    .reset_index()
)

st.plotly_chart(px.bar(cidade_acima.head(7),
    x="city",
    y="restaurant_id",
    text="restaurant_id",
    color="country",
    title="Top 7 das cidades com média de avaliação acima de 4",
    labels={
        "city": "Cidade",
        "restaurant_id": "Quantidade de Restaurantes",
        "country": "País"
            }
                      ), use_container_width=True
               )

# Top 7 Cidades com Restaurantes com média de avaliação abaixo de 2.5

cidade_abaixo = (
    df1.loc[
        (df1["aggregate_rating"] <= 2.5) & (df1["country"].isin(paises)),
        ["restaurant_id", "country", "city"],
    ]
    .groupby(["country", "city"])
    .count()
    .sort_values(["restaurant_id", "city"], ascending=[False, True])
    .reset_index()
)

st.plotly_chart(px.bar(
    cidade_abaixo.tail(7),
    x="city",
    y="restaurant_id",
    text="restaurant_id",
    color="country",
    title="Top 7 Cidades com Restaurantes com média de avaliação abaixo de 2.5",
    labels={
        "city": "Cidade",
        "restaurant_id": "Quantidade de Restaurantes",
        "country": "País",
    },
                    ), use_container_width=True
            )


# Top 10 Cidades mais restaurantes com tipos culinários distintos

culinaria = (
    df1.loc[df1["country"].isin(paises), ["cuisines", "country", "city"]]
    .groupby(["country", "city"])
    .nunique()
    .sort_values(["cuisines", "city"], ascending=[False, True])
    .reset_index()
)

st.plotly_chart(px.bar(
    culinaria.head(10),
    x="city",
    y="cuisines",
    text="cuisines",
    color="country",
    title="Top 10 Cidades mais restaurantes com tipos culinários distintos",
    labels={
        "city": "Cidades",
        "cuisines": "Quantidade de Tipos Culinários Únicos",
        "country": "País",
            }
                    ), use_container_width=True
               )
