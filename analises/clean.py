import pandas as pd
import numpy as np

import xavy.dataframes as xd


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
    
    return splitted


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
    periodical_labels  = {1:True, 2:False}
    
    # Get table of used datasets:
    datasets_df = parse_usecase_datasets(usecase_df, max_datasets)
    # Remove empty rows:
    datasets_df.dropna(how='all', subset=required_data_info, inplace=True)

    # Translation of the periodicity of the data collection:
    datasets_df['data_periodical'] = (datasets_df['data_periodical']).astype(int).map(periodical_labels)

    # Format as a list of dicts:
    dict_list = datasets_df.to_dict(orient='records')
    
    return dict_list


def series2transposed_df(series):
    """
    Transform a `series` (Series) into a single-row DataFrame.
    
    Returns a DataFrame.
    """
    return pd.DataFrame({0:series}).transpose()