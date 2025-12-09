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
import os
from streamlit_tags import st_tags
from datetime import datetime
from pathlib import Path
from copy import deepcopy

# Internal imports:
import config as cf
import dataops as io
import auxiliar as aux
import controls as ct

# Logging:
#aux.log('Started app run')

# Move current working directory to the script’s directory:
os.chdir(Path(__file__).parent)


############
### Init ###
############

### Constant data ###

# Load list of options for multiselect widgets:
if 'sel_opts' not in st.session_state:
    mun = aux.read_lines('data/municipios.csv')
    st.session_state['sel_opts'] = {'countries': cf.COUNTRY_OPTIONS, 
                                    'fed_units': cf.UF_OPTIONS, 
                                    'municipalities': mun,
                                    'type': cf.TYPE_OPTIONS,
                                    'topics': cf.TOPIC_OPTIONS,
                                    'data_format': cf.FORMAT_OPTIONS}
# Load usecase default values:
if 'uc_defaults' not in st.session_state:
    st.session_state['uc_defaults'] = io.load_data(cf.ENTRY_MODEL)
uc_v0 = st.session_state['uc_defaults']
# Load datasets default values:
if 'ds_defaults' not in st.session_state:
    st.session_state['ds_defaults'] = io.load_data(cf.DATASET_MODEL)
ds_v0 = st.session_state['ds_defaults']

### Controladores de edição ###

# Prepare usecase editing space:
if 'uc' not in st.session_state:
    st.session_state['uc'] = None
# Initialization of session variables:
if 'id_init' not in st.session_state:
    st.session_state['id_init'] = None
if 'usecase_selectbox' not in st.session_state:
    st.session_state['usecase_selectbox'] = None

# Login:
if 'allow_edit' not in st.session_state:
    aux.edit_control()


################
### Controls ###
################

# Sidebar header:
st.sidebar.image('img/logo-cordata.png', width=200)
# Replace local data with the one from the repo:
st.sidebar.button('🐙 Carregar do Github', on_click=io.load_from_github)
# Upload data from local:
st.sidebar.button('⬆️ Subir dados locais', on_click=io.upload_data)
# Remove all data from the app:
st.sidebar.button('🗑️ Limpar a base', on_click=io.erase_usecases)

# Load local data:
data = io.load_data(cf.TEMP_FILE)

# Baixar dados:
st.sidebar.download_button('⬇️ Baixar dados', json.dumps(data, indent=1, ensure_ascii=False), file_name='usecases_current.json')
aux.html('<hr>', sidebar=True)

# Select a usecase to view/edit:
hash_id = ct.usecase_selector(data)

# Add new usecase:
st.sidebar.button('➕ Adicionar novo caso', on_click=io.add_new_case, args=(data,))


######################
### Usecase editor ###
######################        

