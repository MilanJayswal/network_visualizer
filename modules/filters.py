def split_semicolon(value):
    if value is None:
        return []
    return [x.strip() for x in str(value).split(";") if x.strip()]


def get_pathway_pairs_from_row(row):
    ids = split_semicolon(row["Pathway_ID"])
    names = split_semicolon(row["Pathway_Name"])

    pairs = []

    for i, pid in enumerate(ids):
        pname = names[i] if i < len(names) else ""
        pairs.append((pid, pname))

    return pairs


def build_pathway_options(df):
    pathway_map = {}

    for _, row in df.iterrows():
        for pid, pname in get_pathway_pairs_from_row(row):
            pathway_map[pid] = pname

    return [
        f"{pid} | {pname}"
        for pid, pname in sorted(pathway_map.items())
    ]


def extract_pathway_id(label):
    return label.split("|")[0].strip()


def row_has_selected_pathway(row, selected_ids):
    row_pathways = split_semicolon(row["Pathway_ID"])
    return any(pid in selected_ids for pid in row_pathways)


def apply_pathway_filter(df, selected_pathways):
    if not selected_pathways:
        return df.copy()

    selected_ids = [extract_pathway_id(x) for x in selected_pathways]

    return df[
        df.apply(lambda row: row_has_selected_pathway(row, selected_ids), axis=1)
    ].copy()


def apply_search_filter(df, full_df, search_type, search_value):
    if search_type == "None" or not search_value:
        return df.copy()

    if search_type == "NodeID":
        # first-degree upstream + downstream
        return df[
            (df["Source_NodeID"] == search_value) |
            (df["Target_NodeID"] == search_value)
        ].copy()

    if search_type == "RelationID":
        return df[df["RelationID"] == search_value].copy()

    if search_type == "ClusterID":
        return df[df["ClusterID"] == search_value].copy()

    return df.copy()
