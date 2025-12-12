#!/usr/bin/env -S="streamlit run"
# http://localhost:8501
# Main code (app)
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
from pathlib import Path

# Internal imports:
import dataops as io
import auxiliar as aux
import controls as ct
import init
import editor as ed


# Logging:
#aux.log('Started app run')

# Move current working directory to the script’s directory:
os.chdir(Path(__file__).parent)


############
### Init ###
############

# Initialize session state (permanent variables through successive code runs):
init.init_session()
# Create shorthand for data in memory:
data  = st.session_state['data']


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

# Baixar dados:
st.sidebar.download_button('⬇️ Baixar dados', json.dumps(data, indent=1, ensure_ascii=False), file_name='usecases_current.json')
aux.html('<hr>', sidebar=True)

# Select a usecase to view/edit:
hash_id = ct.usecase_selector(data)

# Add new usecase:
st.sidebar.button('➕ Adicionar novo caso', on_click=io.add_usecase, args=(data,))


######################
### Usecase editor ###
######################        

ed.usecase_page(hash_id, data)


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
#aux.log(f'hash_id = {hash_id}')