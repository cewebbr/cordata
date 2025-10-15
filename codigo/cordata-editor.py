#!/usr/bin/env -S="streamlit run"
# http://localhost:8501
# -*- coding: utf-8 -*-

"""
CORDATA EDITOR (Content Management System)
Copyright (C) 2025 Henrique Xavier
Contact: contato@henriquexavier.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# External imports:
import json
import streamlit as st
from streamlit_tags import st_tags
from datetime import datetime
from pathlib import Path
import os

# Internal imports:
import config as cf
import dataops as io
import auxiliar as aux

# Move current working directory to the script’s directory
os.chdir(Path(__file__).parent)


#################
### Functions ###
#################

# Display format for options including None:
none_fmt = aux.translate_dict({None:'(vazio)'})


############
### Init ###
############

# Initialization of session variables:
if 'idx_init' not in st.session_state:
    st.session_state['idx_init'] = None
# Load list of location names:
if 'localities' not in st.session_state:
    mun = aux.read_lines('data/municipios.csv')
    st.session_state['localities'] = {'countries': cf.COUNTRY_OPTIONS, 'fed_units': cf.UF_OPTIONS, 'municipalities': mun}

################
### Controls ###
################

# Sidebar header:
st.sidebar.image('img/logo-cordata.png', width=200)

# Replace local data with the one from the repo:
st.sidebar.button('🐙 Carregar do Github', on_click=io.load_from_github)

# Remove all data from the app:
st.sidebar.button('🗑️ Limpar a base', on_click=io.erase_usecases)

# Load local data:
data = io.load_data(cf.TEMP_FILE)
usecases = data["data"]

# Select usecase:
names = [uc['name'] for uc in usecases]
idx = st.sidebar.selectbox("Selecione o caso de uso:", range(len(usecases)), format_func=lambda i: names[i], 
                           index=st.session_state['idx_init'], on_change=io.save_data, kwargs={'data': data})

# Add new usecase:
st.sidebar.button('➕ Adicionar novo caso', on_click=io.add_new_case, args=(data,))


######################
### Usecase editor ###
######################

if idx != None:
    uc = usecases[idx]

    # Editing the selected usecase:
    st.subheader(f"{uc.get('name')}")

    ### Mandatory fields ###

    uc["name"] = st.text_input("Nome:", uc.get("name", ""))
    uc["url"] = st.text_input("Link:", uc.get("url", ""))

    ### Optional fields ###

    uc["description"] = st.text_area("Descrição:", uc.get('description', ''), height=200)
    # Data de publicação:
    known_pub_date = st.checkbox("Data de publicação conhecida", value=(uc['pub_date'] != None))
    if known_pub_date == True:
        pub_date = st.date_input("Data de publicação:", aux.read_date(uc.get("pub_date")), format="DD/MM/YYYY")            
        uc["pub_date"] = None if pub_date == None else pub_date.strftime("%m/%Y")
    else:
        uc["pub_date"] = None
    
    uc['authors'] = st_tags(label='Autor:', value=uc.get('authors', []))
    # Nível de cobertura geográfica:
    uc['geo_level'] = st.radio("Nível de cobertura geográfica:",
                options=cf.GEOLEVEL_OPTIONS,
                index=cf.GEOLEVEL_OPTIONS.index(uc.get("geo_level")),
                horizontal=True, format_func=(lambda x: none_fmt[x]))
    geolevel = uc['geo_level']
    if geolevel in cf.GEOLEVEL_KEYS.keys():
        gkey = cf.GEOLEVEL_KEYS[geolevel]
        uc[gkey] = st.multiselect(geolevel + ':', st.session_state['localities'][gkey], default=uc.get(gkey, []))

    uc['email'] = st_tags(label='Email de contato:', value=uc.get('email', []))
    uc["type"] = st.multiselect("Tipo de caso:", cf.TYPE_OPTIONS, default=uc.get("type", []))
    uc["topics"] = st.multiselect("Temas tratados no caso:", cf.TOPIC_OPTIONS, default=uc.get("topics", []))
    uc['tags'] = st_tags(label='Tags:', value=uc.get('tags', []))
    uc["url_source"] = st.text_input("Código fonte:", uc.get("url_source", ""))
    uc["url_image"] = st.text_input("Link para imagem:", uc.get("url_image", ""))
    uc["comment"] = st.text_area("Comentários internos:", uc.get('comment', ''), height=200)


    ### Datasets ###

    st.markdown("#### Conjuntos de dados")
    datasets = uc['datasets']

    rm_dataset_btn = []
    for i, ds in enumerate(datasets):
        with st.expander(f"Dataset {i+1}"):
            # Dataset metadata:
            ds["data_name"] = st.text_input("Nome do conjunto:", ds.get("data_name", ""), key=f"name_{i}")
            ds["data_institution"] = st.text_input("Instituição responsável:", ds.get("data_institution", ""), key=f"inst_{i}")
            ds["data_url"] = st.text_input("Link:", ds.get("data_url", ""), key=f"url_{i}")            
            ds['data_license'] = st.selectbox('Licença:', options=cf.LICENSE_OPTIONS, key=f"license_{i}", 
                                              index=aux.nindex(cf.LICENSE_OPTIONS, ds.get("data_license")))
            ds["data_periodical"] = st.radio("Uso periódico?",
                options=[True, False, None],
                index=[True, False, None].index(ds.get("data_periodical")),
                horizontal=True,
                format_func=(lambda x: {True:'Sim', False:'Não', None:'(vazio)'}[x]),
                key=f"periodical_{i}"
            )
            # Option to remove this dataset:
            def rm_dataset(index=i):
                uc['datasets'].pop(index)
                io.save_data(data)
            rm_dataset_btn.append(rm_dataset)
            st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=rm_dataset_btn[i])

    # Option to add new dataset        
    st.button("➕ Adicionar conjunto de dados", on_click=io.append_dataset, args=(data, datasets))


    ### Usecase final ###

    aux.html('<hr>')

    # Save button:
    if st.button("💾 Salvar"):
        io.save_data(data)
        st.success("Dados salvos com sucesso!")

    # Remove button:
    st.button("❌  Remover caso de uso", on_click=io.remove_usecase, args=(data, idx))



#################
### App final ###
#################

st.sidebar.download_button('⬇️ Baixar dados', json.dumps(data, indent=1, ensure_ascii=False), file_name='usecases_current.json')

    #uc['datasets'] = datasets
    #print(json.dumps(uc, indent=1))
    #print('')


########################
### Dataset metadata ###
########################

st.sidebar.write('\# casos cadastrados: {:}'.format(len(usecases)))


print('\n>> Run!')