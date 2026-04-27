from collections import defaultdict


def split_ids(value):
    if not value:
        return []

    value = str(value).replace(",", ";")
    parts = []

    for token in value.split(";"):
        token = token.strip()
        if token:
            parts.append(token)

    return parts


def build_node_metadata(df):
    node_kegg_ids = defaultdict(set)
    node_pathways = defaultdict(set)

    for _, row in df.iterrows():
        source_node = row["Source_NodeID"]
        target_node = row["Target_NodeID"]

        for kid in split_ids(row["Source"]):
            node_kegg_ids[source_node].add(kid)

        for kid in split_ids(row["Target"]):
            node_kegg_ids[target_node].add(kid)

        pathway_label = f"{row['Pathway_ID']} | {row['Pathway_Name']}"

        node_pathways[source_node].add(pathway_label)
        node_pathways[target_node].add(pathway_label)

    nodes = []

    all_node_ids = sorted(
        set(df["Source_NodeID"].dropna()) |
        set(df["Target_NodeID"].dropna())
    )

    for node_id in all_node_ids:
        nodes.append({
            "id": node_id,
            "label": node_id,
            "title": node_id,
            "metadata": {
                "NodeID": node_id,
                "KEGG_IDs": sorted(node_kegg_ids[node_id]),
                "Pathways": sorted(node_pathways[node_id]),
            }
        })

    return nodes


def build_edge_metadata(df):
    grouped = df.groupby(
        ["ClusterID", "Source_NodeID", "Target_NodeID"],
        dropna=False
    )

    edges = []

    for (cluster_id, source_node, target_node), group in grouped:
        relation_ids = sorted(group["RelationID"].unique())

        edge_metadata_rows = []

        for _, row in group.iterrows():
            edge_metadata_rows.append({
                "RelationID": row["RelationID"],
                "ClusterID": row["ClusterID"],
                "Source_NodeID": row["Source_NodeID"],
                "Target_NodeID": row["Target_NodeID"],
                "Interaction": row["Interaction"],
                "Source": row["Source"],
                "Target": row["Target"],
                "Pathway_ID": row["Pathway_ID"],
                "Pathway_Name": row["Pathway_Name"],
            })

        edges.append({
            "id": cluster_id,
            "from": source_node,
            "to": target_node,
            "label": cluster_id,
            "arrows": "to",
            "metadata": {
                "ClusterID": cluster_id,
                "Source_NodeID": source_node,
                "Target_NodeID": target_node,
                "RelationIDs": relation_ids,
                "Relations": edge_metadata_rows,
            }
        })

    return edges


def build_nodes_edges(df):
    nodes = build_node_metadata(df)
    edges = build_edge_metadata(df)

    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "relation_count": len(df),
        "pathway_count": df["Pathway_ID"].nunique(),
    }

    return nodes, edges, summary
