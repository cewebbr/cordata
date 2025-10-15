import requests
import json
import streamlit as st
from pathlib import Path
from datetime import datetime

import config as cf


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


@st.dialog('Carregar dados do Github')
def load_from_github():
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados, sendo substituídos pelos do Github. Deseja continuar?')
    if st.button('Confirmar'):
        data = download_data('https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json')
        save_data(data)
        st.session_state['idx_init'] = None
        st.rerun()


def save_data(data, path=cf.TEMP_FILE):
    """
    Save `data` (dict) to `path` (str).
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def load_data(path):
    """
    Load JSON from file at `path` (str).
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))


@st.dialog('Limpar a base')
def erase_usecases():
    st.write('ATENÇÃO! Todos os casos de uso atualmente cadastrados neste app serão apagados. Deseja continuar?')
    if st.button('Confirmar'):
        data = load_data(cf.EMPTY_FILE)
        save_data(data)
        st.rerun()


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
    dataset = load_data(cf.DATASET_MODEL)
    datasets.append(dataset)
    save_data(data)


@st.dialog('Adicionar novo caso')
def add_new_case(data):
    """
    Create a new usecase, add it to dataset and
    show it for edition.
    """
    # Ask for new usecase name:
    name = st.text_input("Nome:")
    if st.button("🚀 Criar!"):
        # Create new usecase:
        uc = load_data(cf.ENTRY_MODEL)
        uc['name'] = name
        uc['record_date'] = datetime.today().strftime('%Y-%m-%d')
        # Insert in dataset:
        usecases = data["data"]
        usecases.insert(0, uc)
        save_data(data, cf.TEMP_FILE)
        # Set to show it:
        st.session_state['idx_init'] = 0
        st.rerun()


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
    st.write('Todas as informações a respeito deste caso de uso serão perdidas.')
    if st.button('Confirmar'):
        usecases = data["data"]
        usecases.pop(idx)
        save_data(data)
        st.rerun()