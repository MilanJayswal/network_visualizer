from collections import defaultdict


def split_semicolon(value):
    if value is None:
        return []
    return [x.strip() for x in str(value).split(";") if x.strip()]


def split_ids(value):
    if not value:
        return []

    value = str(value).replace(",", ";")
    return [x.strip() for x in value.split(";") if x.strip()]


def get_pathway_pairs(row):
    ids = split_semicolon(row["Pathway_ID"])
    names = split_semicolon(row["Pathway_Name"])

    pairs = []

    for i, pid in enumerate(ids):
        pname = names[i] if i < len(names) else ""
        pairs.append({
            "Pathway_ID": pid,
            "Pathway_Name": pname
        })

    return pairs


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

        for p in get_pathway_pairs(row):
            label = f"{p['Pathway_ID']} | {p['Pathway_Name']}"
            node_pathways[source_node].add(label)
            node_pathways[target_node].add(label)

    all_node_ids = sorted(
        set(df["Source_NodeID"].dropna()) |
        set(df["Target_NodeID"].dropna())
    )

    nodes = []

    for node_id in all_node_ids:
        nodes.append({
            "id": node_id,
            "label": node_id,
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
        pathway_seen = {}
        interactions = set()

        for _, row in group.iterrows():
            interactions.add(row["Interaction"])

            edge_metadata_rows.append({
                "RelationID": row["RelationID"],
                "ClusterID": row["ClusterID"],
                "Source_NodeID": row["Source_NodeID"],
                "Target_NodeID": row["Target_NodeID"],
                "Interaction": row["Interaction"],
                "Source": row["Source"],
                "Target": row["Target"],
            })

            for p in get_pathway_pairs(row):
                pathway_seen[p["Pathway_ID"]] = p["Pathway_Name"]

        pathways = [
            {
                "Pathway_ID": pid,
                "Pathway_Name": pname
            }
            for pid, pname in sorted(pathway_seen.items())
        ]

        edges.append({
            "id": cluster_id,
            "from": source_node,
            "to": target_node,
            "label": cluster_id,
            "metadata": {
                "ClusterID": cluster_id,
                "Source_NodeID": source_node,
                "Target_NodeID": target_node,
                "RelationIDs": relation_ids,
                "Interactions": sorted(interactions),
                "Relations": edge_metadata_rows,
                "Pathways": pathways,
            }
        })

    return edges


def build_nodes_edges(df):
    nodes = build_node_metadata(df)
    edges = build_edge_metadata(df)

    all_pathways = set()

    for _, row in df.iterrows():
        for p in get_pathway_pairs(row):
            all_pathways.add(p["Pathway_ID"])

    summary = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "relation_count": len(df),
        "pathway_count": len(all_pathways),
    }

    return nodes, edges, summary
