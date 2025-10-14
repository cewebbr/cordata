import requests
import json
import streamlit as st
from pathlib import Path

import config as cf

def download_data():
    """
    Download CORDATA data currently up on the website.
    """
    url = 'https://raw.githubusercontent.com/cewebbr/cordata/refs/heads/main/dados/limpos/usecases_current.json'
    response = requests.get(url)
    status = response.status_code
    if status == 200:
        content = response.content.decode()
        data = json.loads(content)
        st.success('Dados carregados com sucesso')
        return data
    else:
        st.error(f'Falha no carregamento dos dados (status code {status})')

def save_data(data, path=cf.TEMP_FILE):
    """
    Save `data` (dict) to `path` (str).
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

def load_data(path):
    """
    Load JSON from file at `path` (str).
    """
    return json.loads(Path(path).read_text(encoding="utf-8"))
