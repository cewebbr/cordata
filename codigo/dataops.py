# CRUD operations on data in storage (HD)
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

import requests
import json
import streamlit as st
from pathlib import Path
from datetime import datetime
from copy import deepcopy

import config as cf
import auxiliar as aux


###############################################
### Auxiliary functions for data operations ###
###############################################

def mun2uf(mun_list):
    """
    List the federative units mentioned in a list of 
    municipalities `mun_list` (list of str).

    Example input:  ['Autazes (AM)', 'Fonte Boa (AM)', 'Melgaço (PA)']
    Example output: ['AM', 'PA']
    """
    
    # Forward None:
    if mun_list == None:
        return None
    # Translate municipalities to UFs:
    uf_list = list(set([m[-3:-1] for m in mun_list]))
    return uf_list


def std_data(data):
    """
    Standardize data in place.
    """
    usecases = data['data']
    # Loop over usecases:
    for uc in usecases:
        # Set other empty information descriptions to None:
        for k in ['url', 'description', 'url_source', 'comment']:
            if uc[k] == "":
                uc[k] = None
        for ds in uc['datasets']:
            for k in ['data_name', 'data_institution', 'data_url']:
                if ds[k] == "":
                    ds[k] = None
            # Set dataset url to None (checked that works better on frontend):
            if ds['data_url'] in {'http://', 'https://'}:
                ds[k] = None            
        for k in ['authors', 'email', 'countries', 'fed_units', 'municipalities', 'type', 'topics', 'tags']:
            if uc[k] == []:
                uc[k] = None
        # Set country as Brasil and UFs from municipalities for more granular cases:
        if uc['geo_level'] == 'Municípios':
            uc['fed_units'] = mun2uf(uc['municipalities'])
        if uc['geo_level'] in {'Unidades federativas', 'Municípios'}:
            uc['countries'] = ['Brasil']
        # Set empty links to https:// to avoid (possible) frontend error:
        for k in ['url', 'url_source']:
            if uc[k] == None:
                uc[k] = 'https://'


def make_derived_data(data):
    """
    Compute data fields given others:
    - Translate type, topics and countries;
    - Assign author IDs for CGU (FAKE FOR NOW!)
    """
    # Hard-coded:
    fields2translate = [('type', 'type_es'), ('topics', 'topics_es'), ('countries', 'countries_es')]
    translate = aux.load_translations()

    # Loop over usecases:
    usecases = data['data']
    for uc in usecases:
        # Translate (loop over fields requiring translation):
        for ptbr, es in fields2translate:
            if uc[ptbr] != None:
                # Loop over items in list:
                translations = []
                for entry in uc[ptbr]:
                    translations.append(translate[entry])
                # Assign translations to key:
                uc[es] = translations
            else:
                uc[es] = None
        # Lookup author IDs from CGU compatibility (FAKE FOR NOW!):
        if uc['authors'] != None:
            uc['authors_id'] = [None] * len(uc['authors'])
        else:
            uc['authors_id'] = None


def today():
    """
    Returns a string with the current date in the
    YYYY-MM-DD format.
    """
    return datetime.today().strftime('%Y-%m-%d')

#########################################
### Operations on all data on storage ###
#########################################

def download_data(url):
    """
    Download CORDATA data from an `url` (str) address pointing to a 
    JSON file.
    """
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        content = response.content.decode()
        data = json.loads(content)
        return data
    else:
        st.error(f'Falha no carregamento dos dados (status code {status})')
    #aux.log('Ran download_data')


@st.dialog('Carregar dados do Github')
def load_from_github():
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados, sendo substituídos pelos do Github. Deseja continuar?')
    if st.button('Confirmar'):
        aux.log('Downloading data from github')
        data = download_data('https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json')
        st.session_state['data'] = deepcopy(data)
        save_data(data)
        st.session_state['usecase_selectbox'] = None
        st.rerun()


@st.dialog('Subir dados locais')
def upload_data():
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados, sendo substituídos pelos do arquivo selecionado.')
    uploaded_file = st.file_uploader(label='Escolha o arquivo para carregar', type='json')
    if uploaded_file is not None:
        aux.log('Uploading local data')
        data = json.load(uploaded_file)
        st.session_state['data'] = deepcopy(data)
        save_data(data)
        st.session_state['usecase_selectbox'] = None
        st.rerun()