if hash_id != None:
    
    # Copy usecase to memory if it is a new selection:
    if st.session_state['uc'] == None or st.session_state['uc']['hash_id'] != hash_id:
        st.session_state['uc'] = deepcopy(aux.select_usecase_by_id(data, hash_id))
        io.set_uc_widgets(st.session_state['uc'])
        aux.log('Changed usecase')
    # Use a short name for the editing usecase:
    uc = st.session_state['uc']
    #uc = aux.select_usecase_by_id(data, hash_id) # Edita direto nos dados, não em cópia da memória.

    # Editing the selected usecase:
    st.subheader(f"{uc.get('name')}")

    ### Mandatory fields ###
    for uckey in ['name', 'url', 'url_archive']:
        uc[uckey] = st.text_input(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey))

    ### Optional fields ###
    uckey = 'description'
    uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey), height=200)
    # Data de publicação:
    uckey = 'known_pub'
    known_pub_date = st.checkbox(label=cf.WIDGET_LABEL[uckey], value=False, key=aux.gen_uckey(hash_id, uckey))
    uckey = 'pub_date'
    if known_pub_date == True:
        pub_date = st.date_input(label=cf.WIDGET_LABEL[uckey], value=aux.read_date(uc_v0[uckey]), key=aux.gen_uckey(hash_id, uckey), 
                                 format="DD/MM/YYYY")            
        uc[uckey] = None if pub_date == None else pub_date.strftime("%m/%Y")
    else:
        uc[uckey] = None
    
    uckey = 'authors'                                  # Default based on usecase V
    uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=aux.tags_fmt(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey))
    # Nível de cobertura geográfica:
    uckey = 'geo_level'
    uc[uckey] = st.radio(label=cf.WIDGET_LABEL[uckey],
                options=cf.GEOLEVEL_OPTIONS,
                index=cf.GEOLEVEL_OPTIONS.index(uc_v0[uckey]), key=aux.gen_uckey(hash_id, uckey),
                horizontal=True, format_func=(lambda x: aux.none_fmt[x]))
    geolevel = uc[uckey]
    # Seletor de localidades (se nível comportar):
    if geolevel in cf.GEOLEVEL_KEYS.keys():
        gkey = cf.GEOLEVEL_KEYS[geolevel]
        uc[gkey] = st.multiselect(label=geolevel + ':', options=st.session_state['sel_opts'][gkey], 
                                  default=uc_v0[gkey], key=aux.gen_uckey(hash_id, gkey))
        # Erase information of other previously set levels:
        for gk in cf.GEOLEVEL_KEYS.values():
            if gk != gkey:
                uc[gk] = None
    # Erase locality information if geo_level does not support:
    else:
        for gkey in cf.GEOLEVEL_KEYS.values():
            uc[gkey] = None

    uckey = 'email'                                    # Default based on usecase V
    uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=aux.tags_fmt(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey))
    for uckey in ['type', 'topics']:
        uc[uckey] = st.multiselect(label=cf.WIDGET_LABEL[uckey], options=st.session_state['sel_opts'][uckey], 
                                   default=[], key=aux.gen_uckey(hash_id, uckey))
    uckey = 'tags'                                     # Default based on usecase V
    uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=aux.tags_fmt(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey))
    for uckey in ['url_source', 'url_image']:
        uc[uckey] = st.text_input(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey))
    st.image(uc['url_image'])

    ### Datasets ###

    st.markdown("#### Conjuntos de dados")
    datasets = uc['datasets']

    #rm_dataset_btn = []
    for i, ds in enumerate(datasets):
        with st.expander(f"Dataset {i+1}"):
            # Dataset metadata:
            for dkey in ['data_name', 'data_institution', 'data_url']:
                ds[dkey] = st.text_input(label=cf.WIDGET_LABEL[dkey], value=ds_v0[dkey], key=aux.gen_uckey(hash_id, dkey, i))
            dkey = 'data_license'
            ds[dkey] = st.selectbox(label=cf.WIDGET_LABEL[dkey], options=cf.LICENSE_OPTIONS, key=aux.gen_uckey(hash_id, dkey, i), 
                                    index=aux.nindex(cf.LICENSE_OPTIONS, ds_v0[dkey]))
            dkey = 'data_format'
            ds[dkey] = st.multiselect(label=cf.WIDGET_LABEL[dkey], options=st.session_state['sel_opts'][dkey], 
                                      default=[], key=aux.gen_uckey(hash_id, dkey, i))
            dkey = 'data_periodical'
            ds[dkey] = st.radio(label=cf.WIDGET_LABEL[dkey], options=[True, False, None],
                                index=[True, False, None].index(ds_v0[dkey]), 
                                key=aux.gen_uckey(hash_id, dkey, i), horizontal=True, 
                                format_func=(lambda x: {True:'Sim', False:'Não', None:'(vazio)'}[x]))
            # Option to remove this dataset:
            #rm_dataset_btn.append(io.gen_rm_dataset(i))
            st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=io.gen_rm_dataset(i), args=(uc,))

    # Option to add new dataset        
    st.button("➕ Adicionar conjunto de dados", on_click=io.append_dataset, args=(data, datasets))

    ### Usecase internal data ###
    st.markdown("#### Registros internos")
    
    # Non editable fields:
    id_col, record_col, modified_col = st.columns(3)
    with id_col:
        st.markdown('**ID:** {:}'.format(uc['hash_id']))
    with record_col:
        st.markdown('**Data de registro:** {:}'.format(uc.get('record_date', '(vazio)')))
    with modified_col:
        st.markdown('**Última modificação:** {:}'.format(uc.get('modified_date', '(vazio)')))
    
    # Editable fields:
    uckey = 'comment'
    uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc.get(uckey, uc_v0[uckey]), key=aux.gen_uckey(hash_id, uckey), height=200)
    status_list = ['status_published', 'status_review']
    status_cols = st.columns(len(status_list))
    for i, uckey in enumerate(status_list):
        with status_cols[i]:
            uc[uckey] = st.radio(cf.WIDGET_LABEL[uckey], options=cf.STATUS_OPTIONS, horizontal=True,
                        index=cf.STATUS_OPTIONS.index(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey),
                        format_func=(lambda x: cf.STATUS_DISPLAY[uckey][x]))


    ### Usecase operations ###

    aux.html('<hr>')
    save_col, remove_col, reset_col = st.columns(3)
    # Save button:
    with save_col:
        if st.button("💾 Salvar"):
            aux.log('Entrou no Salvar caso de uso')
            io.update_usecase(uc, data)
            st.success("Dados salvos com sucesso!")
    # Remove button:
    with remove_col:
        st.button("❌  Remover caso de uso", on_click=io.remove_usecase, args=(data, hash_id))


########################
### Dataset metadata ###
########################

aux.html('<hr>', sidebar=True)
st.sidebar.markdown('**\# casos cadastrados:** {:}'.format(len(data['data'])))
st.sidebar.markdown('**Última atualização**: {:}'.format(data['metadata']['last_update']))
if st.session_state['allow_edit'] == True:
    st.sidebar.write('✏️ Edição permitida')

# Logging:
#aux.log('Finished app run')

print(uc['datasets'])