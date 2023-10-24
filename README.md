# CORDATA

O **CORDATA - Catálogo Online de Reúso de Dados Abertos** é um site que lista casos de uso de dados abertos. Você pode acessá-lo aqui:
<https://cordata.ceweb.br>. Nesta página disponibilizamos os dados brutos coletados e os dados disponibilizados no site do projeto.

**CORDATA - Catálogo Online de Reutilización de Datos Abiertos** _es un sitio web que enumera casos de uso de datos abiertos. Puedes acceder a él aquí:
<https://cordata.ceweb.br>. En esta página ponemos a disposición los datos brutos recopilados y los datos disponibles en el sitio web del proyecto._

## Estrutura do projeto:

    .
    ├── README.md               <- Este documento
    ├── LICENSE                 <- Licença dos dados e códigos do projeto
    ├── requirements.txt        <- Principais pacotes de python necessários
    ├── dados                   <- Metadados sobre casos de uso 
    |   ├── brutos              <- Metadados brutos, originais
    |   └── limpos              <- Metadados limpos, corrigidos, padronizados
    ├── analises                <- Código de limpeza dos dados (notebooks de python)
    ├── scripts                 <- Rotinas auxiliares
    └── docs                    <- Documentos e registros

Os dados brutos, tais quais preenchidos no formulário do CORDATA, estão disponíveis na pasta [dados/brutos](dados/brutos). 
A versão limpa e enriquecida, que aparece no catálogo do CORDATA, está em [dados/limpos](dados/limpos).
O código que faz a limpeza dos dados coletados encontra-se disponível na pasta [analises](analises).

## Contato

Para mais informações sobre o projeto, falar com [Henrique S. Xavier](http://henriquexavier.net) (<https://github.com/hsxavier>).
