def extract_pathway_id(label):
    return label.split("|")[0].strip()


def apply_pathway_filter(df, selected_pathways):
    if not selected_pathways:
        return df.copy()

    selected_ids = [extract_pathway_id(x) for x in selected_pathways]

    return df[df["Pathway_ID"].isin(selected_ids)].copy()


def apply_search_filter(df, full_df, search_type, search_value):
    if search_type == "None" or not search_value:
        return df.copy()

    if search_type == "NodeID":
        subset = df[
            (df["Source_NodeID"] == search_value) |
            (df["Target_NodeID"] == search_value)
        ].copy()
        return subset

    if search_type == "RelationID":
        subset = df[df["RelationID"] == search_value].copy()
        return subset

    if search_type == "ClusterID":
        subset = df[df["ClusterID"] == search_value].copy()
        return subset

    return df.copy()
