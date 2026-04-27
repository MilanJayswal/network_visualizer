MAPPING_COLUMNS = [
    "KEGG_ID",
    "Names",
    "EC_Number",
    "Ortholog_IDs",
    "HSA_IDs",
    "Compound_IDs",
    "HSA_Symbols",
    "Compound_Symbols",
    "HSA_Biological_Names",
    "Compound_Biological_Names",
]


def load_mapping_excel(uploaded_file):
    if uploaded_file is None:
        return None

    mapping_df = pd.read_excel(uploaded_file)
    mapping_df.columns = [str(c).strip() for c in mapping_df.columns]

    for col in mapping_df.columns:
        mapping_df[col] = mapping_df[col].apply(clean_cell)

    return mapping_df


def validate_mapping_columns(mapping_df):
    if mapping_df is None:
        return {
            "valid": True,
            "missing": [],
        }

    missing = [col for col in MAPPING_COLUMNS if col not in mapping_df.columns]

    return {
        "valid": len(missing) == 0,
        "missing": missing,
    }
