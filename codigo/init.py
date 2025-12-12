# Initialization of the app - Edit permission control & Session state init.
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

import streamlit as st
from copy import deepcopy

import auxiliar as aux
import config as cf
import dataops as io


@st.dialog('Controle de edição')
def edit_control():
    """
    Admin access dialog that asks for password to
    enable edit permission.
    """
    entry = st.text_input(label='Digite a senha:', type='password')
    if st.button('🚪 Entrar') == True:
        if entry == st.secrets['PWD']:
            aux.log('Log in: ALLOW EDIT')
            st.session_state['allow_edit'] = True
        else:
            aux.log('Log in: EDITING NOT ALLOWED')
            st.session_state['allow_edit'] = False
        st.rerun()


def init_session():
    """
    Initialize session state memory:
    * Load constant data
    * Load defaults
    * Set initial editing controllers
    * Show login dialog
    * Load data from storage 
    """
    
    # Log start of session:
    if 'session_start' not in st.session_state:
        aux.log('Starting session', prefix='[STT]')
        st.session_state['session_start'] = True

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

    # Load datasets default values:
    if 'ds_defaults' not in st.session_state:
        st.session_state['ds_defaults'] = io.load_data(cf.DATASET_MODEL)


    ### Controladores de edição ###

    # Prepare usecase editing space:
    if 'uc' not in st.session_state:
        st.session_state['uc'] = None
    # Initialization of session variables:
    if 'usecase_selectbox' not in st.session_state:
        st.session_state['usecase_selectbox'] = None
    # Select box state to prevent bug with hitting x in usecase selectbox:
    if 'prev_empty_sel' not in st.session_state:
        st.session_state['prev_empty_sel'] = True

    # Login:
    if 'allow_edit' not in st.session_state:
        st.session_state['allow_edit'] = False
        edit_control()


    ### Load data ###

    # Initial local data load to memory:
    if 'data' not in st.session_state:
        st.session_state['data'] = deepcopy(io.load_data(cf.TEMP_FILE))
