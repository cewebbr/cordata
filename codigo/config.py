# Global variables for cordata-editor.py
# -*- coding: utf-8 -*-

# === CONFIG ===
DATA_FILE  = "data/usecases_current.json"
TEMP_FILE  = "data/usecases_temp.json"
EMPTY_FILE = "data/usecases_empty.json"
ENTRY_MODEL = "data/entry_model.json"

# Lists for controlled vocabularies
TYPE_OPTIONS = [
    "aplicativo ou plataforma",
    "artigo científico ou publicação acadêmica",
    "bot",
    "conjunto de dados",
    "estudo independente",
    "inteligência artificial",
    "matéria jornalística",
    "painel, dashboard ou infográfico",
    "outro"
    ]

TOPIC_OPTIONS = [
    "Agricultura, extrativismo e pesca",
    "Assistência e Desenvolvimento Social",
    "Ciência, Informação e Comunicação",
    "Comércio, Serviços e Turismo",
    "Cultura, Lazer e Esporte",
    "Dados Estratégicos",
    "Defesa e Segurança",
    "Economia e Finanças",
    "Educação",
    "Energia",
    "Equipamentos Públicos",
    "Gênero e Raça",
    "Geografia",
    "Governo e Política",
    "Habitação, Saneamento e Urbanismo",
    "Indústria",
    "Justiça e Legislação",
    "Meio Ambiente",
    "Plano Plurianual",
    "Relações Internacionais",
    "Religião",
    "Saúde",
    "Trabalho",
    "Transportes e Trânsito"
]

COUNTRY_OPTIONS = ['Afeganistão', 'África do Sul', 'Albânia', 'Alemanha', 'Andorra', 'Angola', 'Anguila', 'Antártica', 'Antígua e Barbuda', 'Arábia Saudita', 'Argélia', 'Argentina', 'Armênia', 'Aruba', 'Austrália', 'Áustria', 'Azerbaijão', 'Bahamas', 'Bahrein', 'Bangladesh', 'Barbados', 'Bélgica', 'Belize', 'Benim', 'Bermudas', 'Bielorrússia', 'Bolívia', 'Bósnia e Herzegovina', 'Botswana', 'Brasil', 'Brunei', 'Bulgária', 'Burkina Faso', 'Burundi', 'Butão', 'Cabo Verde', 'Camarões', 'Camboja', 'Canadá', 'Catar', 'Cazaquistão', 'Chade', 'Chile', 'China', 'Chipre', 'Cingapura', 'Colômbia', 'Comores', 'Coreia do Norte', 'Coreia do Sul', 'Costa Rica', 'Costa do Marfim', 'Croácia', 'Cuba', 'Curaçao', 'Dinamarca', 'Djibouti', 'Dominica', 'Egito', 'El Salvador', 'Emirados Árabes Unidos', 'Equador', 'Eritreia', 'Eslováquia', 'Eslovênia', 'Espanha', 'Estados Federados da Micronésia', 'Estados Unidos', 'Estônia', 'Etiópia', 'Fiji', 'Filipinas', 'Finlândia', 'França', 'Gabão', 'Gâmbia', 'Gana', 'Geórgia', 'Gibraltar', 'Granada', 'Grécia', 'Groenlândia', 'Guadalupe', 'Guam', 'Guatemala', 'Guernsey', 'Guiana', 'Guiana Francesa', 'Guiné', 'Guiné Equatorial', 'Guiné-Bissau', 'Haiti', 'Holanda', 'Honduras', 'Hong Kong', 'Hungria', 'Iémen', 'Ilha Bouvet', 'Ilha Christmas', 'Ilha Heard e Ilhas McDonald', 'Ilha Norfolk', 'Ilha da Reunião', 'Ilha de Man', 'Ilhas Åland', 'Ilhas Cayman', 'Ilhas Cocos', 'Ilhas Cook', 'Ilhas Falkland (Ilhas Malvinas)', 'Ilhas Feroe', 'Ilhas Geórgia do Sul e Sandwich do Sul', 'Ilhas Marianas do Norte', 'Ilhas Marshall', 'Ilhas Menores Distantes dos Estados Unidos', 'Ilhas Salomão', 'Ilhas Turcas e Caicos', 'Ilhas Virgens Americanas', 'Ilhas Virgens Britânicas', 'Índia', 'Indonésia', 'Irã', 'Iraque', 'Irlanda', 'Islândia', 'Israel', 'Itália', 'Jamaica', 'Japão', 'Jersey', 'Jordânia', 'Kiribati', 'Kuwait', 'Laos', 'Lesoto', 'Letónia', 'Líbano', 'Libéria', 'Líbia', 'Liechtenstein', 'Lituânia', 'Luxemburgo', 'Macau', 'Macedônia', 'Madagáscar', 'Malásia', 'Malawi', 'Maldivas', 'Mali', 'Malta', 'Marrocos', 'Martinica', 'Maurícia', 'Mauritânia', 'Mayotte', 'México', 'Moçambique', 'Moldávia', 'Mônaco', 'Mongólia', 'Monserrate', 'Montenegro', 'Myanmar', 'Namíbia', 'Nauru', 'Nepal', 'Nicarágua', 'Níger', 'Nigéria', 'Niue', 'Noruega', 'Nova Caledônia', 'Nova Zelândia', 'Omã', 'Países Baixos Caribenhos', 'Palau', 'Palestina', 'Panamá', 'Papua-Nova Guiné', 'Paquistão', 'Paraguai', 'Peru', 'Pitcairn', 'Polinésia Francesa', 'Polônia', 'Porto Rico', 'Portugal', 'Quénia', 'Reino Unido', 'República Centro-Africana', 'República Democrática do Congo', 'República Dominicana', 'República Quirguiz', 'República Tcheca', 'República do Congo', 'Roménia', 'Ruanda', 'Rússia', 'Saara Ocidental', 'Samoa', 'Samoa Americana', 'San Marino', 'Santa Helena, Ascensão e Tristão da Cunha', 'Santa Lúcia', 'São Bartolomeu', 'São Cristóvão e Nevis', 'São Martinho (França)', 'São Martinho (Países Baixos)', 'São Pedro e Miquelon', 'São Tomé e Príncipe', 'São Vicente e Granadinas', 'Seicheles', 'Senegal', 'Serra Leoa', 'Sérvia', 'Síria', 'Somália', 'Sri Lanka', 'Suazilândia', 'Sudão', 'Sudão Do Sul', 'Suécia', 'Suíça', 'Suriname', 'Svalbard e Jan Mayen', 'Tailândia', 'Taiwan', 'Tajiquistão', 'Tanzânia', 'Território do Oceano Índico Britânico', 'Territórios Franceses do Sul', 'Timor-Leste', 'Togo', 'Tokelau', 'Tonga', 'Trinidad e Tobago', 'Tunísia', 'Turcomenistão', 'Turquia', 'Tuvalu', 'Ucrânia', 'Uganda', 'Uruguai', 'Uzbequistão', 'Vanuatu', 'Vaticano', 'Venezuela', 'Vietnã', 'Wallis e Futuna', 'Zâmbia', 'Zimbábue']

UF_OPTIONS = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

GEOLEVEL_OPTIONS = ['Não se aplica', 'Mundial', 'Países', 'Unidades federativas', 'Municípios', None]

GEOLEVEL_KEYS = {'Países':'countries', 'Unidades federativas':'fed_units', 'Municípios':'municipalities'}