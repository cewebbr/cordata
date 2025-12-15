# Code for editing the metadata of a single usecase.
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
import streamlit as st
from streamlit_tags import st_tags
from copy import deepcopy

# Internal imports:
import config as cf
import dataops as io
import auxiliar as aux


#############################################
### Operations on current usecase dataset ###
#############################################

def append_dataset(datasets: list):
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
    dataset = io.load_data(cf.DATASET_MODEL)
    datasets.append(dataset)


def gen_rm_dataset(i: int) -> callable:
    """
    Return a function that receives a usecase as input  
    and removes the dataset in position `i` (int) from
    `uc['datasets']`.
    """
    def rm_dataset(uc):
        uc['datasets'].pop(i)
        set_datasets_widgets(uc)
    return rm_dataset


###########################################
### Functions for managing form widgets ###
###########################################

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


#######################
### Dataset editing ###
#######################

def dataset_edit_form(ds: dict, i: int, hash_id: int):
    """
    Render the dataset editing form and make in-place changes 
    to the fields in dataset `ds` (dict) according to the 
    widgets. 

    Parameters
    ----------
    ds : dict
        Metadata about a dataset used by an usecase.
    i : int
        Position of the dataset in the list of datasets
        used by the usecase.
    hash_id : int
        ID of the associated usecase.
    """    

    # Shorthand for session memory:
    ds_v0 = st.session_state['ds_defaults']

    # Edit fields:

    for dkey in ['data_name', 'data_institution', 'data_url']:
        ds[dkey] = st.text_input(label=cf.WIDGET_LABEL[dkey], value=ds_v0[dkey], key=aux.gen_uckey(hash_id, dkey, i), help=cf.WIDGET_HELP[dkey])

    dkey = 'data_license'
    ds[dkey] = st.selectbox(label=cf.WIDGET_LABEL[dkey], options=cf.LICENSE_OPTIONS, key=aux.gen_uckey(hash_id, dkey, i), 
                            index=aux.nindex(cf.LICENSE_OPTIONS, ds_v0[dkey]), help=cf.WIDGET_HELP[dkey])

    dkey = 'data_format'
    ds[dkey] = st.multiselect(label=cf.WIDGET_LABEL[dkey], options=st.session_state['sel_opts'][dkey], 
                            default=[], key=aux.gen_uckey(hash_id, dkey, i), help=cf.WIDGET_HELP[dkey])

    dkey = 'data_periodical'
    ds[dkey] = st.radio(label=cf.WIDGET_LABEL[dkey], options=[True, False, None],
                        index=[True, False, None].index(ds_v0[dkey]), 
                        key=aux.gen_uckey(hash_id, dkey, i), horizontal=True, 
                        format_func=(lambda x: {True:'Sim', False:'Não', None:'(vazio)'}[x]), help=cf.WIDGET_HELP[dkey])



#######################
### Usecase editing ###
#######################

