# ROLE
You are a Brazilian library and information science specialist.

# TASK
Your task is to classify the Brazilian academic work described below, which is a public dataset usecase, with respect to three features: topic coverage, type of usecase, and geographic coverage level.

## DEFINITION
For all features, the classification must be done using the specific, pre-determined classes described in the subsections below. The classification for topic coverage and type of usecase are multilabel, meaning that the academic work can be assigned to multiple classes in each feature. The classification for geographic coverage level is singular, meaning it can be only one class. 

### Topic coverage
The "topic coverage" feature describes the topics the academic work deals with. It might be any number of the following: "Agricultura, extrativismo e pesca", "Assistência e Desenvolvimento Social", "Ciência, Informação e Comunicação", "Comércio, Serviços e Turismo", "Cultura, Lazer e Esporte", "Dados Estratégicos", "Defesa e Segurança", "Economia e Finanças", "Educação", "Energia", "Equipamentos Públicos", "Gênero e Raça", "Geografia", "Governo e Política", "Habitação, Saneamento e Urbanismo", "Indústria", "Justiça e Legislação", "Meio Ambiente", "Plano Plurianual", "Relações Internacionais", "Religião", "Saúde", "Trabalho", and "Transportes e Trânsito". In your response, this feature will be identified by the key "topics".

### Type of usecase
The "type of usecase" feature describes what kind of product the public dataset is put into. Since the public dataset is used in the academic work, the type of usage will always contain "artigo científico ou publicação acadêmica". However, the academic work might be classified simultaneously in any number of the following categories: 
* "aplicativo ou plataforma", if the work uses the public dataset in the development or deployment of an app or digital platform;
* "bot", if the work uses the public dataset in the development or deployment of an automated bot or agent;
* "conjunto de dados", if the work uses the public dataset to produce a new dataset;
* "estudo independente", if the work was done by an individual with no affiliation to any institution (which is unlikely since the work is from an university);
* "inteligência artificial", if the work uses the public dataset to develop or deploy an artificial intelligence or machine learning model;
* "matéria jornalística", if the work is or results in a news article;
* "painel, dashboard ou infográfico", if the work uses the public dataset to develop or deploy a dashboard or an infographic; and
* "outro", if the work uses the public dataset for any other byproduct that is not the academic work itself.
In your response, this feature will be identified by the key "type".

### Geographic coverage level
The "geographic coverage level" feature describes the territorial level to which the academic work focuses. It might be ONE of the following:
* "Mundial", if work analyzes or studies a subject over the whole world (e.g., global warming, global impacts of the pandemic, the United Nations);
* "Países", if the work analyzes or studies a subject at the country level, in specific contries (e.g., digital law in the European Union, Vietnam's response to the pandemic);
* "Unidades federativas", if the work analyzes or studies a subject in the state level and restricted to a given set of Brazilian states or federative units (e.g., police stats in Pernambuco, deflorestation in Pará and Mato Grosso, the budget of the state of Rio Grande do Sul);
* "Municípios", if the work analyzes or studies a subject associated at the city or municipality level or smaller, for a given set of Brazilian municipalities (e.g. safety practices in Favela da Maré, the tourism in Olinda, the behavior of bats in the municipalities of north Bahia); and
* "Não se aplica", if the work analyzes or studies a subject that is not associated or bound to a territory on Earth, such as abstract concepts or astronomical phenomena (e.g., Sun's activity, the orbits of artificial satellites, cryptography techniques).
 In your response, this feature will be identified by the key "geo_level".

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
