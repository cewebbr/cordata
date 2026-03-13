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
import csv
import re

import config as cf
import auxiliar as aux


###############################################
### Auxiliary functions for data operations ###
###############################################

def mun2uf(mun_list: list) -> list:
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


def std_data(data: dict):
    """
    Standardize `data` (dict) in place.
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


def make_derived_data(data: dict):
    """
    Compute data fields given others, in place:
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


def today() -> str:
    """
    Returns a string with the current date in the
    YYYY-MM-DD format.
    """
    return datetime.today().strftime('%Y-%m-%d')


#########################################
### Operations on all data on storage ###
#########################################

def save_data(data: dict, path=cf.TEMP_FILE):
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


def load_data(path: str) -> dict:
    """
    Load JSON from file at `path` (str).
    """
    aux.log('Load data from {:}'.format(path))
    return json.loads(Path(path).read_text(encoding="utf-8"))


def serialize_data(data: dict) -> str:
    """
    Standardize and fill derived data (in place) and
    then serialize to string in JSON format.
    """
    # Standardize data and derive other fields:
    std_data(data)
    make_derived_data(data)
    # Serialize data:
    serial = json.dumps(data, indent=1, ensure_ascii=False)
    return serial


def get_json(url: str) -> dict:
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
        aux.log('Downloading data from github')
        data = get_json('https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json')
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


def insert_usecase(uc: dict):
    """
    Load data from HD, insert usecase `uc` (dict) 
    in position 0 and save data to HD.
    """
    data = load_data(cf.TEMP_FILE)
    usecases = data['data']
    usecases.insert(0, uc)
    st.session_state['data'] = deepcopy(data)
    save_data(data)


@st.dialog('Adicionar novo caso')
def add_usecase(data: dict):
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
        insert_usecase(uc)

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
def remove_usecase(data: dict, hash_id: int):
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
def reset_usecase(idx: int):
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


########################################################
### Methods for importing data from Dspace databases ###
########################################################

