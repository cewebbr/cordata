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