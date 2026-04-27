import streamlit as st

from modules.data_loader import (
    load_excel,
    validate_columns,
    load_mapping_excel,
    validate_mapping_columns,
)

from modules.ui_controls import sidebar_controls
from modules.filters import apply_pathway_filter, apply_search_filter
from modules.network_builder import build_nodes_edges
from modules.visualizer import render_network


st.set_page_config(
    page_title="Biological Pathway Network Visualizer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        max-width: 100%;
    }
    section[data-testid="stSidebar"] {
        width: 340px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Biological Pathway Network Visualizer")

relation_file = st.file_uploader(
    "Upload relation metadata enriched Excel file",
    type=["xlsx"],
    key="relation_file",
)

mapping_file = st.file_uploader(
    "Upload KEGG ID mapping file",
    type=["xlsx"],
    key="mapping_file",
)

if relation_file is None:
    st.info("Upload your relation metadata enriched file.")
    st.stop()

df = load_excel(relation_file)
validation = validate_columns(df)

if not validation["valid"]:
    st.error("Missing required columns in relation file:")
    st.write(validation["missing"])
    st.stop()

mapping_df = load_mapping_excel(mapping_file)
mapping_validation = validate_mapping_columns(mapping_df)

if not mapping_validation["valid"]:
    st.error("Missing required columns in mapping file:")
    st.write(mapping_validation["missing"])
    st.stop()

controls = sidebar_controls(df)

filtered_df = apply_pathway_filter(
    df=df,
    selected_pathways=controls["selected_pathways"],
)

filtered_df = apply_search_filter(
    df=filtered_df,
    full_df=df,
    search_type=controls["search_type"],
    search_value=controls["search_value"],
)

nodes, edges, summary = build_nodes_edges(
    filtered_df,
    mapping_df=mapping_df,
)

top_left, top_right = st.columns([3, 1])

with top_left:
    st.caption(
        f"Nodes: {summary['node_count']} | "
        f"Edges / ClusterIDs: {summary['edge_count']} | "
        f"Relations: {summary['relation_count']} | "
        f"Pathways: {summary['pathway_count']}"
    )

with top_right:
    st.caption("Click any node or edge inside the network to view metadata.")

render_network(
    nodes=nodes,
    edges=edges,
    height_px=760,
)
