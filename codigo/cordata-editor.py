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

def tags_fmt(x):
    if x == None:
        return []
    return x

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
# Load usecase default values:
if 'uc_defaults' not in st.session_state:
    st.session_state['uc_defaults'] = io.load_data(cf.ENTRY_MODEL)
uc_v0 = st.session_state['uc_defaults']

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
    for uckey in ['name', 'url']:
        uc[uckey] = st.text_input(label=cf.WIDGET_LABEL[uckey], value=uc.get(uckey, uc_v0[uckey]), key=aux.gen_uckey(uckey))

    ### Optional fields ###
    uckey = 'description'
    #uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc.get(uckey, uc_v0[uckey]), key=aux.gen_uckey(uckey), height=200)
    uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc.get(uckey, uc_v0[uckey]), height=200)
    # Data de publicação:
    known_pub_date = st.checkbox("Data de publicação conhecida", value=(uc['pub_date'] != None))
    if known_pub_date == True:
        pub_date = st.date_input("Data de publicação:", aux.read_date(uc.get("pub_date")), format="DD/MM/YYYY", key='usecase_pub_date')            
        uc["pub_date"] = None if pub_date == None else pub_date.strftime("%m/%Y")
    else:
        uc["pub_date"] = None
    
    uckey = 'authors'
    #uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=tags_fmt(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(uckey))
    uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=tags_fmt(uc.get(uckey, uc_v0[uckey])))
    # Nível de cobertura geográfica:
    uckey = 'geo_level'
    uc[uckey] = st.radio(label=cf.WIDGET_LABEL[uckey],
                options=cf.GEOLEVEL_OPTIONS,
                index=cf.GEOLEVEL_OPTIONS.index(uc.get(uckey, uc_v0[uckey])),
                horizontal=True, format_func=(lambda x: none_fmt[x]))
    #            horizontal=True, format_func=(lambda x: none_fmt[x]), key=aux.gen_uckey(uckey))
    geolevel = uc[uckey]
    if geolevel in cf.GEOLEVEL_KEYS.keys():
        gkey = cf.GEOLEVEL_KEYS[geolevel]
        uc[gkey] = st.multiselect(geolevel + ':', st.session_state['localities'][gkey], default=uc.get(gkey, uc_v0[gkey]), key=aux.gen_uckey(gkey))

    #uc['email'] = st_tags(label='Email de contato:', value=tags_fmt(uc.get('email', [])), key='usecase_email')
    uc['email'] = st_tags(label='Email de contato:', value=tags_fmt(uc.get('email', [])))
    uc["type"] = st.multiselect("Tipo de caso:", cf.TYPE_OPTIONS, default=uc.get("type", []), key='usecase_type')
    uc["topics"] = st.multiselect("Temas tratados no caso:", cf.TOPIC_OPTIONS, default=uc.get("topics", []), key='usecase_topics')
    #uc['tags'] = st_tags(label='Tags:', value=tags_fmt(uc.get('tags', [])), key='usecase_tags')
    uc['tags'] = st_tags(label='Tags:', value=tags_fmt(uc.get('tags', [])))
    uc["url_source"] = st.text_input("Código fonte:", uc.get("url_source", ""), key='usecase_url_source')
    uc["url_image"] = st.text_input("Link para imagem:", uc.get("url_image", ""), key='usecase_url_image')
    st.image(uc["url_image"])

    ### Datasets ###

    st.markdown("#### Conjuntos de dados")
    datasets = uc['datasets']

    rm_dataset_btn = []
    for i, ds in enumerate(datasets):
        with st.expander(f"Dataset {i+1}"):
            # Dataset metadata:
            ds["data_name"] = st.text_input("Nome do conjunto:", ds.get("data_name", ""), key=f"usecase_data_name_{i}")
            ds["data_institution"] = st.text_input("Instituição responsável:", ds.get("data_institution", ""), key=f"usecase_data_inst_{i}")
            ds["data_url"] = st.text_input("Link:", ds.get("data_url", ""), key=f"usecase_data_url_{i}")            
            ds['data_license'] = st.selectbox('Licença:', options=cf.LICENSE_OPTIONS, key=f"usecase_data_license_{i}", 
                                              index=aux.nindex(cf.LICENSE_OPTIONS, ds.get("data_license")))
            ds["data_periodical"] = st.radio("Uso periódico?",
                options=[True, False, None],
                index=[True, False, None].index(ds.get("data_periodical")),
                horizontal=True,
                format_func=(lambda x: {True:'Sim', False:'Não', None:'(vazio)'}[x]),
                key=f"usecase_data_periodical_{i}"
            )
            # Option to remove this dataset:
            def rm_dataset(index=i):
                uc['datasets'].pop(index)
                io.save_data(data)
            rm_dataset_btn.append(rm_dataset)
            st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=rm_dataset_btn[i])

    # Option to add new dataset        
    st.button("➕ Adicionar conjunto de dados", on_click=io.append_dataset, args=(data, datasets))

    ### Usecase internal data ###

    st.markdown("#### Registros internos")
    id_col, record_col, modified_col = st.columns(3)
    with id_col:
        st.markdown('**ID:** {:}'.format(uc['hash_id']))
    with record_col:
        st.markdown('**Data de registro:** {:}'.format(uc.get('record_date', '(vazio)')))
    with modified_col:
        st.markdown('**Última modificação:** {:}'.format(uc.get('modified_date', '(vazio)')))
    uc["comment"] = st.text_area("Comentários internos:", uc.get('comment', ''), height=200)
    uc["status"] = st.radio("Status do caso:", options=cf.STATUS_OPTIONS, horizontal=True,
                            index=cf.STATUS_OPTIONS.index(uc.get("status", "Em revisão")))

    ### Usecase operations ###

    aux.html('<hr>')
    save_col, remove_col, reset_col = st.columns(3)
    # Save button:
    with save_col:
        if st.button("💾 Salvar"):
            io.save_data(data)
            st.success("Dados salvos com sucesso!")
    # Remove button:
    with remove_col:
        st.button("❌  Remover caso de uso", on_click=io.remove_usecase, args=(data, idx))
    # Reset button:
    with reset_col:
        st.button("🔄 Desfazer edições", on_click=io.reset_usecase, args=(idx,))


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

aux.html('<hr>', sidebar=True)
st.sidebar.markdown('**\# casos cadastrados:** {:}'.format(len(usecases)))
st.sidebar.markdown('**Última atualização**: {:}'.format(data['metadata']['last_update']))

print('\n>> Run!')
