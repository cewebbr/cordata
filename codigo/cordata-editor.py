#!/usr/bin/env -S="streamlit run"
# -*- coding: utf-8 -*-

import json
import copy as cp
import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime
from pathlib import Path

# === CONFIG ===
DATA_FILE = "data/usecases_current.json"

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

# === LOAD DATA ===
if "data" not in st.session_state:
    st.session_state["data"] = json.loads(Path(DATA_FILE).read_text(encoding="utf-8"))
usecases = st.session_state["data"]["data"]

# === GUI ===
st.title("Editor de casos do CORDATA")

# Select use case:
names = [uc['name'] for uc in usecases]
idx = st.selectbox("Selecione o caso de uso:", range(len(usecases)), format_func=lambda i: names[i])
#uc = cp.deepcopy(usecases[idx])
uc = usecases[idx]

# Editing the selected usecase:
st.subheader(f"Editando: {uc.get('name')}")

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
uc['authors'] = st_tags(label='Autor:', value=uc.get('authors', ''))
uc["countries"] = st.multiselect("Countries", COUNTRY_OPTIONS, default=uc.get("countries", []))
uc['email'] = st_tags(label='Email de contato:', value=uc.get('email', ''))
uc["type"] = st.multiselect("Type", TYPE_OPTIONS, default=uc.get("type", []))
uc["topics"] = st.multiselect("Topics", TOPIC_OPTIONS, default=uc.get("topics", []))
uc['tags'] = st_tags(label='Tags:', value=uc.get('tags', ''))
uc["url_source"] = st.text_input("Código fonte:", uc.get("url_source", ""))
uc["url_image"] = st.text_input("Link para imagem:", uc.get("url_image", ""))
uc["comment"] = st.text_area("Comentários internos:", uc.get('comment', ''), height=200)

# Automatic fields:
#uc["record_date"]


# Datasets
st.markdown("### Datasets")
rm_dataset_btn = []
for i, ds in enumerate(uc.get("datasets", [])):
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
        def rm_dataset():
            uc['datasets'].pop(i)
        rm_dataset_btn.append(rm_dataset)
        st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=rm_dataset_btn[i])


# Option to add new dataset
st.button("➕ Adicionar conjunto de dados",
          on_click=(lambda: uc['datasets'].append({"data_name": "", "data_institution": "", "data_url": "", "data_periodical": None}))
          )
    

# Save
if st.button("💾 Save changes"):
    Path(DATA_FILE).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    st.success("Changes saved successfully!")

