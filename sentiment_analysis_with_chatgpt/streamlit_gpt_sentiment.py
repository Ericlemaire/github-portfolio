# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 11:56:49 2023

@author: ericlemaire
"""
import openai
import streamlit as st
from streamlit_chat import message
from time import time, sleep
import pandas as pd
import plotly.express as px
import time
import uuid

st.set_page_config(layout="wide")

st.sidebar.image("/Users/lemaireeric/Desktop/Teamtrust/Teamtrust - logotype vertical fond clair.png")

st.title(" 💬 ChatGPT pour l'analyse de sentiments")

with st.container():
    empty_space = st.empty()
    empty_space.text("""
    """)

vider_cache = st.sidebar.button("Effacer l'historique de la conversation")
if vider_cache:
    st.cache_data.clear()

st.container()

col1, col2 = st.columns([2, 2], gap="large")

with col1:
    with st.expander("Introduction"):
        st.markdown("""
            La présente application est destinée à l'analyse de sentiments exprimés dans différents verbatim, 
            que ce soit des avis laissés par des clients sur google par exemple, 
            ceux de salariés laissés dans une enquête interne.
            Cette application intègre la technologie **ChatGPT** pour produire les analyses de la voix des clients. 
            De nombreuses possibilités sont ouvertes. 
L'utilisateur peut demander au modèle de rendre compte de :

1) la **tonalité affective** (identification des sentiments et émotions), 
2) des **thèmes** clés, 
3) des **opinions** exprimées, 
4) de **résumer** les items précédents sous forme de textes
5) de générer des **réponses** aux commentaires
etc. 

