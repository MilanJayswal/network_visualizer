import pandas as pd


REQUIRED_COLUMNS = [
    "RelationID",
    "ClusterID",
    "Source_NodeID",
    "Target_NodeID",
    "Interaction",
    "Source",
    "Target",
    "Pathway_ID",
    "Pathway_Name",
]


def clean_cell(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def load_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)

    df.columns = [str(c).strip() for c in df.columns]

    for col in df.columns:
        df[col] = df[col].apply(clean_cell)

    return df


def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    return {
        "valid": len(missing) == 0,
        "missing": missing,
    }
