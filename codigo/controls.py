import streamlit as st

import dataops as io
import config as cf
import auxiliar as aux

#################
### Functions ###
#################

def status_selected(usecase: dict, status_filter: dict):
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


def status_selectors():
    """
    Create status selectors (checkbox filters) for 
    usecases.
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
    

def usecase_picker(usecases: list, data: dict):
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
    #idx = st.sidebar.selectbox("Selecione o caso de uso:", range(len(usecases)), format_func=lambda i: names[i], 
    #                        index=st.session_state['idx_init'], on_change=io.save_data, kwargs={'data': data})
    hash_id = st.sidebar.selectbox("Selecione o caso de uso:", ids, format_func=lambda i: id2name[i], 
                                   index=aux.usecase_id2idx(ids, st.session_state['id_init']), on_change=io.save_data, kwargs={'data': data})

    return hash_id


def usecase_selector(data: dict):
    """
    Display selectors for the usecase to be viewed/edited.
    """
    
    # Display statuses selectors for usecases:
    status_filter = status_selectors()

    # Filter usecases based on statuses:
    usecases = data["data"]
    sel_usecases = list(filter(lambda uc: status_selected(uc, status_filter), usecases))

    # Select usecase:
    #aux.log('Will run usecase select box')
    hash_id = usecase_picker(sel_usecases, data)
    #aux.log('Ran usecase select box')

    return hash_id


################
### Controls ###
################

