# Content Management System (CMS) do CORDATA

Este diretório contém o código de um editor de casos de uso para o projeto CORDATA. O Web app foi construído em Python, utilizando 
o pacote [Streamlit](https://docs.streamlit.io/). O editor possui uma interface gráfica na qual é possível selecionar um caso de uso 
para visualizar e editar todos os seus campos.

## Estrutura do CMS:

    .
    ├── README.md               <- Este documento
    ├── LICENSE                 <- Licença dos dados e códigos do projeto
    ├── requirements.txt        <- Principais pacotes de python necessários
	├── data                    <- Modelos para os registros e dados internos
	├── .streamlit              <- Pasta com configurações do streamlit e senha do CMS
    ├── backup.sh               <- Script em bash de backup automático
	├── cordata-editor.py       <- Arquivo principal do CMS
    └── *.py                    <- Restante do código do CMS

## Como executar o CMS

Instale as dependências com o comando:

    pip install -r requirements.txt
	
Crie um arquivo `secrets.toml` dentro da pasta `.streamlit` com a linha `PWD = "senhaquedeseja"` para definir a senha de acesso ao Web app. Em seguida, utilize o pacote de python `streamlit` para executar o CMS:

    streamlit run cordata-editor.py &
	
Acesse o CMS através do seguinte endereço no seu navegador Web: `http://localhost:8502/`.
