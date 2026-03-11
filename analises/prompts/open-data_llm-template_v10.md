# ROLE
You are a data scientist expert in research metadata analysis and open data.

# TASK
Your task is to determine whether the Brazilian academic work described below makes use of publicly available datasets in its analysis.

## DEFINITION
For this task, consider that a work "uses publicly available datasets" if it analyzes data that can be accessed online by the public without special authorization or payment, such as:
- Government or official statistics (e.g., IBGE, INEP, World Bank, WHO, and DATASUS);
- Open government data portals (e.g., Portal Brasileiro de Dados Abertos, Geosampa);
- Public administrative records;
- Datasets made available on the Web by NGOs (e.g., Wikidata);
- Open scientific, academic or environmental datasets;
- Open satellite or geospatial data (e.g., Prodes, Landsat, Sentinel, OpenStreetMap);
- Open access bibliographic databases (e.g., Scielo, PubMed);
- Open access chemical, genetical, or biological databases (e.g., PubChem, GenBank, GBIF).

Do NOT consider as publicly available datasets:
- Data collected exclusively via surveys, interviews, experiments, or fieldwork;
- Proprietary, commercial, or restricted datasets;
- Private institutional databases;
- Publicly available documents that are not datasets (e.g., research papers on arXiv, government reports, news articles);
- Works that study, discuss, or evaluate "open data" policies, platforms, or initiatives without actually using open datasets in their analysis.

## INSTRUCTIONS
- Base your decision ONLY on the information provided (title, abstract, and keywords).
- Focus on whether the work USES public data, not whether it DISCUSSES open data.
- When in doubt if the work uses publicly available data or not, take your best guess based on the information provided.

## OUTPUT FORMAT
Respond with only one of the two options: "Uses public data" or "Does not use public data". Do not provide any other output apart from these two possible answers.


# ACADEMIC WORK DESCRIPTION

<TITLE>%(titulo)s</TITLE>

<ABSTRACT>%(resumo)s</ABSTRACT>

<KEYWORDS>%(palavras_chave)s</KEYWORDS>

# TASK 
Your task is to determine whether the academic work described above makes use of publicly available datasets in its analysis. 
Respond with only one of the two options: "Uses public data" or "Does not use public data".
