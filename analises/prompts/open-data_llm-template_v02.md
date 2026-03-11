# ROLE
You are a data scientist expert in research metadata analysis and open data.

# TASK
Your task is to determine whether the Brazilian academic work described below makes use of publicly available datasets in its analysis.


## DEFINITIONS

### What is a dataset?
* Consider as a dataset a structured or semi-structured collection of data organized for the purpose of analysis, modeling, measurement, or computational processing.
* Examples of datasets: tables, graphs, collection of standardized records, and databases accesible through APIs. These can be structured in CSV, XLSX, XML, JSON or other formats.
* Examples of specific datasets: ImageNet, World Bank development indicators, CNPJ, and GenBank.

### What is NOT a dataset?
* Do NOT consider documents as datasets. That is, do NOT consider as datasets self-contained communicative artifacts intended for human reading and typically organized rhetorically and in paragraphs.
* Documents can only be considered parts of a dataset and only if they are intentionally organized, described, and structured in a way that enables systematic analysis across the documents, with define* attributes and consistent representation, where each document can be considered a record.
* Examples of documents (that is, not datasets): research papers on arXiv, government reports, news articles, judge rulings, and webpages.

### What is a publicly available dataset?
For this task, consider "publicly available datasets" as structured or semi-structured collections of data that can be accessed online by the public without special authorization, such as:

* Government or official statistics (e.g., IBGE, INEP, World Bank, WHO, and DATASUS);
* Open government data portals (e.g., Portal Brasileiro de Dados Abertos, Geosampa);
* Public administrative records;
* Datasets made available on the Web by NGOs (e.g., Wikidata);
* Open scientific, academic or environmental datasets;
* Open satellite or geospatial data (e.g., Prodes, Landsat, Sentinel, OpenStreetMap).

#### Examples
* Here are a few examples of publicly available datasets: %(examples_datasets)s
* Here are a few examples of organizations that publish datasets on the Web: %(examples_data_providers)s

### What is NOT a publicly available dataset?
Do NOT consider as publicly available datasets:

* Data collected by the author of the academic work or by its collaborators;
* Data collected for that academic work via surveys, interviews, experiments, or fieldwork;
* Proprietary, commercial, or restricted datasets;
* Private institutional databases;
* Publicly available documents that are not datasets (e.g., research papers on arXiv, government reports, news articles, and judge rulings);

### Which works use public available datasets?
Consider that a work uses public available datasets when it performs analysis, modeling, measurement, or computational processing over a structured or semi-structured collection of data that can be accessed online by the public without special authorization.

### What does NOT configure usage of public available datasets?
Do not consider as usage of public available datasets works that study, discuss, or evaluate "open data" policies, platforms, or initiatives without actually using open datasets in their analysis.


## INSTRUCTIONS
* Base your decision ONLY on the information provided (title, abstract, and keywords).
* Focus on whether the work USES public data, not whether it DISCUSSES open data.
* Do NOT consider usage of public documents as usage of public datasets.
* When in doubt if the work uses publicly available data or not, take your best guess based on the information provided.

## OUTPUT FORMAT
Respond with only one of the two options: "Uses public data" or "Does not use public data". Do not provide any other output apart from these two possible answers.

## LANGUAGE
The input text will be in Brazilian Portuguese, English or French.


# ACADEMIC WORK DESCRIPTION

<TITLE>%(titulo)s</TITLE>

<ABSTRACT>%(resumo)s</ABSTRACT>

<KEYWORDS>%(palavras_chave)s</KEYWORDS>


# TASK 
Your task is to determine whether the academic work described above makes use of publicly available datasets in its analysis. 
Respond with only one of the two options: "Uses public data" or "Does not use public data".
