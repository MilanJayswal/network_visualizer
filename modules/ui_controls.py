import streamlit as st
from modules.filters import build_pathway_options


def sidebar_controls(df):
    st.sidebar.header("Network Controls")

    pathway_labels = build_pathway_options(df)

    selected_pathways = st.sidebar.multiselect(
        "Select pathway(s)",
        options=pathway_labels,
        default=[]
    )

    st.sidebar.divider()

    search_type = st.sidebar.selectbox(
        "Search type",
        options=[
            "None",
            "NodeID",
            "RelationID",
            "ClusterID",
        ]
    )

    if search_type == "NodeID":
        options = sorted(
            set(df["Source_NodeID"].dropna()) |
            set(df["Target_NodeID"].dropna())
        )

    elif search_type == "RelationID":
        options = sorted(df["RelationID"].dropna().unique())

    elif search_type == "ClusterID":
        options = sorted(df["ClusterID"].dropna().unique())

    else:
        options = []

    search_value = None

    if search_type != "None":
        search_value = st.sidebar.selectbox(
            f"Select {search_type}",
            options=options
        )

    return {
        "selected_pathways": selected_pathways,
        "search_type": search_type,
        "search_value": search_value,
    }
