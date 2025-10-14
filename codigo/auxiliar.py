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

class translate_dict(dict):
    """
    A dict that returns the key used if no translation was provided for it.
    """
    def __missing__(self,key):
        return key
    

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
        print(fmt)
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


def html(html_code):
    """
    Place `html_code` (str) in the Streamlit app.
    """
    st.write(html_code, unsafe_allow_html=True)
