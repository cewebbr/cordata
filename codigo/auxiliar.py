"""
CORDATA EDITOR libraries 
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
import streamlit.components.v1 as components
from datetime import datetime
from zlib import crc32
import numpy as np
import csv

import config as cf

class translate_dict(dict):
    """
    A dict that returns the key used if no translation was provided for it.
    """
    def __missing__(self,key):
        return key


# Display format for options including None:
none_fmt = translate_dict({None:'(vazio)'})


def tags_fmt(x):
    """
    Return empty list if `x` is None.
    """
    if x == None:
        return []
    return x


def gen_uckey(hash, prop, idx=0):
    """
    Return a standardized key for usecase widgets.

    Parameters
    ----------
    hash : int
        ID of the usecase.
    prop : str
        Name of the usecase property.
    idx : int
        Index of an entry part of property
        (e.g. for datasets used by a usecase).
    
    Returns
    -------
    uckey : str
        Unique key for that usecase and property 
        (and entry in the case of datasets).
    """
    return 'uc_{:}_{:}_{:}'.format(hash, prop, idx)


def read_lines(path):
    """
    Read strings from file at `path` (str or Path) and 
    put each line into an element of a list.
    """
    with open(path, 'r') as file:
        lines = [line.rstrip() for line in file]
    return lines


def read_date(date_str, date_fmts=['%m/%Y', '%d/%m/%Y']):
    """
    Parse date from `date_str` (str) using the first 
    format in `date_fmts` (list of str) that works.
    """

    # Forward None:
    if date_str == None:
        return None

    success = False
    for fmt in date_fmts:
        try:
            date = datetime.strptime(date_str, fmt).date()
            success = True
        except:
            pass
        if success == True:
            break
    if success == True:
        return date
    else:
        raise Exception("Weird date format '{:}'".format(date_str))


def nindex(options, sel):
    """
    Return position of `sel` (obj) in `options` (list).
    If `sel` is None, return None.
    """    
    # None forward:
    if sel == None:
        return None
    # Return position of option
    return options.index(sel)


def html(html_code, sidebar=False):
    """
    Place `html_code` (str) in the Streamlit app.
    If `sidebar` is True, place it in the sidebar.
    """
    if sidebar == True:
        st.sidebar.write(html_code, unsafe_allow_html=True)
    else:
        st.write(html_code, unsafe_allow_html=True)


def log(message, prefix='[LOG]', log_time=True):
    """
    Print message to terminal.

    Parameters
    ----------
    message : str
        The message to print.
    prefix : str
        Prefix added to message (followed by a whitespace)
        to identify the logging.
    log_time : bool
        Whether to add date and time of the message or not.
    """
    if cf.LOG == True:
        if log_time == True:
            t = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            output = '{:} {:} == {:}'.format(prefix, t, message)
        else:
            output = '{:} {:}'.format(prefix, message)
        print(output)


def hash_string(string, prefix=''):
    """
    Takes a `string` as input, remove `prefix` from it and turns it into a hash.
    """
    name   = string.replace(prefix, '')
    return crc32(bytes(name, 'utf-8'))


@st.dialog('Controle de edição')
def edit_control():
    """
    Admin access dialog that asks for password to
    enable edit permission.
    """
    entry = st.text_input(label='Digite a senha:', type='password')
    if st.button('🚪 Entrar') == True:
        if entry == st.secrets['PWD']:
            log('Log in: ALLOW EDIT')
            st.session_state['allow_edit'] = True
        else:
            log('Log in: EDITING NOT ALLOWED')
            st.session_state['allow_edit'] = False
        st.rerun()


def read_csv_as_dict(filename, delimiter=",", skip_header=True):
    """
    Read a CSV file and return a dict of NumPy arrays (one per column).

    Parameters
    ----------
    filename : str
        Path to the CSV file.
    delimiter : str, optional
        Field delimiter (default ',').
    skip_header : bool, optional
        If True, assumes the first line contains column headers.

    Returns
    -------
    dict[str, np.ndarray]
        A dictionary mapping column names to NumPy arrays.
    """
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=delimiter)
        header = next(reader) if skip_header else None
        rows = [row for row in reader]

    # Convert to NumPy array for easy slicing
    data = np.array(rows, dtype=object)  # use object to handle mixed types

    # Infer header if not present
    if header is None:
        header = [f"col{i}" for i in range(data.shape[1])]

    # Try to convert each column to numeric if possible
    result = {}
    for i, name in enumerate(header):
        result[name] = data[:, i]

    return result


@st.cache_data
def load_translations(path='data/translations.csv', from_l='ptbr', to_l='es'):
    """
    Load translations for terms used in the data from 
    CSV file stored in `path` (str) and return a dict 
    with the translations from language `from_l` (str)
    to `to_l` (str). 
    """
    translations_df = read_csv_as_dict(path)
    translation_dict = dict(zip(translations_df[from_l], translations_df[to_l]))
    return translation_dict


def usecase_id2idx(ids: list, target_id: int):
    """
    Return the index of `target_id` in `ids`.
    If `target_id` is None, return None.
    """
    if target_id == None:
        return None
    else:
        return ids.index(target_id)
    

def get_usecase_pos(usecases: list, hash_id: int) -> int: 
    """
    Given a list `usecases` of usecases (dicts), returns the 
    position in the list of the usecase identified by `hash_id`
    (int).
    """
    ids = [uc['hash_id'] for uc in usecases]
    idx = usecase_id2idx(ids, hash_id)
    return idx


def select_usecase_by_id(data: dict, hash_id: int) -> dict:
    """
    Return the usecase stored in `data` (dict) whose
    hash_id is the one provided. 
    """
    usecases = data["data"]
    
    selection = list(filter(lambda uc: uc['hash_id'] == hash_id, usecases))
    assert len(selection) <= 1, 'Found duplicated hash_id = {:}'.format(hash_id)
    assert len(selection) > 0, 'Did not find hash_id = {:}'.format(hash_id)
    uc = selection[0]

    return uc