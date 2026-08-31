"""
ETL pipeline for the UFRGS bibliographic dataset.

Dataset characteristics (discovered during exploration):
- File: CSV with latin1 encoding and semicolon delimiter
- 30,943 rows × 15 columns
- Column mapping required: AUTORIA→autoria, TITULO→titulo, URI→uri,
  RESUMO_COMPLETO→resumo, PUBLICADORA→publicador, PALAVRAS_CHAVES→palavras_chave
- RESUMO_COMPLETO has 840 placeholder values ("Resumo não disponível" variants)
- URI has 1,724 missing values
- TIPO has a case inconsistency ('Trabalho de conclusão de Curso' vs '…curso')
- 30 duplicate titles (59 rows); duplicates share same title but different years/URIs
- PALAVRAS_CHAVES already uses "; " as separator — no transformation needed
- AUTORIA has 8 missing values; format is already "Sobrenome, Nome"
- No separate abstract/resumo or keywords/area columns to merge
"""

import re
import chardet
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------------------------
# 1. Loading
# ---------------------------------------------------------------------------

def detect_encoding(filepath: str, sample_bytes: int = 100_000) -> str:
    """Detect file encoding using chardet on a byte sample."""
    with open(filepath, "rb") as f:
        raw = f.read(sample_bytes)
    result = chardet.detect(raw)
    encoding = result.get("encoding") or "utf-8"
    # chardet often returns Windows-1252 for latin1 content — both are safe to
    # read with 'latin1' which never raises on arbitrary bytes.
    if encoding.lower() in ("windows-1252", "iso-8859-1"):
        encoding = "latin1"
    return encoding


def detect_delimiter(filepath: str, encoding: str, candidates: tuple = (",", ";")) -> str:
    """
    Sniff the CSV delimiter by comparing column counts for each candidate.
    Returns the delimiter that yields the most columns on the first data row.
    """
    best_sep, best_count = candidates[0], 0
    with open(filepath, encoding=encoding, errors="replace") as f:
        header = f.readline()
    for sep in candidates:
        count = header.count(sep)
        if count > best_count:
            best_count = count
            best_sep = sep
    return best_sep


def load_file(filepath: str) -> pd.DataFrame:
    """
    Load a CSV/XLS/XLSX file into a DataFrame with automatic encoding and
    delimiter detection.
    """
    path = Path(filepath)
    suffix = path.suffix.lower()

    if suffix in (".xls",):
        return pd.read_excel(filepath, engine="xlrd")
    if suffix in (".xlsx",):
        return pd.read_excel(filepath, engine="openpyxl")

    # CSV / TSV
    encoding = detect_encoding(filepath)
    delimiter = detect_delimiter(filepath, encoding)
    df = pd.read_csv(
        filepath,
        encoding=encoding,
        sep=delimiter,
        dtype=str,          # keep everything as string; we normalise later
        low_memory=False,
    )
    return df


# ---------------------------------------------------------------------------
# 2. Column renaming & selection
# ---------------------------------------------------------------------------

