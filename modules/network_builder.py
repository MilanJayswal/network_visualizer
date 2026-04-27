from collections import defaultdict


def split_semicolon(value):
    if value is None:
        return []
    return [x.strip() for x in str(value).split(";") if x.strip()]


def normalize_kegg_id(value):
    value = str(value).strip()

    if ":" in value:
        return value.split(":")[-1].strip()

    return value


def split_ids(value):
    if not value:
        return []

    value = str(value).replace(",", ";")
    ids = []

    for x in value.split(";"):
        x = x.strip()
        if x:
            ids.append(x)

    return ids


def get_pathway_pairs(row):
    ids = split_semicolon(row["Pathway_ID"])
    names = split_semicolon(row["Pathway_Name"])

    pairs = []

    for i, pid in enumerate(ids):
        pname = names[i] if i < len(names) else ""
        pairs.append({
            "Pathway_ID": pid,
            "Pathway_Name": pname,
        })

    return pairs


def build_mapping_lookup(mapping_df):
    if mapping_df is None:
        return {}

    lookup = {}

    for _, row in mapping_df.iterrows():
        raw_id = str(row["KEGG_ID"]).strip()
        norm_id = normalize_kegg_id(raw_id)

        lookup[norm_id] = {
            "KEGG_ID": raw_id,
            "Names": row.get("Names", ""),
            "EC_Number": row.get("EC_Number", ""),
            "Ortholog_IDs": row.get("Ortholog_IDs", ""),
            "HSA_IDs": row.get("HSA_IDs", ""),
            "Compound_IDs": row.get("Compound_IDs", ""),
            "HSA_Symbols": row.get("HSA_Symbols", ""),
            "Compound_Symbols": row.get("Compound_Symbols", ""),
            "HSA_Biological_Names": row.get("HSA_Biological_Names", ""),
            "Compound_Biological_Names": row.get("Compound_Biological_Names", ""),
        }

    return lookup


def get_mapping_for_kegg_id(kegg_id, mapping_lookup):
    norm_id = normalize_kegg_id(kegg_id)

    if norm_id in mapping_lookup:
        return mapping_lookup[norm_id]

    return {
        "KEGG_ID": kegg_id,
        "Names": "",
        "EC_Number": "",
        "Ortholog_IDs": "",
        "HSA_IDs": "",
        "Compound_IDs": "",
        "HSA_Symbols": "",
        "Compound_Symbols": "",
        "HSA_Biological_Names": "",
        "Compound_Biological_Names": "",
    }


def build_node_metadata(df, mapping_df=None):
    mapping_lookup = build_mapping_lookup(mapping_df)

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
        kegg_ids = sorted(node_kegg_ids[node_id])

        mapped_ids = [
            get_mapping_for_kegg_id(kid, mapping_lookup)
            for kid in kegg_ids
        ]

        nodes.append({
            "id": node_id,
            "label": node_id,
            "metadata": {
                "NodeID": node_id,
                "KEGG_IDs": kegg_ids,
                "Mapped_IDs": mapped_ids,
                "Pathways": sorted(node_pathways[node_id]),
            },
        })

    return nodes


def build_edge_metadata(df):
    grouped = df.groupby(
        ["ClusterID", "Source_NodeID", "Target_NodeID"],
        dropna=False,
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
                "Pathway_Name": pname,
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
            },
        })

    return edges


def build_nodes_edges(df, mapping_df=None):
    nodes = build_node_metadata(df, mapping_df=mapping_df)
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
