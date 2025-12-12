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


###############################################
### Operations on current usecase in memory ###
###############################################

def append_dataset(datasets):
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


def gen_rm_dataset(i: int):
    """
    Return a function that receives a usecase as input  
    and removes the dataset in position `i` (int) from
    `uc['datasets']`.
    """
    def rm_dataset(uc):
        uc['datasets'].pop(i)
        set_datasets_widgets(uc)
    return rm_dataset


def set_ds_widgets(hash_id: int, ds: dict, i: int):
    """
    Set the value of the widgets for editing the dataset 
    `i` (int) of a usecase to the values in the provided 
    dataset `ds` (dict).    
    """

    # Load default values:
    ds_v0 = st.session_state['ds_defaults']

    for dkey in ds.keys():
        if dkey == 'data_format':
            st.session_state[aux.gen_uckey(hash_id, dkey, i)] = deepcopy(ds.get(dkey, []))
        else:
            st.session_state[aux.gen_uckey(hash_id, dkey, i)] = deepcopy(ds.get(dkey, ds_v0[dkey]))


def set_datasets_widgets(uc: dict):
    """
    Set the values of the widgets of all datasets in usecase
    `uc` (dict). 
    """
    # Loop over datasets:
    for i, ds in enumerate(uc['datasets']):
        set_ds_widgets(uc['hash_id'], ds, i)


def set_uc_widgets(uc: dict):
    """
    Set the value of the widgets for editing the usecase 
    to the values in the provided usecase `uc` (dict).
    """

    # Hard-coded:
    tags = {'authors', 'email', 'tags'}
    multiselect = {'type', 'topics', 'countries', 'fed_units', 'municipalities'}
    # Load default values:
    uc_v0 = st.session_state['uc_defaults']

    # Loop over usecase properties:
    for uckey in uc.keys():
        # Multiselects:
        if uckey in multiselect:
            st.session_state[aux.gen_uckey(uc['hash_id'], uckey)] = deepcopy(aux.tags_fmt(uc.get(uckey, [])))
        # Tags:
        #elif uckey in tags:
        #    st.session_state[aux.gen_uckey(uc['hash_id'], uckey)] = deepcopy(tags_fmt(uc.get(uckey, uc_v0[uckey])))
        # Special cases:
        elif uckey == 'pub_date':
            st.session_state[aux.gen_uckey(uc['hash_id'], uckey)] = deepcopy(aux.read_date(uc.get(uckey, uc_v0[uckey])))
        # Datasets:
        elif uckey == 'datasets':
            set_datasets_widgets(uc)
        # Normal properties:
        else:
            st.session_state[aux.gen_uckey(uc['hash_id'], uckey)] = deepcopy(uc.get(uckey, uc_v0[uckey]))

    # Set widgets with no keys in usecase:
    uckey = 'known_pub'
    st.session_state[aux.gen_uckey(uc['hash_id'], uckey)] = (uc['pub_date'] != None)