Comment se servir des cette application ? 
1) Vous devez commencer par charger un jeu de données. 
2) Vous pouvez ensuite sélectionner les colonnes avec lesquelles vous souhaiteez travailler. Faîtes attention au fait que ces colonnes doivent comporter une colonne "Note" et une colonne "Date", et une dernière "Commentaires".
3) Réaliser un filtrage des données et appliquer les filtres pour définir l'ensemble de commentaires à analyser. 
4) Choisissez la praramètres du'tulisation de chatgpt. Vous pouvez les laisser tel quel pour commencer. 
5) Choisissez un prompt. 
IMPORTANT : n'oubliez pas de renseigner votre clé API OpenAI.
Pour obtenir une clé API OpenAI, rendez-vous ici : ....
            """)

with col2:
    with st.expander("Comment communiquer avec ChatGPT ?"):
        st.markdown("""
    L'utilisateur trouvera ci-dessous quelques **exemples d'instructions** qui ont été testées. 
    Elles peuvent servir de **points de départs** pour générer de nouvelles instructions plus adaptées à ses besoins.

    Quelques conseils : 
    1) Ecrivez des instructions **claires et spécifiques**. 
    2) N'ayez pas peur d'écrire des instructions **longues et détaillées** expliquant le **contexte** de votre recherche.     
    3) N'hésitez pas à spécifiez clairement les **étapes** requises pour compléter une tâche.
    4) **Réitérez** : si vous n'obtenez pas le résultat souhaité dès le premier essai, n'hésitez pas à **reformuler** votre demande. 
    5) Les sliders présents dans la barre latérale sont là pour vous aider à affiner votre recherche en fonction 
    des questions que vous vous posez. 
    6) Affiner votre recherche afin de passer dans le modèle uniquement des données pertinentes, ce qui permettra de **réduire vos coûts**.        
        """)

with st.sidebar:
    openai_api_key = st.text_input('OpenAI API Key', key='chatbot_api_key')

# Chargement des données (Avis google, avec notes...)
progress_text = "Operation in progress. Please wait."
my_bar = st.sidebar.progress(0, text=progress_text)
for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1, text=progress_text)

uploaded_file = st.sidebar.file_uploader("Télécharger un fichier CSV", type="csv")


# Chargement des données
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, sep=',')
    # remplissage des valeurs manquantes avec des 0
    # data = data.fillna(0)
    return data


@st.cache_data
def preparing(data):
    data = data.drop(["Avis client : N° d?avis", "Concession", "Client", "Réponse à l'avis"], axis=1)
    data = data.rename(columns={"Avis client : Date de création": "Date"})
    data["Date"] = pd.to_datetime(data["Date"], format='mixed')
    return data


# Préparation des données et création des options de filtrage :
if uploaded_file is not None:
    df = load_data(uploaded_file)
    df = preparing(df)
    st.dataframe(df)

elif uploaded_file is None:
    st.sidebar.warning("Veuillez charger un jeu de données !")

# if uploaded_file is not None:
#   col_selected = st.multiselect("Choisissez les colonnes", default=df.columns ,options=df.columns)
#   if col_selected is not None:
#      df = df[col_selected]
# elif col_selected is None:
#    pass
# elif uploaded_file is None:
#   pass


# FILTRAGE DES DONNEES ET GENERATION DE LA VARIABLE TEXTE UTILISEE DANS LES PROMPTS
st.subheader("Filtrage des données")
col1, col2 = st.columns([2, 2], gap="large")

# FILTRE NOTE:
with col1:
    st.subheader("Filtre par note")
    Filtre_note = st.slider(
        label="Filtrer par notes:",
        min_value=1,
        max_value=5,
        value=(1, 5),
        step=1)
    st.write("Vous avez choisi de filtrer:", Filtre_note)

    # FILTRE DATE:
with col2:
    st.subheader("Filtre par date")
    from datetime import time
    from datetime import datetime

    Filtre_date = st.slider(
        "Filtrer date:",
        min_value=datetime(2019, 1, 1),
        max_value=datetime(2024, 1, 1),
        value=(datetime(2019, 1, 1), datetime(2024, 1, 1)),
        # format='mixed'
    )
    st.write("Vous filtez les cate:", Filtre_date)

Filtrage = st.button("Appliquer les filtres au jeu de données")

if Filtrage:
    #    if Filtre_note:
    df = df[(df["Note"] >= Filtre_note[0]) & (df["Note"] <= Filtre_note[1])]
    #    if Filtre_date:
    df = df[(df["Date"] >= Filtre_date[0]) & (df["Date"] <= Filtre_date[1])]
    texte = list(df["Commentaire"].dropna())
    st.metric("Nombre de commentaires après filtrage", (~(df["Commentaire"].isna())).sum())

elif Filtrage is None:
    st.warning("Veulliez filter votre jeu de données")

tab1, tab2 = st.tabs(["Distribution des notes", "Les notes dans le temps"])

with tab1:
    #   st.header("Distribution des notes google")
    #   st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    if Filtrage:
        fig = px.histogram(df, x="Note")
        st.plotly_chart(fig)
    elif Filtrage is None:
        pass

with tab2:
    if Filtrage:
        df["Date"] = pd.to_datetime(df["Date"], exact=False)
        df_date = df.set_index(df["Date"])
        options_lissage = ['1W', '2W', '3W', '1M', "2M", '3M']
        lissage = st.selectbox("Durée pour le lissage de la moyenne",
                               options=options_lissage,
                               # format_func = options_lissage
                               )
        fig_2 = px.line(df_date["Note"].resample(lissage).mean())
        st.plotly_chart(fig_2)
    elif Filtrage is None:
        pass

# texte = list(df["Commentaire"].dropna())


st.subheader("Affichage des données filtrées")

col1, col2 = st.columns(2)
with col1:
    with st.expander("Voir la table de données"):
        if Filtrage:
            st.dataframe(df)
        elif Filtrage is None:
            pass

with col2:
    with st.expander("Voir les commentaires à copier dans le Prompt"):
        if Filtrage is not None:
            st.write(texte)
        elif Filtrage is None:
            pass

st.sidebar.subheader("Quelques idées de prompts:")

with st.sidebar.expander("Prompt_4 : Trouver quels sentiments s'expriment dans un commentaire client"):
    st.write(f"Peux-tu me dire quels sentiments (Positif, négatif, neutre) s'expriment dans le commentaire d'un client délimité par ''' ? \
            Tu ajouteras à ta réponses des émoticônes appropriés.\
             Commentaire client : '''{texte}''' ")

with st.sidebar.expander(
        "Prompt_2 : Trouver 5 sujets exprimant des critiques et de de la satisfaction  présents dans un ensemble de commentaires client"):
    st.write(f"Dans la liste de commentaires données délimitée par '' , identifie les choses suivantes :"
             f" - cinq sujets exprimant des critiques importants dans les commentaires."
             f"- cinq sujets exprimant de la satisfaction importants dans les commentaires."
             f" - Tu présenteras ta réponse comme une liste de points numérotés en veillant à séparer \
                     clairement les sujets critiques des sujets exprimant de la satifaction."
             f"liste de commentaires: '''{texte}''' """
             "")

