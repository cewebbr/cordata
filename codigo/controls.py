# Special widgets for controling the editor.
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

import config as cf
import auxiliar as aux


def status_selected(usecase: dict, status_filter: dict) -> bool:
    """
    Return whether the usecase is selected by a filter, that is,
    whether its value for the possible statuses in listed in 
    the provided status filter.

    Parameters
    ----------
    usecase : dict
        One usecase, stored as a dict.
    status_filter : dict of lists
        Each key is a possible status type, and the associated
        value is a list of selected statuses for that type.
    
    Returns
    -------
    selected : bool
        Whether or not that usecase was selected by the filter.
    """
    # Return False if any status type is not selected:
    for status_type in status_filter.keys():
        if usecase[status_type] not in status_filter[status_type]:
            return False
    # Return True if all status types are selected:
    return True


def status_selectors() -> dict:
    """
    Create status selectors (checkbox filters) for 
    usecases. Return the statuses selected by the 
    checkbox widgets.
    """
    
    status_filter = dict()
    status_caption = {'status_published': 'Status de publicação:', 'status_review': 'Status de revisão:'}
    
    # Loop over statuses types:
    for status_type in cf.STATUS_DISPLAY.keys():
        
        # Get captions and options for one status type:
        st.sidebar.write(status_caption[status_type])
        status_dict = cf.STATUS_DISPLAY[status_type]
        
        # Loop over options:
        cols = st.sidebar.columns(len(status_dict))
        status_filter[status_type] = []
        for i, (status_val, status_label) in enumerate(status_dict.items()):
            with cols[i]:
                # If options is selected, add it to selection
                if st.checkbox(label=status_label, value=True) == True:
                    status_filter[status_type].append(status_val)

    return status_filter
    

def usecase_picker(usecases: list, data: dict) -> int:
    """
    Create the dropdown selector used to pick a usecase
    from the list of usecases.

    Parameters
    ----------
    usecases : list of dict
        A list of usecases, each a dict containing the data
        about that usecase. It can be filtered (i.e. not 
        contain all usecases in `data`).
    data : dict
        The whole CORDATA data, including the metadata (e.g. 
        last_update) and all usecases.
    
    Returns
    -------
    hash_id : int
        The ID of the selected usecase.
    """
    names = [uc['name'] for uc in usecases]
    ids   = [uc['hash_id'] for uc in usecases]
    id2name = dict(zip(ids, names))
    hash_id = st.sidebar.selectbox("Selecione o caso de uso:", ids, format_func=lambda i: id2name[i],  
                                   index=aux.nindex(ids, st.session_state['usecase_selectbox']), 
                                   key='usecase_selectbox')

    return hash_id


def usecase_selector(data: dict)-> int:
    """
    Display selectors for the usecase to be viewed/edited.
    Return the ID of the usecase selected in the select box, 
    after filtering the usecases by statuses accordingly to 
    the check boxes. 
    """
    
    # Display statuses selectors for usecases and get selected statuses:
    status_filter = status_selectors()

    # Check if status selector will drop current usecase:
    usecases = data["data"]
    if st.session_state['usecase_selectbox'] != None:
         uc = aux.select_usecase_by_id(data, st.session_state['usecase_selectbox'])
         if status_selected(uc, status_filter) == False:
             # Set id_init to None.
             st.session_state['usecase_selectbox'] = None

    # Filter usecases based on statuses:
    sel_usecases = list(filter(lambda uc: status_selected(uc, status_filter), usecases))

    # Select usecase:
    hash_id = usecase_picker(sel_usecases, data)
    
    return hash_id