#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Functions for cleaning and preparing data in CORDATA
Copyright (C) 2023  Henrique S. Xavier
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

import pandas as pd
import numpy as np
import json
from zlib import crc32
from glob import glob
from collections import defaultdict

import xavy.dataframes as xd


# Tags associated to dummy columns:
topic_names = {'topics_agricultura_extrativismo_pesca': 'Agricultura, extrativismo e pesca',
 'topics_assistencia_desenvolvimento_social': 'Assistência e Desenvolvimento Social',
 'topics_ciencia_informacao_comunicacao': 'Ciência, Informação e Comunicação',
 'topics_comercio_servicos_turismo': 'Comércio, Serviços e Turismo',
 'topics_cultura_lazer_esporte': 'Cultura, Lazer e Esporte',
 'topics_dados_estrategicos': 'Dados Estratégicos',
 'topics_defesa_seguranca': 'Defesa e Segurança',
 'topics_economia_financas': 'Economia e Finanças',
 'topics_educacao': 'Educação',
 'topics_energia': 'Energia',
 'topics_equipamentos_publicos': 'Equipamentos Públicos',
 'topics_geografia': 'Geografia',
 'topics_genero_raca': 'Gênero e Raça',
 'topics_governo_politica': 'Governo e Política',
 'topics_habitacao_saneamento_urbanismo': 'Habitação, Saneamento e Urbanismo',
 'topics_industria': 'Indústria',
 'topics_justica_legislacao': 'Justiça e Legislação',
 'topics_meio_ambiente': 'Meio Ambiente',
 'topics_plano_plurianual': 'Plano Plurianual',
 'topics_relacoes_internacionais': 'Relações Internacionais',
 'topics_religiao': 'Religião',
 'topics_saude': 'Saúde',
 'topics_trabalho': 'Trabalho',
 'topics_transportes_transito': 'Transportes e Trânsito'}

type_names = {'type_artigo': 'artigo científico ou publicação acadêmica',
 'type_materia_jornalistica': 'matéria jornalística',
 'type_aplicativo_plataforma': 'aplicativo ou plataforma',
 'type_painel': 'painel, dashboard ou infográfico',
 'type_conjunto_de_dados': 'conjunto de dados',
 'type_inteligencia_artificial': 'inteligência artificial',
 'type_estudo': 'estudo independente',
 'type_bot': 'bot',
 'type_outro': 'outro'}


# Functions:

def rename_first_data_cols(df):
    """
    Standardize columns names of data about the used datasets
    so they all end with a number identifying the dataset.
    """
    
    # Hard-coded columns names associated to first dataset:
    data_cols = ['data_name', 'data_institution', 'data_url', 'data_periodical']
    suffix    = '_1'
    
    # Build name map:
    renamer = {k:k+suffix for k in data_cols}
    # Rename columns in place:
    df.rename(renamer, axis=1, inplace=True)

    
def std_date_series(series):
    """
    Standardize date `series` (of str). Unespecified patterns, 
    dates prior to 1900-01 and unexistent dates become NaNs.
    
    Returns a string series as well.
    """
    
    # Regex patterns for identifying dates:
    date_regexes = [r'(?:^[1-9]|\D[1-9]|0[1-9]|1[0-2])\/(?:19|20)[0-9]{2}', 
                    r'(?:19|20)[0-9]{2}-(?:[1-9]|0[1-9]|1[0-2])']
    # Date formats associated to the patterns above:
    date_formats = ['%m/%Y', '%Y-%m']
    
    # Strip data from whitespaces:
    cleaned = series.str.strip()
    output  = pd.Series(np.NaN, index=series.index, name=series.name)
    # Loop over date patterns:
    for r, f in zip(date_regexes, date_formats):
        # Standardize these dates:
        pos = cleaned.str.contains(r, regex=True).fillna(False)
        output.loc[pos] = pd.to_datetime(cleaned.loc[pos], format=f).dt.strftime('%Y-%m')
        
    return output


def bad_url(url_series):
    """
    Return a boolean Series specifying if input contains valid URLs.
    """
    
    # URL pattern:
    expr = r'(?:https?:\/\/|ftp:\/\/|did:)[^\s/$.?#]+\.[^\s]*'
    
    # Check if there is something written: 
    has_content = url_series.str.len() > 0
    # Check if matches the pattern:
    is_bad = has_content & ~url_series.fillna('').str.contains(expr, regex=True)
    
    return is_bad