COLUMN_MAP = {
    "AUTORIA": "autoria",
    "ORIENTADOR": "orientador",
    "TITULO": "titulo",
    "ANO": "ano",
    "FOMENTO": "fomento",
    "PUBLICADORA": "publicador",
    "LOCAL": "local",
    "TIPO": "tipo",
    "PROGRAMA": "programa",
    "NIVEL": "nivel",
    "PAGINAS": "paginas",
    "RESUMO_COMPLETO": "resumo",
    "IDIOMA": "idioma",
    "URI": "uri",
    "PALAVRAS_CHAVES": "palavras_chave",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns to snake_case following the required output specification.
    Any columns not listed in COLUMN_MAP are lowercased and spaces replaced
    with underscores.
    """
    df = df.rename(columns=COLUMN_MAP)
    # Normalise any remaining columns not in the map
    df.columns = [
        COLUMN_MAP.get(c, re.sub(r"\s+", "_", c.strip().lower()))
        for c in df.columns
    ]
    return df


# ---------------------------------------------------------------------------
# 3. Text normalisation
# ---------------------------------------------------------------------------

def _normalise_text(value: str) -> str:
    """
    Strip a single string value:
      - Replace line breaks, carriage returns, tabs with a single space
      - Collapse multiple consecutive spaces
      - Strip leading/trailing whitespace
    """
    if not isinstance(value, str):
        return value
    # Replace common whitespace variants with a space
    value = re.sub(r"[\r\n\t\xa0\u200b\u00a0]+", " ", value)
    # Collapse multiple spaces
    value = re.sub(r" {2,}", " ", value)
    return value.strip()


def normalise_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply whitespace normalisation to all object (string) columns."""
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    _map = getattr(pd.DataFrame, "map", None) or getattr(pd.DataFrame, "applymap")
    df[str_cols] = df[str_cols].apply(lambda col: col.map(_normalise_text))
    return df


# ---------------------------------------------------------------------------
# 4. Handling missing / placeholder values
# ---------------------------------------------------------------------------

# Regex pattern matching common placeholder values (case-insensitive)
_PLACEHOLDER_RE = re.compile(
    r"^\s*("
    r"resumo\s+n[aã]o\s+dispon[ií]vel"
    r"|resumo"
    r"|abstract"
    r"|n[aã]o\s+dispon[ií]vel"
    r"|sem\s+resumo"
    r"|indispon[ií]vel"
    r")\s*$",
    re.IGNORECASE,
)


def _is_missing(value) -> bool:
    """Return True when a value should be treated as missing."""
    if value is None:
        return True
    if not isinstance(value, str):
        return pd.isna(value)
    stripped = value.strip()
    if stripped == "" or stripped.lower() in ("nan", "none"):
        return True
    if _PLACEHOLDER_RE.match(stripped):
        return True
    return False


def standardise_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace all placeholder/empty values with NaN across the entire DataFrame.
    """
    return df.apply(lambda col: col.map(lambda v: None if _is_missing(v) else v))


def drop_missing_required(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows where `resumo` or `uri` is missing."""
    before = len(df)
    df = df[df["resumo"].notna() & df["uri"].notna()].copy()
    after = len(df)
    print(f"[drop_missing_required] Dropped {before - after} rows "
          f"(missing resumo or uri). Remaining: {after}")
    return df


# ---------------------------------------------------------------------------
# 5. Column-specific cleaning
# ---------------------------------------------------------------------------

def _normalise_separator(value: str, sep_in: str, sep_out: str = "; ") -> str:
    """
    Standardise the separator inside a multi-value string.
    Handles extra spaces around the separator.
    """
    if not isinstance(value, str):
        return value
    parts = [p.strip() for p in value.split(sep_in)]
    parts = [p for p in parts if p]
    return sep_out.join(parts)


def clean_autoria(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise author separator to '; '."""
    df["autoria"] = df["autoria"].apply(
        lambda v: _normalise_separator(v, ";") if isinstance(v, str) else v
    )
    return df


def clean_palavras_chave(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise keyword separator to '; '."""
    df["palavras_chave"] = df["palavras_chave"].apply(
        lambda v: _normalise_separator(v, ";") if isinstance(v, str) else v
    )
    return df


def clean_tipo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalise TIPO inconsistency:
    'Trabalho de conclusão de Curso' → 'Trabalho de conclusão de curso'
    """
    if "tipo" in df.columns:
        df["tipo"] = df["tipo"].str.strip().str.replace(
            r"[Cc]urso$", "curso", regex=True
        )
    return df


def clean_resumo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove inline semicolons used as paragraph separators inside the resumo
    field (an artifact of the source data: '; ' between sections).
    Replace them with a space so the text reads continuously.
    
    NOTE: We only replace '; ' at sentence boundaries inside resumo —
    not at the start/end (which would already be stripped).
    """
    # The UFRGS source uses '; ' to join abstract paragraphs.
    # Replace with a space to get a clean continuous text.
    df["resumo"] = df["resumo"].apply(
        lambda v: re.sub(r"\s*;\s+", " ", v) if isinstance(v, str) else v
    )
    return df


def normalize_colons(series: pd.Series) -> pd.Series:
    """
    Replace any sequence of colons (with optional surrounding whitespace)
    by a single ': '.
    """
    return series.str.replace(r"\s*:+\s*", ": ", regex=True)


def clean_title(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace any sequence of colons (with optional surrounding whitespace)
    by a single ': '.
    """
    df["titulo"] = normalize_colons(df["titulo"])
    return df


# ---------------------------------------------------------------------------
# 6. Deduplication
# ---------------------------------------------------------------------------

def _title_key(title: str) -> str:
    """Normalise a title for fuzzy duplicate detection."""
    if not isinstance(title, str):
        return ""
    # Lowercase, remove punctuation, collapse spaces
    t = title.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def deduplicate_title(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect and resolve duplicate documents based on normalised title.

    Strategy:
      1. Compute a normalised title key for fuzzy matching.
      2. Group rows by this key.
      3. Within each group:
         - Drop entries without a meaningful resumo.
         - Among remaining, keep the most recent (highest ANO).
         - If ANO is unavailable, keep the first occurrence.
    """
    df = df.copy()
    df["_title_key"] = df["titulo"].apply(_title_key)

    # Convert ANO to numeric for comparison
    df["_ano_num"] = pd.to_numeric(df.get("ano", pd.Series(dtype=float)), errors="coerce")

    kept_indices = []

    for _key, group in df.groupby("_title_key", sort=False):
        # Filter out rows with missing resumo (already dropped, but be safe)
        valid = group[group["resumo"].notna()]
        if valid.empty:
            # If all have missing resumo, keep the first
            kept_indices.append(group.index[0])
            continue

        if len(valid) == 1:
            kept_indices.append(valid.index[0])
            continue

        # Keep the most recent; NaT/NaN sorts last — prefer filled ANO
        valid_sorted = valid.sort_values("_ano_num", ascending=False, na_position="last")
        kept_indices.append(valid_sorted.index[0])

    before = len(df)
    df = df.loc[kept_indices].copy()
    df.drop(columns=["_title_key", "_ano_num"], inplace=True)
    after = len(df)
    print(f"[deduplicate] Removed {before - after} duplicate rows. Remaining: {after}")
    return df


def deduplicate_abstract(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect and resolve duplicate documents based on normalised title.

    Strategy:
      1. Compute a normalised title key for fuzzy matching.
      2. Group rows by this key.
      3. Within each group:
         - Drop entries without a meaningful resumo.
         - Among remaining, keep the most recent (highest ANO).
         - If ANO is unavailable, keep the first occurrence.
    """
    df = df.copy()
    df["_title_key"] = df["resumo"].apply(_title_key)

    # Convert ANO to numeric for comparison
    df["_ano_num"] = pd.to_numeric(df.get("ano", pd.Series(dtype=float)), errors="coerce")

    kept_indices = []

    for _key, group in df.groupby("_title_key", sort=False):
        # Filter out rows with missing resumo (already dropped, but be safe)
        valid = group[group["resumo"].notna()]
        if valid.empty:
            # If all have missing resumo, keep the first
            kept_indices.append(group.index[0])
            continue

        if len(valid) == 1:
            kept_indices.append(valid.index[0])
            continue

        # Keep the most recent; NaT/NaN sorts last — prefer filled ANO
        valid_sorted = valid.sort_values("_ano_num", ascending=False, na_position="last")
        kept_indices.append(valid_sorted.index[0])

    before = len(df)
    df = df.loc[kept_indices].copy()
    df.drop(columns=["_title_key", "_ano_num"], inplace=True)
    after = len(df)
    print(f"[deduplicate] Removed {before - after} duplicate rows. Remaining: {after}")
    return df


# ---------------------------------------------------------------------------
# 7. Final column ordering & type cleanup
# ---------------------------------------------------------------------------

# Columns that must be present in the output (in preferred order)
REQUIRED_COLUMNS = [
    "autoria",
    "titulo",
    "uri",
    "resumo",
    "publicador",
    "palavras_chave",
]

PREFERRED_ORDER = REQUIRED_COLUMNS + [
    "orientador",
    "ano",
    "tipo",
    "nivel",
    "programa",
    "idioma",
    "paginas",
    "local",
    "fomento",
]


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Place required columns first, then remaining columns alphabetically."""
    present_required = [c for c in REQUIRED_COLUMNS if c in df.columns]
    preferred_rest = [c for c in PREFERRED_ORDER if c in df.columns and c not in present_required]
    remaining = sorted([c for c in df.columns if c not in PREFERRED_ORDER])
    final_order = present_required + preferred_rest + remaining
    return df[final_order]


def reset_index_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Reset the DataFrame index after all filtering steps."""
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 8. ETL pipeline orchestrator
# ---------------------------------------------------------------------------

def run_etl(filepath: str) -> pd.DataFrame:
    """
    Full ETL pipeline:
      1. Load file (auto-detect encoding & delimiter)
      2. Rename columns to snake_case
      3. Normalise whitespace in all text fields
      4. Standardise missing / placeholder values to NaN
      5. Drop rows missing `resumo` or `uri`
      6. Clean specific columns (autoria, palavras_chave, tipo, resumo)
      7. Deduplicate by normalised title
      8. Reorder columns and reset index

    Returns
    -------
    pd.DataFrame
        Cleaned and standardised bibliographic dataset.
    """
    print(f"\n{'='*60}")
    print(f"ETL pipeline started for: {filepath}")
    print(f"{'='*60}\n")

    # Step 1 – Load
    print("[1/8] Loading file...")
    df = load_file(filepath)
    print(f"      Loaded {len(df):,} rows × {len(df.columns)} columns.")

    # Step 2 – Rename columns
    print("[2/8] Renaming columns...")
    df = rename_columns(df)
    print(f"      Columns: {df.columns.tolist()}")

    # Step 3 – Normalise whitespace
    print("[3/8] Normalising whitespace in text columns...")
    df = normalise_text_columns(df)

    # Step 4 – Standardise missing values
    print("[4/8] Standardising missing / placeholder values...")
    df = standardise_missing(df)

    # Step 5 – Drop rows missing required fields
    print("[5/8] Dropping rows with missing `resumo` or `uri`...")
    df = drop_missing_required(df)

    # Step 6 – Column-specific cleaning
    print("[6/8] Applying column-specific cleaning...")
    df = clean_autoria(df)
    df = clean_palavras_chave(df)
    df = clean_tipo(df)
    df = clean_resumo(df)
    df = clean_title(df)

    # Step 7 – Deduplication
    print("[7/8] Deduplicating records by title...")
    df = deduplicate_abstract(df)

    # Step 8 – Final structure
    #print("[8/8] Reordering columns and resetting index...")
    #df = reorder_columns(df)
    #df = reset_index_clean(df)

    print(f"\n{'='*60}")
    print(f"ETL complete. Final dataset: {len(df):,} rows × {len(df.columns)} columns.")
    print(f"Columns: {df.columns.tolist()}")
    print(f"{'='*60}\n")

    return df


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    input_path = sys.argv[1] if len(sys.argv) > 1 else "ufrgs.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "ufrgs_clean.csv"

    cleaned_df = run_etl(input_path)
    cleaned_df.to_csv(output_path, index=False, encoding="utf-8-sig", sep=";")
    print(f"Saved cleaned dataset to: {output_path}")
