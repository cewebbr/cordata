#!/usr/bin/env -S="streamlit run"
# http://localhost:8501
# -*- coding: utf-8 -*-

import json
import copy as cp
import streamlit as st
import requests
from streamlit_tags import st_tags
from datetime import datetime
from pathlib import Path
import os

# Move current working directory to the script’s directory
os.chdir(Path(__file__).parent)

# === CONFIG ===
DATA_FILE  = "data/usecases_current.json"
TEMP_FILE  = "data/usecases_temp.json"
EMPTY_FILE = "data/usecases_empty.json"
ENTRY_MODEL = "data/entry_model.json"

# Lists for controlled vocabularies
TYPE_OPTIONS = [
    "aplicativo ou plataforma",
    "artigo científico ou publicação acadêmica",
    "bot",
    "conjunto de dados",
    "estudo independente",
    "inteligência artificial",
    "matéria jornalística",
    "painel, dashboard ou infográfico",
    "outro"
    ]

TOPIC_OPTIONS = [
    "Agricultura, extrativismo e pesca",
    "Assistência e Desenvolvimento Social",
    "Ciência, Informação e Comunicação",
    "Comércio, Serviços e Turismo",
    "Cultura, Lazer e Esporte",
    "Dados Estratégicos",
    "Defesa e Segurança",
    "Economia e Finanças",
    "Educação",
    "Energia",
    "Equipamentos Públicos",
    "Gênero e Raça",
    "Geografia",
    "Governo e Política",
    "Habitação, Saneamento e Urbanismo",
    "Indústria",
    "Justiça e Legislação",
    "Meio Ambiente",
    "Plano Plurianual",
    "Relações Internacionais",
    "Religião",
    "Saúde",
    "Trabalho",
    "Transportes e Trânsito"
]

COUNTRY_OPTIONS = [
    "Brasil", "Mundial", "Argentina", "Chile", "Colômbia", "México", "Espanha"
]

def download_data():
    """
    Download CORDATA data currently up on the website.
    """
    url = 'https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json'
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        content = response.content.decode()
        data = json.loads(content)
        st.success('Dados carregados com sucesso')
        return data
    else:
        st.error(f'Falha no carregamento dos dados (status code {status})')

def save_data(path=TEMP_FILE):
    """
    Save current data dict to `path` (str).
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

def load_data(path):
    """
    Load JSON from file at `path` (str).
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.dialog('Adicionar novo caso')
def add_new_case():
    """
    Create a new usecase, add it to dataset and
    show it for edition.
    """
    # Ask for new usecase name:
    name = st.text_input("Nome:")
    if st.button("Criar!"):
        # Create new usecase:
        uc = load_data(ENTRY_MODEL)
        uc['name'] = name
        # Insert in dataset:
        usecases.insert(0, uc)
        save_data(TEMP_FILE)
        # Set to show it:
        st.session_state['idx_init'] = 0
        st.rerun()

# Initialization of session variables:
if 'idx_init' not in st.session_state:
    st.session_state['idx_init'] = None

# Sidebar:
st.sidebar.image('img/logo-cordata.png', width=200)


# === LOAD DATA ===
# Replace local data with the one from the repo:
if st.sidebar.button('🐙 Carregar do Github'):
    data = download_data()
    save_data()
    st.session_state['idx_init'] = None

# Remove all data from the app:
if st.sidebar.button('🗑️ Limpar a base'):
    data = load_data(EMPTY_FILE)
    save_data()
    st.success('Todos os casos de uso foram removidos')
# Load local data:
data = load_data(TEMP_FILE)
usecases = data["data"]

# Select usecase:
names = [uc['name'] for uc in usecases]
idx = st.sidebar.selectbox("Selecione o caso de uso:", range(len(usecases)), format_func=lambda i: names[i], 
                           index=st.session_state['idx_init'], on_change=save_data)

# Add new usecase:
st.sidebar.button('➕ Adicionar novo caso', on_click=add_new_case)


if idx != None:
    uc = usecases[idx]

    # Editing the selected usecase:
    st.subheader(f"{uc.get('name')}")

    # Mandatory fields:
    uc["name"] = st.text_input("Nome:", uc.get("name", ""))
    uc["url"] = st.text_input("Link:", uc.get("url", ""))

    # Optional fields:
    uc["description"] = st.text_area("Descrição:", uc.get('description', ''), height=200)
    pub_date = st.date_input(
        "Data de publicação:",
        datetime.strptime(uc.get("pub_date", "01/2000"), "%m/%Y").date() if uc.get("pub_date") else datetime.today().date(),
        format="DD/MM/YYYY"
    )
    uc["pub_date"] = pub_date.strftime("%m/%Y")
    uc['authors'] = st_tags(label='Autor:', value=uc.get('authors', []))
    uc["countries"] = st.multiselect("Countries", COUNTRY_OPTIONS, default=uc.get("countries", []))
    uc['email'] = st_tags(label='Email de contato:', value=uc.get('email', []))
    uc["type"] = st.multiselect("Type", TYPE_OPTIONS, default=uc.get("type", []))
    uc["topics"] = st.multiselect("Topics", TOPIC_OPTIONS, default=uc.get("topics", []))
    uc['tags'] = st_tags(label='Tags:', value=uc.get('tags', []))
    uc["url_source"] = st.text_input("Código fonte:", uc.get("url_source", ""))
    uc["url_image"] = st.text_input("Link para imagem:", uc.get("url_image", ""))
    uc["comment"] = st.text_area("Comentários internos:", uc.get('comment', ''), height=200)

    # Automatic fields:
    #uc["record_date"]


    # Datasets
    st.markdown("### Datasets")
    #if 'datasets' not in st.session_state:
    #    st.session_state['datasets'] = cp.deepcopy(uc['datasets'])
    #datasets = st.session_state['datasets']
    datasets = uc['datasets']

    rm_dataset_btn = []
    for i, ds in enumerate(datasets):
        with st.expander(f"Dataset {i+1}"):
            # Dataset metadata:
            ds["data_name"] = st.text_input("Nome do conjunto:", ds.get("data_name", ""), key=f"name_{i}")
            ds["data_institution"] = st.text_input("Instituição responsável:", ds.get("data_institution", ""), key=f"inst_{i}")
            ds["data_url"] = st.text_input("Link:", ds.get("data_url", ""), key=f"url_{i}")
            ds["data_periodical"] = st.radio("Uso periódico?",
                options=[True, False, None],
                index=[True, False, None].index(ds.get("data_periodical")),
                horizontal=True,
                format_func=(lambda x: {True:'Sim', False:'Não',None:'(vazio)'}[x]),
                key=f"periodical_{i}"
            )
            # Option to remove this dataset:
            def rm_dataset(index=i):
                uc['datasets'].pop(index)
                save_data()
            rm_dataset_btn.append(rm_dataset)
            st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=rm_dataset_btn[i])


    # Option to add new dataset
    def append_dataset():
        datasets.append({"data_name": "", "data_institution": "", "data_url": "", "data_periodical": None})
        save_data()

    st.button("➕ Adicionar conjunto de dados", on_click=append_dataset)

    # Save
    if st.button("💾 Salvar"):
        save_data()
        st.success("Dados salvos com sucesso!")


st.sidebar.download_button('⬇️ Baixar dados', json.dumps(data, indent=1, ensure_ascii=False), file_name='usecases_current.json')

    #uc['datasets'] = datasets
    #print(json.dumps(uc, indent=1))
    #print('')

print('\n>> Run!')