def basic_str_clean(series):
    """
    Basic cleaning of str Series:
    - Remove surrounding whitespaces.
    
    Returns Series.
    """
    
    cleaned = series
    cleaned = cleaned.str.strip()
    
    return cleaned


def split_semicolons(series, delimiter=';'):
    """
    Split strings in `series` (Series) by `delimiter` (str).
    Also remove trailing whitespaces from the split elements.
    
    Returns a Series of lists.
    """
    
    # Remove trailing whitespaces:
    regex = r'\s*{}\s*'.format(delimiter)
    stripped = series.str.replace(regex, ';', regex=True)
    # Split terms:
    splitted = stripped.str.split(';')
    # Drop empty entries:
    notempty = splitted.apply(lambda l: l if l == None else list(filter(lambda s: len(s) > 0, l)))
    
    return notempty


def options_to_list(df, col_names):
    """
    Join option columns of a given set into a list of selected options.
    
    Parameters
    ----------
    df : DataFrame
        Table containing binary columns (dummy variables) that represent
        each option.
    col_names : dict str -> str
        Give the names to be associated to the dummy variable 1, for each
        column in `df`.
        
    Returns
    -------
    result : Series of list
        The selected options (with dummies equal to 1) in a list, 
        each one represented by its name in `col_names`.
    """    
    
    # Replace dummy variables by strings:
    temp_df = pd.DataFrame()
    for c in col_names.keys():
        mapper = {0:'', 1:col_names[c]}
        temp_df[c] = df[c].map(mapper)

    # Join options into lists:
    result = temp_df.apply(lambda row: list(filter(lambda s: len(s) > 0, row.tolist())), axis=1)
    
    return result


def sel_usecase_dataset(df, i):
    """
    Select columns from `df` (DataFrame) with a given dataset index 
    `i` (int) and standardize the columns names by removing the
    index.
    
    Returns a DataFrame.
    """
    
    # Select columns associated to one dataset:
    cols = xd.sel_col_by_regex(df, '_{}$'.format(i))
    
    # Remove index from column name:
    std_df = xd.rename_columns(df[cols], '(_{})$'.format(i), '')
    
    return std_df


def parse_usecase_datasets(usecase_df, max_datasets):
    """
    Given a single-row DataFrame about one usecase, returns a 
    DataFrame with the used datasets stacked.
    
    Parameters
    ----------
    usecase_df : DataFrame
        Table with the data used by one usecase, all in one line 
        (the info associated to each dataset is identified by 
        an index in the column name).
    max_datasets : int
        Maximum number of datasets allowed for each usecase.
    
    Returns
    -------
    df : DataFrame
        Table with information about all datasets used by the 
        usecase.
    """
    
    df = pd.concat([sel_usecase_dataset(usecase_df, i + 1) for i in range(max_datasets)], ignore_index=True)
    return df


def data_info_dict_list(usecase_df, max_datasets):
    """
    Parse the information about used datasets for one usecase
    into a list of dictionaries, where each entry in the list
    is an used dataset.
    
    Parameters
    ----------
    usecase_df : DataFrame
        Table with the data used by one usecase, all in one line 
        (the info associated to each dataset is identified by 
        an index in the column name).
    max_datasets : int
        Maximum number of datasets allowed for each usecase.
    
    Returns
    -------
    dict_list : list of dics
        A list with information about all datasets used by the 
        usecase.
    """
    
    # Hard-coded:
    required_data_info = ['data_name', 'data_institution', 'data_url']
    periodical_labels  = {0: None, 1:True, 2:False}
    
    # Get table of used datasets:
    datasets_df = parse_usecase_datasets(usecase_df, max_datasets)
    # Remove empty rows:
    datasets_df.dropna(how='all', subset=required_data_info, inplace=True)

    # Translation of the periodicity of the data collection:
    datasets_df['data_periodical'] = (datasets_df['data_periodical']).fillna(0).astype(int).map(periodical_labels)

    # Format as a list of dicts:
    dict_list = datasets_df.to_dict(orient='records')
    
    return dict_list


