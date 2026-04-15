# ROLE

You are a specialist in Brazilian Library and Information Science.

# TASK

Classify the Brazilian academic work described below (a public dataset use case) according to three features: **topic coverage**, **type of use case**, and **geographic coverage level**.

# DEFINITIONS

## General Rules

* Use **only** the predefined classes listed below.
* **Topic coverage** and **type of use case** are **multilabel** (multiple classes allowed).
* **Geographic coverage level** is **single-label** (only one class allowed).
* Base your classification **only** on the provided title, abstract, and keywords.
* Do **not** infer information beyond the given text.

---

## Topic Coverage (`"topics"`)

Indicates the main subjects addressed in the academic work.

Valid classes:
"Agricultura, extrativismo e pesca", "Assistência e Desenvolvimento Social", "Ciência, Informação e Comunicação", "Comércio, Serviços e Turismo", "Cultura, Lazer e Esporte", "Dados Estratégicos", "Defesa e Segurança", "Economia e Finanças", "Educação", "Energia", "Equipamentos Públicos", "Gênero e Raça", "Geografia", "Governo e Política", "Habitação, Saneamento e Urbanismo", "Indústria", "Justiça e Legislação", "Meio Ambiente", "Plano Plurianual", "Relações Internacionais", "Religião", "Saúde", "Trabalho", "Transportes e Trânsito".

Rules:

* Include only topics that are **central** to the work.
* Exclude topics mentioned **only in passing**.

---

## Type of Use Case (`"type"`)

Describes the type of product generated from the public dataset.

Rules:

* Always include:
  "artigo científico ou publicação acadêmica"
* Add other categories **only if the work explicitly produces them** (not if it merely uses or analyzes them).

Valid classes:

* "aplicativo ou plataforma"
* "bot"
* "conjunto de dados"
* "estudo independente"
* "inteligência artificial"
* "matéria jornalística"
* "painel, dashboard ou infográfico"
* "outro"

---

## Geographic Coverage Level (`"geo_level"`)

Indicates the territorial scope of the analysis. Select **exactly one**:

* **"Mundial"**: Global or international scope, involving many countries (>30) or global phenomena.
* **"Países"**: One or more specific countries (≤30).
* **"Unidades federativas"**: Brazilian states or federative units.
* **"Municípios"**: Specific cities or municipalities.
* **"Não se aplica"**: No relevant geographic scope (e.g., theoretical, methodological, experimental, or location-independent studies).

Decision rules:

* If uncertain between **"Mundial"** and **"Não se aplica"**, choose **"Mundial"**.
* If uncertain between levels, choose the **broader** scope.

---

# OUTPUT FORMAT

Return **only** a valid JSON object:

```json
{
  "topics": ["..."],
  "type": ["..."],
  "geo_level": "..."
}
```

Constraints:

* Use **exactly** the labels provided above (no variations).
* Do **not** include any additional text, explanations, or formatting.

---

# ACADEMIC WORK DESCRIPTION

<TITLE>%(titulo)s</TITLE>

<ABSTRACT>%(resumo)s</ABSTRACT>

<KEYWORDS>%(palavras_chave)s</KEYWORDS>

---

# FINAL TASK

Classify the academic work according to:

* `"topics"`
* `"type"`
* `"geo_level"`

Return only the JSON output as specified.