#@st.cache_data
def read_csv_into_records(filename, filter_func=None):
    """
    Read CSV file into a list of dicts. 

    Parameters
    ----------
    filename : str | Path
        Path to the CSV file.
    filter_func : executable
        A function that receives as input a CSV row 
        (dict) and returns True if the row is to be
        included in the output, and False otherwise.

    Returns
    -------
    data : list of dicts
        The data in the CSV file in the "list of 
        dicts" format. All data is returned as str.
    """
    
    # If no filtering is provided, return all rows:
    if filter_func == None:
        filter_func = (lambda x: True)        
    
    data = []
    with open(filename, 'r', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if filter_func(row):
                data.append(row)
    
    return data


def value_not_in_set(row: dict, key: str, values):
    """
    Return True if row[key] is NOT in values.
    Otherwise, return False.
    """
    if row[key] not in set(values):
        return True
    return False


def use_public_data(row, key='y_pred'):
    """
    Return True if item under `key` (str) is 1.
    Otherwise, return False.
    """
    if int(row[key]) == 1:
        return True
    return False

    
def normalize_name(name: str) -> str:
    """
    Standardize author names from SILVA, José dos Santos
    and José dos Santos SILVA to José dos Santos Silva.
    """

    # Hard-coded:
    LOWER_PARTICLES = {"da", "de", "do", "das", "dos", "e"}
    name = name.strip()

    # Remove stop:
    if name[-1] == '.':
        name = name[:-1]
    
    # Case 1: "SURNAME, Given names"
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
        name = f"{first} {last}"

    # Normalize capitalization
    parts = re.split(r"\s+", name)
    normalized = []

    for p in parts:
        pl = p.lower()
        if pl in LOWER_PARTICLES:
            normalized.append(pl)
        else:
            normalized.append(pl.capitalize())

    return " ".join(normalized)


def parse_authors(authors_str: str, sep=";"):
    """
    Parse a string with multiple authors into 
    a list of strings, with authors names in
    standard format.
    """
    authors = [a.strip() for a in authors_str.split(sep) if a.strip()]
    return [normalize_name(a) for a in authors]


def normalize_title(title):
    """
    Standardize the title of an academic work.
    """
    # Remove last period:
    if title[-1] == '.':
        title = title[:-1]
    # Remove space before colon:
    title = re.sub('( +: +)', ': ', title)
    # Avoid all caps titles:
    if title.isupper():
        title = title.capitalize()
    # Remove double spacings:
    title = ' '.join(title.split())
    
    return title


def normalize_url(url: str):
    """
    Function to normalize the academic work's URL.
    Currently just replaces 'http://' with 'https://'
    """
    return url.replace('http://', 'https://')

    
def normalize_date(date_str: str) -> str:
    """
    Normalize a date string to the format "MM/YYYY".

    The input string may represent a date in one of the following formats:
    - "YYYY"
    - "YYYY-MM"
    - "YYYY-MM-DD"

    Missing components are filled with "01". For example, a missing month
    defaults to January ("01").

    The function validates the resulting date using ``datetime.strptime``.

    Parameters
    ----------
    date_str : str
        A string representing a date in the formats "YYYY", "YYYY-MM",
        or "YYYY-MM-DD".

    Returns
    -------
    str
        A normalized date string in the format "MM/YYYY".

    Raises
    ------
    ValueError
        If the input string does not match one of the supported formats
        or if the resulting date is not valid.
    """
    
    parts = date_str.strip().split("-")

    if len(parts) == 1:          # YYYY
        parts += ["01"]
    elif len(parts) == 3:        # YYYY-MM-DD
        parts = parts[:-1]
    elif len(parts) != 2:
        raise ValueError("Invalid date format")

    # Validate the date:
    normalized = "/".join(parts[::-1])
    datetime.strptime(normalized, "%m/%Y")

    return normalized


def university_acronym(name: str) -> str:
    """
    Build a likely acronym for a Brazilian university name.

    The function generates an acronym by taking the first letter of each
    relevant word in the name while ignoring common Portuguese
    prepositions and conjunctions (e.g., "de", "da", "do", "dos", "das",
    "e"). The result is returned in uppercase.

    Parameters
    ----------
    name : str
        Full name of a university (e.g., "Universidade Federal de Pernambuco").

    Returns
    -------
    str
        The inferred acronym (e.g., "UFPE").
    """

    # Hard-coded:
    BRAZIL_STATES = {
    "acre": "AC",
    "alagoas": "AL",
    "amapá": "AP",
    "amazonas": "AM",
    "bahia": "BA",
    "ceará": "CE",
    "distrito federal": "DF",
    "espírito santo": "ES",
    "goiás": "GO",
    "maranhão": "MA",
    "mato grosso": "MT",
    "mato grosso do sul": "MS",
    "minas gerais": "MG",
    "pará": "PA",
    "paraíba": "PB",
    "paraná": "PR",
    "pernambuco": "PE",
    "piauí": "PI",
    "rio de janeiro": "RJ",
    "rio grande do norte": "RN",
    "rio grande do sul": "RS",
    "rondônia": "RO",
    "roraima": "RR",
    "santa catarina": "SC",
    "são paulo": "SP",
    "sergipe": "SE",
    "tocantins": "TO",
    }

    STOPWORDS = {"de", "da", "do", "dos", "das", "e"}

    normalized = name.lower().strip()

    # Check if the name ends with a state name (longest match first)
    for state in sorted(BRAZIL_STATES, key=len, reverse=True):
        if normalized.endswith(state):
            prefix = normalized[: -len(state)].strip()
            words = re.findall(r"[a-zà-ÿ]+", prefix)
            letters = [w[0] for w in words if w not in STOPWORDS]
            return "".join(letters).upper() + BRAZIL_STATES[state]

    # Default behavior if no state is detected
    words = re.findall(r"[a-zà-ÿ]+", normalized)
    letters = [w[0] for w in words if w not in STOPWORDS]

    return "".join(letters).upper()
    

def ensure_university_acronym(name: str) -> str:
    """
    Ensure a Brazilian university name ends with its acronym.

    If the last token of the string is an all-caps word (e.g., "UFRN"),
    the function assumes the acronym is already present and returns the
    input unchanged. Otherwise, it appends " - <ACRONYM>" to the name,
    where <ACRONYM> is inferred using ``university_acronym()``.

    Parameters
    ----------
    name : str
        Full name of a Brazilian university.

    Returns
    -------
    str
        The university name followed by its acronym if it was not
        already present.
    """
    name = name.strip()

    # Get last token ignoring trailing punctuation
    last_word = re.findall(r"[A-Za-z]+$", name)
    if last_word and last_word[0].isupper():
        return name

    acronym = university_acronym(name)
    return f"{name} - {acronym}"


def normalize_keywords(keywords, sep=';'):
    """
    Normalize a semicolon-separated list of keywords.

    The function converts the input string to lowercase, splits it on
    semicolons (';'), strips surrounding whitespace from each keyword,
    and returns the sorted resulting list.

    Parameters
    ----------
    keywords : str
        A string containing keywords separated by semicolons.

    Returns
    -------
    list[str]
        A list of normalized keywords.
    """
    
    if keywords == None or keywords == '':
        return None
        
    keywords = keywords.lower()
    keyword_list = keywords.split(sep)
    keyword_list = sorted(list(set([k.strip() for k in keyword_list if k.strip()])))
    return keyword_list


def collect_usecase_info(record, usecase_data_model):
    """
    ETL for an usecase metadata: from Dspace data to CORDATA.

    Parameters
    ----------
    record : dict
        Standardized fields present in Dspace. Expecting:
        'titulo', 'uri', 'resumo', 'data_publicacao', 
        'autoria', 'publicador', 'palavras_chave'.
    usecase_data_model : dict
        JSON structure used for CORDATA's usecases.

    Returns
    -------
    uc : dict
        The CORDATA's JSON structure filled with processed
        information drawn from `record`. Fields filled:
        'hash_id', 'name', 'url', 'description', 'pub_date', 'authors', 
        'type', 'tags', 'comment', 'record_date', 'modified_date'.
    """

    # Create a copy of the structure:
    uc = deepcopy(usecase_data_model)

    # Process fields:
    uc['record_date'] = today()
    uc['modified_date'] = today()
    uc['name'] = normalize_title(record['titulo'])
    uc['hash_id'] = aux.hash_string(uc['name'] + uc['record_date'])
    uc['url']  = normalize_url(record['uri'])
    uc['description'] = record['resumo']
    uc['pub_date'] = normalize_date(record['data_publicacao'])
    uc['authors'] = parse_authors(record['autoria']) + [ensure_university_acronym(record['publicador'])]
    uc['type'] = ['artigo científico ou publicação acadêmica']
    uc['tags'] = normalize_keywords(record['palavras_chave'])
    uc['comment'] = 'Pré-preenchido via Python a partir dos metadados do DSpace.'
    
    return uc


@st.dialog('Carrega caso de uso de DSpace')
def load_from_dspace():
    """
    Opens dialog that lists academic works in CSV databases
    extracted from DSpace. The user can load some metadata 
    about the work in the appropriate format. 
    """
    
    # List Dspace datasets:
    dspace_index = read_csv_into_records(Path(cf.DSPACE_DIR) / Path(cf.DSPACE_INDEX_FILE))
    dspace_dict   = aux.to_dict(dspace_index, 'filename', 'label')
    dspace_file   = st.selectbox(label='Selecione a fonte de trabalhos acadêmicos:', options=dspace_dict.keys(), 
                                index=None, key='dspace_selector', format_func=(lambda x: dspace_dict[x])) 
    if dspace_file != None:
        # List academic works in the selected Dspace dataset:
        current_ucs = aux.extract(st.session_state['data']['data'], 'url')
        dspace_data = read_csv_into_records(Path(cf.DSPACE_DIR) / Path(dspace_file), 
                                            lambda row: (normalize_url(row['uri']) not in current_ucs) and use_public_data(row))
        titles = aux.extract(dspace_data, 'titulo')
        title = st.selectbox(label='Selecione o trabalho acadêmico:', options=titles, index=None, key='academic_work_selector')
        
        if title != None:
            if st.button('➕ Carregar como caso de uso'):        
                # Parse data from the selected academic work:
                work_data = aux.select(dspace_data, 'titulo', title)[0]
                work_prep = collect_usecase_info(work_data, st.session_state['uc_defaults'])
                
                # Insert in dataset:
                insert_usecase(work_prep)

                # Set to show it:
                st.session_state['usecase_selectbox'] = work_prep['hash_id']
                st.rerun()

            