def series2transposed_df(series):
    """
    Transform a `series` (Series) into a single-row DataFrame.
    
    Returns a DataFrame.
    """
    return pd.DataFrame({0:series}).transpose()


def get_translator(translation_df, fields_regex, lower=False):
    """
    Create a dict from portuguese to spanish to be used 
    to translate certain text fields.
    
    Parameters
    ----------
    translation_df : DataFrame
        Table with text field names 'campo' and the textual
        content 'texto_pt' (in portuguese) and 'texto_es' 
        in spanish.
    fields_regex : str
        Regular expression representing the text fields to
        be used.
    lower : bool
        Whether to put everything to lower case.
        
    Returns
    -------
    mapper : dict
        A translation from portuguese to spanish for the 
        fields specified by `fields_regex`.
    """
    
    # Select subset of translations:
    sel_df = translation_df.loc[translation_df['campo'].str.contains(fields_regex)].copy()

    # Put to lowercase:
    if lower == True:
        sel_df['texto_pt'] = sel_df['texto_pt'].str.lower()
        sel_df['texto_es'] = sel_df['texto_es'].str.lower()
    
    # Create translation dict:
    mapper = sel_df[['texto_pt', 'texto_es']].set_index('texto_pt').to_dict()['texto_es']
    
    return mapper


def hash_string(string, prefix=''):
    """
    Takes a `string` as input, remove `prefix` from it and turns it into a hash.
    """
    name   = string.replace(prefix, '')
    return crc32(bytes(name, 'utf-8'))


def build_hash_id(df):
    """
    Return an int Series with hashes build from the 
    content in each line in `df`.
    """
    
    return df.astype(str).sum(axis=1).apply(hash_string)


def embed_metadata(data, metadata, data_key="data", meta_key="metadata"):
    """
    Create a new dict with keys `meta_key` and `data_key` pointing
    to values `metadata` and `data`, respectively.
    
    Returns a dict.
    """
    
    all_data = {meta_key: metadata, data_key: data}
    
    return all_data


def translate_list_elements(l, translator):
    """
    Translate every element in list `l` using `translator`
    (dict or equivalent). If `l` is None, return None.
    """
    # Guard against None:
    if l == None:
        return None
    # Translate each element in list:
    else:
        return [translator[a] for a in l]
    

def add_translation(case_json, type_map, topic_map, country_map):
    """
    Add entries (in place) to dict `case_json` containing translations for
    the type, topic and country of the usecase.
    
    Parameters
    ----------
    case_json : dict
        Data about one usecase.
    type_map : dict
        Mapping from portuguese to spanish for possible 
        usecase types.
    topic_map : dict
        Mapping from portuguese to spanish for possible 
        usecase types.
    country_map : dict
        Mapping from portuguese to spanish for possible 
        usecase types.
    """
    
    case_json['type_es']      = [type_map[k] for k in case_json['type']]
    case_json['topics_es']    = [topic_map[k] for k in case_json['topics']]
    case_json['countries_es'] = translate_list_elements(case_json['countries'], country_map)
    
    return case_json


def load_json(filename):
    """
    Load a JSON stored in `filename`.
    Returns a dict.
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    return data


def load_institution_identifier(json_pattern):
    """
    Creates a default dict that translates institution
    names listed in CGU's Portal Brasileiro de Dados 
    Abertos to their IDs.
    
    Parameters
    ----------
    json_pattern : str
        File pattern for glob function indicating 
        JSON files containing a list of institution
        data, including their name and ID.
    
    Returns
    -------
    inst2id : defaultdict
        The translator.  If the name is not found,
        the default dict returns None.    
    """
    
    # Load institution names:
    inst_files = glob(json_pattern)
    institutions = []
    ids = []
    for f in inst_files:
        institutions += [(i['titulo'], i['id']) for i in load_json(f)]
    
    # Sort list:
    institutions = sorted(institutions)
    
    # Security check: no repeated names:
    names = {i[0] for i in institutions}
    assert len(names) == len(institutions)
    
    # Create translator (name > ID):
    inst_dict = dict(institutions)
    inst2id = defaultdict(lambda: None, inst_dict)
    
    return inst2id