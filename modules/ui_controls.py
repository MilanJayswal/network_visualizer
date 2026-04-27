import streamlit as st


def sidebar_controls(df):
    st.sidebar.header("Network Controls")

    pathway_options = (
        df[["Pathway_ID", "Pathway_Name"]]
        .drop_duplicates()
        .sort_values(["Pathway_ID", "Pathway_Name"])
    )

    pathway_labels = [
        f"{row.Pathway_ID} | {row.Pathway_Name}"
        for row in pathway_options.itertuples(index=False)
    ]

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

    st.sidebar.divider()

    st.sidebar.markdown(
        """
        **Logic used**

        - Node search = first-degree neighborhood  
        - RelationID search = selected relation edge  
        - ClusterID search = all relations inside that cluster  
        - Visual edge = ClusterID  
        """
    )

    return {
        "selected_pathways": selected_pathways,
        "search_type": search_type,
        "search_value": search_value,
    }