with st.sidebar.expander(
        "Prompt_3 : Identifier 1)Les sentiments, 2) Les émotions, 3) La colère, 4) Les sujets, 5) les opinions exprimées, dans un ensemble de commentaires client"):
    st.write("""
             Dans la liste de commentaires données délimitée par ''', identifie les choses suivantes : 
                 - Sentiment (positif, négatif ou neutre).
                 - Les émotions qui s'expriment
                 - Le commentaire contient-il de la colère ? 
                 - les sujets abordés dans les commentaires.
                 - Présente les opinions exprimés dans les commentaires en moins de 50 mots.
liste de commentaires: '''{texte}'''
""")

with st.sidebar.expander("Prompt_4 : Résumer les informations pertinentes dans un ensemble de commentaires client"):
    st.write("""
             Ton travail consiste à résumer les avis clients présents dans la liste python délimitée par ```. 
             Ton résumé ne doit pas dépasser cent mots. 

            Commentaires client : ```{texte}```    
    OU 
        Pour chaque commentaire dans la liste de commentaires délimitées par '''', \
            peux-tu extraire l'information pertinente ? \

        Ensuite, résume l'analyse dans un texte de cinquante mots environ.
        Liste de commentaires : ```{texte}```

    """)

with st.sidebar.expander(
        "Prompt_5: analyser les opinions et sentiments présents dans une liste de commentaires, en détaillant puis en résumant"):
    st.write("""
            Dans la liste de commentaires indiquée entre ''', \ 
                en 40 caractères au maximum, peux-tu me préciser quelles opinions se dégagent de ces commentaires ? \

    Tu organiseras ta réponse comme suit :\

    - Commentaire 1 : 
        Opinion 1
        Sentiment 

    - Commentaire 2 : 
        Opinion 2
        sentiment 

    et ainsi de suite \

    Ensuite peux-tu préciser en un mot quel est le sentiment dominant dans le commentaire. \

    Compte le nombre de commentaires dont la tonalité est négative \_

    Enfin, peux-tu résumer en 50 mots au plus les opinions exprimées dans les commentaires analysés ? \
        Liste de commentaires: '''{texte}'''
             """)

with st.sidebar.expander("Prompt_6: Créer une réponse à un commentaire"):
    st.write("""
            Rédige une réponse au commentaire d'un client.
            A partir du commentaire délimité par ```, \
            génère une pour remercier le clients pour son commentaire.
            Si le sentiment exprimé dans le commentaire est positif ou neutre, alors remercie le client pour son message.\
            En revanche, si le sentiment exprimé dans le commentaire est négatif, présente tes excuses et suggère au client \
            de prendre contact avec le service client. 
            Pour générer ta réponse au client, Utilise un maximum de détails issu du commentaire du client.
            Ecris dans un style professionnel et sobre.
            Signe le message par `A compléter`.
            Commentaire client: ```{texte}```
             """)

# REGLAGE DE CHATGPT-HESS :

st.subheader('Réglage des paramètres du modèle')

# Choix du modèle
radio_markdown = '''
[Voir les caractéristiques des modèles](https://platform.openai.com/docs/models/overview)'''.strip()

