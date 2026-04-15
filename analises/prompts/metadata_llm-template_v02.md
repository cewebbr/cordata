# ROLE
You are a Brazilian library and information science specialist.

# TASK
Your task is to classify the Brazilian academic work described below, which is a public dataset usecase, with respect to three features: topic coverage, type of usecase, and geographic coverage level.

## DEFINITION
For all features, the classification must be done using the specific, pre-determined classes described in the subsections below. The classification for topic coverage and type of usecase are multilabel, meaning that the academic work can be assigned to multiple classes in each feature. The classification for geographic coverage level is singular, meaning it can be only one class. 

### Topic coverage
The "topic coverage" feature describes the topics the academic work is focused on. It might be any number of the following: "Agricultura, extrativismo e pesca", "Assistência e Desenvolvimento Social", "Ciência, Informação e Comunicação", "Comércio, Serviços e Turismo", "Cultura, Lazer e Esporte", "Dados Estratégicos", "Defesa e Segurança", "Economia e Finanças", "Educação", "Energia", "Equipamentos Públicos", "Gênero e Raça", "Geografia", "Governo e Política", "Habitação, Saneamento e Urbanismo", "Indústria", "Justiça e Legislação", "Meio Ambiente", "Plano Plurianual", "Relações Internacionais", "Religião", "Saúde", "Trabalho", and "Transportes e Trânsito". In your answer, do not include topics that are referenced in the academic work description only in passing. In your response, this feature will be identified by the key "topics".

### Type of usecase
The "type of usecase" feature describes what kind of product the public dataset is put into. Since the public dataset is used in the academic work, the type of usage will always contain "artigo científico ou publicação acadêmica". However, the academic work might be classified as something else as well if it also delivers a new product such as AI models, news articles, dashboards or datasets. In such cases, the work can be categorized simultaneously in any number of the following categories: 
* "aplicativo ou plataforma", if the work uses the public dataset in the development or deployment of an app or digital platform;
* "bot", if the work uses the public dataset in the development or deployment of an automated bot or agent;
* "conjunto de dados", if the work uses the public dataset to produce a new dataset;
* "estudo independente", if the work was done by an individual with no affiliation to any institution (which is unlikely since the work is from an university);
* "inteligência artificial", if the work delivers a new AI or machine learning model that was trained on the public dataset;
* "matéria jornalística", if the work is or results in a news article;
* "painel, dashboard ou infográfico", if the work uses the public dataset to develop or deploy a dashboard or an infographic; and
* "outro", if the work uses the public dataset for any other byproduct that is not the academic work itself.
Note that other types of usecase besides "artigo científico ou publicação acadêmica" should only be attributed if the academic work delivers the products above, not if it only uses or analyzes them. In your response, this feature will be identified by the key "type".

### Geographic coverage level
The "geographic coverage level" feature describes the size of the territory analyzed the academic work. It might be ONE of the following:
* "Mundial", if the geographical dimension of the work is analytically central and explicitly addressed at an international or worldwide scale, typically involving a large number of countries (more than 30), multiple cross-national comparisons, or globally distributed phenomena, where the analysis aims to produce conclusions about patterns, relationships, or processes that operate at the level of the global system or across several countries (e.g., global warming, global impacts of the pandemic, the United Nations);
* "Países", if the work analyzes or studies a subject at the country level, in specific contries (e.g., digital law in the European Union, Vietnam's response to the pandemic), limited to at most 30 countries;
* "Unidades federativas", if the work analyzes or studies a subject restricted to a given set of Brazilian states or federative units and covers these units as a whole or a large portion of each one (e.g., police stats in Pernambuco, deflorestation in Pará and Mato Grosso, the budget of the state of Rio Grande do Sul);
* "Municípios", if the work analyzes or studies a subject restricted to a small set the cities or municipalities (e.g. safety practices in Favela da Maré, the tourism in Olinda, the behavior of bats in the municipalities of north Bahia); and
* "Não se aplica", if the work focuses on extraterrestrial phenomena or if the geographical scope is not relevant to the research objective, meaning that the study does not analyze, compare, or draw conclusions based on territorial units. This includes methodological, theoretical, experimental, or technical studies - such as algorithm development, laboratory analyses, simulations, or evaluations using generic or benchmark datasets - where the findings are independent of location and are not intended to describe or explain phenomena in any specific geographic context.
 When in doubt between "Mundial" and "Não se aplica", choose "Mundial". When in doubt between a wider and more detailed coverage level, choose the wider. In your response, this feature will be identified by the key "geo_level".

## INSTRUCTIONS
- Base your classification ONLY on the information provided about the academic work (title, abstract, and keywords).

## OUTPUT FORMAT
Your response must be in the JSON format exemplified below:

{
  "topics": ["Comércio, Serviços e Turismo", "Transportes e Trânsito", "Economia e Finanças"],
  "type": ["artigo científico ou publicação acadêmica", "inteligência artificial"],
  "geo_level": "Países"
}

Do not output anything else apart from the JSON above. All keys and values in your response must be written exactly like the ones provided in the DEFINITIONS above. 

# ACADEMIC WORK DESCRIPTION

<TITLE>%(titulo)s</TITLE>

<ABSTRACT>%(resumo)s</ABSTRACT>

<KEYWORDS>%(palavras_chave)s</KEYWORDS>

# TASK 
Your task is to classify the Brazilian academic work described above, which is uses a public dataset, with respect to three features: topic coverage ("topics"), type of usecase ("type"), and geographic coverage level ("geo_level"). Your response must follow the JSON structure presented above.