def save_data(data, path=cf.TEMP_FILE):
    """
    Save `data` (dict) to `path` (str) if edit controls
    are enabled.
    """
    if st.session_state['allow_edit'] == True:
        # Standardize data and derive other fields:
        std_data(data)
        make_derived_data(data)
        # Set update date to now:
        data['metadata']['last_update'] = today()
        # Save data:
        with open(path, 'w') as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        aux.log(f'Saved data to {path}')


def load_data(path):
    """
    Load JSON from file at `path` (str).
    """
    aux.log('Load data from {:}'.format(path))
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.dialog('Limpar a base')
def erase_usecases():
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados. Deseja continuar?')
    if st.button('Confirmar'):
        aux.log('Erasing all data')
        data = load_data(cf.EMPTY_FILE)
        st.session_state['data'] = deepcopy(data)
        save_data(data)
        st.rerun()


######################################
### Operations to a single usecase ###
######################################

@st.dialog('Adicionar novo caso')
def add_usecase(data):
    """
    Create a new usecase, add it to dataset and
    show it for edition.
    """

    # Ask for new usecase name:
    name = st.text_input("Nome:")
    
    if st.button("🚀 Criar!"):
        aux.log(f'Adding new usecase: {name}')
        
        # Create new usecase:
        uc = load_data(cf.ENTRY_MODEL)
        uc['name'] = name
        uc['record_date']   = today()
        uc['modified_date'] = today()
        uc['hash_id'] = aux.hash_string(uc['name'] + uc['record_date'])
        
        # Insert in dataset:
        data = load_data(cf.TEMP_FILE)
        usecases = data['data']
        usecases.insert(0, uc)
        st.session_state['data'] = deepcopy(data)
        save_data(data)
        
        # Set to show it:
        st.session_state['usecase_selectbox'] = uc['hash_id']
        st.rerun()
    

def update_usecase(uc: dict, data:dict):
    """
    Update the information about an usecase in `data` (dict)
    to the new information provided `uc` (dict). The `data` 
    is saved to the file.  
    """        
    
    aux.log(f"Saving usecase: {uc['name']}")

    # Load current data saved on file:
    data = load_data(cf.TEMP_FILE)

    # Set last modified date:
    uc['modified_date'] = today()

    # Copy to the usecase position in list:
    idx = aux.get_usecase_pos(data['data'], uc['hash_id'])
    data['data'][idx] = uc # Deepcopy not required since we are saving to a file.
    st.session_state['data'] = deepcopy(data)

    # Save to file:
    save_data(data)


@st.dialog('Remover caso de uso')
def remove_usecase(data, hash_id):
    """
    Remove usecase from our data.

    Parameters
    ----------
    data : dict
            The whole information about the usecases, including
            the metadata (e.g. last_update).
    hash_id : int
        Usecase ID.
    """
    st.write('Todas as informações a respeito deste caso de uso serão perdidas.')
    
    if st.button('Confirmar'):
        aux.log(f'Removing usecase: {hash_id}')

        # Load current data saved on file:
        data = load_data(cf.TEMP_FILE)

        # Remove target usecase:
        usecases = data['data']
        idx = aux.get_usecase_pos(usecases, hash_id)
        usecases.pop(idx)
        
        # Save data:
        st.session_state['data'] = deepcopy(data)
        save_data(data)
        
        # Reset usecase selection:
        st.session_state['usecase_selectbox'] = None
        st.rerun()


@st.dialog('Desfazer modificações')
def reset_usecase(idx):
    """
    Erase records of widgets' states used to edit the usecase.
    """
    st.write('As edições neste caso de uso serão substituídas pelas informações salvas anteriormente. Deseja continuar?')
    if st.button('Confirmar'):
        # Load saved usecase data:
        data = load_data(cf.TEMP_FILE)
        uc = data['data'][idx]
        st.session_state['usecase_status'] = uc.get('status', 'Em revisão')
        usecase_widgets = list(filter(lambda x: x[:8] == 'usecase_', st.session_state.keys()))
        st.rerun()