choix_model = st.selectbox("Je choisis un modèle",
                           options=[  # " gpt-4",
                               "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
                           # ,"text-davinci-003","text-curie-001", "text-babbage-001", "text-ada-001"]
                           , help=radio_markdown
                           )
st.sidebar.info("[Mieux comprendre les modèles en suivant ce lien:](https://platform.openai.com/docs/models/overview)")

# Liberté du modèle

col1, col2 = st.columns(2)

with col1:
    with st.form("Choix du prompt"):
        prompts_dictionary = {'Prompt 1 : Résumer les informations pertinentes dans un ensemble de commentaires ':

                                  f"Peux-tu me dire quels sentiments (Positif, négatif, neutre) s'expriment dans le commentaire d'un client délimité par ''' ? \
                                Tu ajouteras à ta réponses des émoticônes appropriés.\
                                 Commentaire client : '''{texte}''' ",

                              "Prompt_2 : Trouver 5 sujets exprimant des critiques et de de la satisfaction  présents dans un ensemble de commentaires client":

                                  f"Dans la liste de commentaires données délimitée par '' , identifie les choses suivantes :"
                                  f" - cinq sujets exprimant des critiques importants dans les commentaires."
                                  f"- cinq sujets exprimant de la satisfaction importants dans les commentaires."
                                  f" - Tu présenteras ta réponse comme une liste de points numérotés en veillant à séparer \
                                                     clairement les sujets critiques des sujets exprimant de la satifaction."
                                  f"liste de commentaires: '''{texte}''' """
                                  "",
                              "Prompt_3 : Identifier 1) Les sentiments, 2) Les émotions, 3) La colère, 4) Les sujets, 5) les opinions exprimées, dans un ensemble de commentaires client":

                                  f"Dans la liste de commentaires données délimitée par ''', identifie les choses suivantes :  \ "
                                  f"- Sentiment (positif, négatif ou neutre).\
                                 - Les émotions qui s'expriment\
                                 - Le commentaire contient-il de la colère ? \
                                 - les sujets abordés dans les commentaires.\
                                 - Présente les opinions exprimés dans les commentaires en moins de 50 mots.\
                                    liste de commentaires: '''{texte}'''.",

                              "Prompt_6: Créer une réponse à un commentaire":

                                  f"Rédige une réponse au commentaire d'un client.A partir du commentaire délimité par ```, \
                                    génère une pour remercier le clients pour son commentaire.Si le sentiment exprimé dans le commentaire est positif ou neutre, alors remercie le client pour son message.\
                                    En revanche, si le sentiment exprimé dans le commentaire est négatif, présente tes excuses et suggère au client \
                                    de prendre contact avec le service client. Pour générer ta réponse au client, Utilise un maximum de détails issu du commentaire du client."
                                  f"Ecris dans un style professionnel et sobre."
                                  f"Signe le message par `A compléter`."
                                  f"Commentaire client: ```{texte}```."
                              }

        chosen_prompt = st.selectbox(label="Que voulez-vous savoir ?", options=prompts_dictionary.keys())
        # prompt = st.button("Prompt_4 : Résumer les informations pertinentes dans un ensemble de commentaires client")
        if chosen_prompt:
            user_input = prompts_dictionary[chosen_prompt]
            st.form_submit_button("Appliquer")

# Choix du modèle
radio_markdown = '''
[Voir les caractéristiques des modèles](https://platform.openai.com/docs/models/overview)'''.strip()

with col2:
    with st.form("Paramètres du modèle"):
        Temperature = st.slider('Liberté', min_value=0.0, max_value=1.0, value=0.0, step=0.01, help=radio_markdown)
        # Top P
        Top_P = st.slider('Top P', min_value=0.0, max_value=1.0, value=0.0, step=0.01)
        # Penalités : présence et fréquence
        Penalite_frequence = st.slider('Pénalité : fréquence', min_value=0.0, max_value=2.0, value=0.0, step=0.01)

        Penalite_presence = st.slider('Prénalité : présence', min_value=0.0, max_value=2.0, value=0.0, step=0.01)
        # Longueur maximum de l'output
        # Longueur_output =   st.sidebar.slider('Longueur max du résultat', min_value=1, max_value=4000, value=50, step=1)
        # Best of
        # Bigmac =  st.sidebar.slider('Best_of', min_value=0, max_value=20, value=0, step=1)
        st.form_submit_button(label="Appliquer")

if "messages" not in st.session_state:
    st.session_state.messages = []

widget_key = str(uuid.uuid4())

for msg in st.session_state.messages:
    # Tentative de générer une clé spécifique à chaque appel de la fonction.
    widget_key = str(uuid.uuid4())

    message(msg["content"], is_user=msg["role"] == "user",
            key=widget_key
            )

if user_input and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

if user_input and openai_api_key:
    openai.api_key = openai_api_key
    st.session_state.messages.append({"role": "user", "content": user_input})
    message(user_input, is_user=True)
    response = openai.ChatCompletion.create(model=choix_model,
                                            messages=st.session_state.messages,
                                            temperature=Temperature,
                                            # this is the degree of randomness of the model's output
                                            # max_tokens=Longueur_output,
                                            # best_of=Bigmac ,
                                            top_p=Top_P,
                                            frequency_penalty=Penalite_frequence,
                                            presence_penalty=Penalite_presence
                                            )
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    message(msg.content)
