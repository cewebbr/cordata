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
from datetime import datetime
from zlib import crc32

import config as cf

class translate_dict(dict):
    """
    A dict that returns the key used if no translation was provided for it.
    """
    def __missing__(self,key):
        return key
    

def gen_uckey(hash, uckey):
    """
    Return a standardized key for usecase widgets.
    """
    return 'uc_{:}_{:}'.format(hash, uckey)


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