def usecase_edit_form(uc: dict):
    """
    Render the usecase editing form and make in-place changes 
    to the fields in usecase `uc` (dict) according to the 
    widgets. 
    """

    # Use shorthands for session memory:
    uc_v0 = st.session_state['uc_defaults']
    hash_id = uc['hash_id']

    # Display the usecase name as header:
    st.subheader(f"{uc.get('name')}")

    ### Mandatory fields ###
    for uckey in ['name', 'url', 'url_archive']:
        uc[uckey] = st.text_input(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey), help=cf.WIDGET_HELP[uckey])

    ### Optional fields ###
    uckey = 'description'
    uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey), height=200, help=cf.WIDGET_HELP[uckey])
    # Data de publicação:
    uckey = 'known_pub'
    known_pub_date = st.checkbox(label=cf.WIDGET_LABEL[uckey], value=False, key=aux.gen_uckey(hash_id, uckey), help=cf.WIDGET_HELP[uckey])
    uckey = 'pub_date'
    if known_pub_date == True:
        pub_date = st.date_input(label=cf.WIDGET_LABEL[uckey], value=aux.read_date(uc_v0[uckey]), key=aux.gen_uckey(hash_id, uckey), 
                                format="DD/MM/YYYY", help=cf.WIDGET_HELP[uckey])            
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
                horizontal=True, format_func=(lambda x: aux.none_fmt[x]), help=cf.WIDGET_HELP[uckey])
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
                                default=[], key=aux.gen_uckey(hash_id, uckey), help=cf.WIDGET_HELP[uckey])
    uckey = 'tags'                                     # Default based on usecase V
    uc[uckey] = st_tags(label=cf.WIDGET_LABEL[uckey], value=aux.tags_fmt(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey))
    for uckey in ['url_source', 'url_image']:
        uc[uckey] = st.text_input(label=cf.WIDGET_LABEL[uckey], value=uc_v0[uckey], key=aux.gen_uckey(hash_id, uckey), help=cf.WIDGET_HELP[uckey])
    st.image(uc['url_image'])

    ### Datasets ###

    st.markdown("#### Conjuntos de dados")
    datasets = uc['datasets']

    #rm_dataset_btn = []
    for i, ds in enumerate(datasets):
        with st.expander(f"Dataset {i+1}"):

            # Run the dataset edit form:
            dataset_edit_form(ds, i, hash_id)

            # Option to remove this dataset:
            st.button("❌  Remover", key=f'rm-dataset_{i}', on_click=gen_rm_dataset(i), args=(uc,))

    # Option to add new dataset        
    st.button("➕ Adicionar conjunto de dados", on_click=append_dataset, args=(datasets,))

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
    uc[uckey] = st.text_area(label=cf.WIDGET_LABEL[uckey], value=uc.get(uckey, uc_v0[uckey]), key=aux.gen_uckey(hash_id, uckey), height=200, help=cf.WIDGET_HELP[uckey])
    status_list = ['status_published', 'status_review']
    status_cols = st.columns(len(status_list))
    for i, uckey in enumerate(status_list):
        with status_cols[i]:
            uc[uckey] = st.radio(cf.WIDGET_LABEL[uckey], options=cf.STATUS_OPTIONS, horizontal=True,
                        index=cf.STATUS_OPTIONS.index(uc.get(uckey, uc_v0[uckey])), key=aux.gen_uckey(hash_id, uckey),
                        format_func=(lambda x: cf.STATUS_DISPLAY[uckey][x]), help=cf.WIDGET_HELP[uckey])
            

def usecase_page(hash_id: int, data: dict):
    """
    Run the main app page (reading/editing a single usecase
    specified by its hash ID).

    Parameters
    ----------
    hash_id : int
        The ID of the usecase.
    data : dict
        The whole CORDATA data, including its metadata. The 
        usecases should be stored in a list under the key 
        'data'.
    """
    
    # An usecase was selected:
    if hash_id != None:
        
        # Copy usecase to memory if it is a new selection:
        if st.session_state['uc'] == None or st.session_state['uc']['hash_id'] != hash_id or st.session_state['prev_empty_sel']:
            st.session_state['uc'] = deepcopy(aux.select_usecase_by_id(data, hash_id))
            set_uc_widgets(st.session_state['uc'])
            aux.log(f"Changed to usecase: {st.session_state['uc']['name']}")
        st.session_state['prev_empty_sel'] = False
        
        # Edit usecase:
        usecase_edit_form(st.session_state['uc'])

        # Usecase record operations:
        aux.html('<hr>')
        save_col, remove_col, reset_col = st.columns(3)
        
        # Save button:
        with save_col:
            if st.button("💾 Salvar"):
                io.update_usecase(st.session_state['uc'], data)
                st.success("Dados salvos com sucesso!")
        
        # Remove button:
        with remove_col:
            st.button("❌  Remover caso de uso", on_click=io.remove_usecase, args=(data, hash_id))

    # No usecase selected:
    else:
        st.session_state['prev_empty_sel'] = True