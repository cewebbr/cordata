import requests
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

import config as cf
import auxiliar as aux

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
        data = download_data('https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json')
        save_data(data)
        st.session_state['idx_init'] = None
        st.rerun()


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
        # Set country as Brasil for more granular cases:
        if uc['geo_level'] in {'Unidades federativas', 'Municípios'}:
            uc['countries'] = ['Brasil']
        # Set empty links to https:// to avoid (possible) frontend error:
        for k in ['url', 'url_source']:
            if uc[k] == None:
                uc[k] = 'https://'


def save_data(data, path=cf.TEMP_FILE):
    """
    Save `data` (dict) to `path` (str) if edit controls
    are enabled.
    """
    if st.session_state['login'] == True:
        # Standardize data:
        std_data(data)
        # Set update date to now:
        data['metadata']['last_update'] = datetime.today().strftime('%Y-%m-%d')
        # Save data:
        with open(path, 'w') as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        #aux.log('Saved data to {:}'.format(path))


def load_data(path):
    """
    Load JSON from file at `path` (str).
    """
    #aux.log('Will load data from {:}'.format(path))
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.dialog('Limpar a base')
def erase_usecases():
    aux.log('Entered erase_usecases dialog')
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados. Deseja continuar?')
    if st.button('Confirmar'):
        aux.log('Entered erase_usecases confirm area')
        data = load_data(cf.EMPTY_FILE)
        save_data(data)
        st.rerun()
    aux.log('Finished erase_usecases dialog')


def append_dataset(data, datasets):
    """
    Add a new dataset to those used by a usecase.

    Parameters
    ----------
    data : dict
        The whole information about the usecases, including
        the metadata (e.g. last_update).
    datasets : list
        List of datasets used by the usecase. It must be a 
        reference to a list inside a usecase inside `data`.
    """
    #aux.log('Will append dataset to usecase')
    dataset = load_data(cf.DATASET_MODEL)
    datasets.append(dataset)
    save_data(data)


@st.dialog('Adicionar novo caso')
def add_new_case(data):
    """
    Create a new usecase, add it to dataset and
    show it for edition.
    """
    aux.log('Entered add_new_case dialog')
    # Ask for new usecase name:
    name = st.text_input("Nome:")
    if st.button("🚀 Criar!"):
        aux.log('Entered add_new_case confirm area')
        # Create new usecase:
        uc = load_data(cf.ENTRY_MODEL)
        uc['name'] = name
        uc['record_date'] = datetime.today().strftime('%Y-%m-%d')
        uc['hash_id'] = aux.hash_string(uc['name'] + uc['record_date'])
        # Insert in dataset:
        usecases = data["data"]
        usecases.insert(0, uc)
        save_data(data, cf.TEMP_FILE)
        # Set to show it:
        st.session_state['idx_init'] = 0
        st.rerun()
    aux.log('Finished add_new_case dialog')

@st.dialog('Remover caso de uso')
def remove_usecase(data, idx):
    """
    Remove usecase from our data.

    Parameters
    ----------
    data : dict
            The whole information about the usecases, including
            the metadata (e.g. last_update).
    idx : int
        Position in list of usecases `data['data]`.
    """
    aux.log('Entered remove_usecase dialog')
    st.write('Todas as informações a respeito deste caso de uso serão perdidas.')
    if st.button('Confirmar'):
        aux.log('Entered remove_usecase confirm area')
        usecases = data["data"]
        usecases.pop(idx)
        save_data(data)
        st.session_state['idx_init'] = None
        st.rerun()
    aux.log('Finished remove_usecase dialog')

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