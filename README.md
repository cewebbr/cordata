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
    ├── codigo                  <- Web app interno de catalogação e gestão dos dados (CMS) 
	├── dados                   <- Metadados sobre casos de uso 
    |   ├── brutos              <- Metadados brutos, originais, vindos do formulário
	|   ├── curados             <- Metadados originados do form manualmente corrigidos
    |   └── limpos              <- Metadados limpos, corrigidos, padronizados
	├── imagens                 <- Imagens representativas dos casos de uso
    ├── analises                <- Código de limpeza dos dados (notebooks de python)
    ├── scripts                 <- Rotinas auxiliares
    └── docs                    <- Documentos e registros


## Sobre os metadados dos reúsos

Alguns metadados sobre reúsos foram informados pelo público em geral através do [formulário do CORDATA](https://cordata.ceweb.br/formulario). Nesses casos, os metadados são armazenados na sua forma bruta e posteriormente passam por uma curadoria do Ceweb.br. Os dados brutos, tais quais preenchidos no formulário do CORDATA, estão disponíveis na pasta [dados/brutos](dados/brutos). Os dados curados são versões dos dados brutos manualmente corrigidas, ainda no formato CSV. Ver [dados/curados](dados/curados). 

Outros metadados são registrados diretamente pela equipe do Ceweb.br. Nesses casos, o registro é feito através do _Content Management System_ (CMS) disponibilizado em [codigo](codigo), que resulta diretamente no formato final (JSON). Nesses casos, não há versões brutas ou curadas.

A versão limpa e enriquecida dos metadados coletados através do formulário, combinada com os registrados diretamente pela equipe do Ceweb.br, está em [dados/limpos](dados/limpos). São esses os dados que aparecem no [site do CORDATA](http://cordata.ceweb.br).

O código que faz a limpeza dos dados coletados através do formulário encontra-se disponível na pasta [analises](analises).


## Contato

Para mais informações sobre o projeto, falar com [Henrique S. Xavier](http://henriquexavier.net) (<https://github.com/hsxavier>).
