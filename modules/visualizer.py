import json
import html
import streamlit.components.v1 as components


def render_network(nodes, edges, height_px=760):
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>

        <style>
            html, body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
                font-family: Arial, sans-serif;
                background: #ffffff;
            }}

            #layout {{
                display: grid;
                grid-template-columns: 76% 24%;
                height: {height_px}px;
                width: 100%;
            }}

            #network {{
                height: {height_px}px;
                border: 1px solid #ddd;
                background: #fafafa;
            }}

            #metadata {{
                height: {height_px}px;
                border: 1px solid #ddd;
                border-left: none;
                padding: 12px;
                overflow-y: auto;
                background: #ffffff;
                font-size: 13px;
            }}

            .title {{
                font-size: 17px;
                font-weight: bold;
                margin-bottom: 12px;
                color: #111;
            }}

            .section {{
                margin-bottom: 14px;
                padding: 10px;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                background: #fafafa;
            }}

            .section-title {{
                font-weight: bold;
                margin-bottom: 6px;
                color: #222;
            }}

            .item {{
                margin-bottom: 4px;
            }}

            .key {{
                font-weight: bold;
            }}

            .chip {{
                display: inline-block;
                padding: 3px 7px;
                margin: 2px;
                border-radius: 12px;
                background: #eef2f7;
                font-size: 12px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 12px;
                margin-top: 6px;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 5px;
                text-align: left;
                vertical-align: top;
            }}

            th {{
                background: #f2f2f2;
            }}
        </style>
    </head>

    <body>
        <div id="layout">
            <div id="network"></div>

            <div id="metadata">
                <div class="title">Metadata</div>
                <div>Click a node or edge.</div>
            </div>
        </div>

        <script>
            const nodesData = {nodes_json};
            const edgesData = {edges_json};

            const nodes = new vis.DataSet(nodesData.map(n => ({{
                id: n.id,
                label: n.label,
                title: "NodeID: " + n.id,
                shape: "dot",
                size: 13,
                metadata: n.metadata
            }})));

            const edges = new vis.DataSet(edgesData.map(e => ({{
                id: e.id,
                from: e.from,
                to: e.to,
                label: e.label,
                arrows: "to",
                metadata: e.metadata,
                smooth: {{
                    enabled: true,
                    type: "dynamic"
                }}
            }})));

            const container = document.getElementById("network");

            const data = {{
                nodes: nodes,
                edges: edges
            }};

            const options = {{
                interaction: {{
                    hover: true,
                    navigationButtons: true,
                    keyboard: true
                }},
                physics: {{
                    enabled: true,
                    stabilization: {{
                        iterations: 250
                    }},
                    barnesHut: {{
                        gravitationalConstant: -30000,
                        springLength: 130,
                        springConstant: 0.04,
                        damping: 0.09
                    }}
                }},
                nodes: {{
                    font: {{
                        size: 12
                    }}
                }},
                edges: {{
                    font: {{
                        size: 10,
                        align: "middle"
                    }},
                    width: 1
                }}
            }};

            const network = new vis.Network(container, data, options);

            network.once("stabilizationIterationsDone", function () {{
                network.setOptions({{ physics: false }});
            }});

            function chips(values) {{
                if (!values || values.length === 0) return "<div>None</div>";

                return values.map(v => "<span class='chip'>" + v + "</span>").join("");
            }}

            function renderNode(meta) {{
                return `
                    <div class="title">Node Metadata</div>

                    <div class="section">
                        <div class="section-title">Node</div>
                        <div class="item"><span class="key">NodeID:</span> ${{meta.NodeID}}</div>
                    </div>

                    <div class="section">
                        <div class="section-title">KEGG IDs</div>
                        ${{chips(meta.KEGG_IDs)}}
                    </div>

                    <div class="section">
                        <div class="section-title">Pathways containing this node</div>
                        ${{chips(meta.Pathways)}}
                    </div>
                `;
            }}

            function renderEdge(meta) {{
                let relationRows = "";

                meta.Relations.forEach(r => {{
                    relationRows += `
                        <tr>
                            <td>${{r.RelationID}}</td>
                            <td>${{r.Interaction}}</td>
                            <td>${{r.Source}}</td>
                            <td>${{r.Target}}</td>
                        </tr>
                    `;
                }});

                let pathwayRows = "";

                if (meta.Pathways) {{
                    meta.Pathways.forEach(p => {{
                        pathwayRows += `
                            <tr>
                                <td>${{p.Pathway_ID}}</td>
                                <td>${{p.Pathway_Name}}</td>
                            </tr>
                        `;
                    }});
                }}

                return `
                    <div class="title">Edge / Cluster Metadata</div>

                    <div class="section">
                        <div class="section-title">Cluster</div>
                        <div class="item"><span class="key">ClusterID:</span> ${{meta.ClusterID}}</div>
                        <div class="item"><span class="key">Source Node:</span> ${{meta.Source_NodeID}}</div>
                        <div class="item"><span class="key">Target Node:</span> ${{meta.Target_NodeID}}</div>
                        <div class="item"><span class="key">Relation count:</span> ${{meta.RelationIDs.length}}</div>
                    </div>

                    <div class="section">
                        <div class="section-title">Relation IDs</div>
                        ${{chips(meta.RelationIDs)}}
                    </div>

                    <div class="section">
                        <div class="section-title">Relations in this cluster</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>RelationID</th>
                                    <th>Interaction</th>
                                    <th>Source KEGG</th>
                                    <th>Target KEGG</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{relationRows}}
                            </tbody>
                        </table>
                    </div>

                    <div class="section">
                        <div class="section-title">Pathways containing this edge</div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Pathway ID</th>
                                    <th>Pathway Name</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{pathwayRows}}
                            </tbody>
                        </table>
                    </div>
                `;
            }}

            network.on("click", function(params) {{
                const panel = document.getElementById("metadata");

                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const node = nodes.get(nodeId);
                    panel.innerHTML = renderNode(node.metadata);
                }}

                else if (params.edges.length > 0) {{
                    const edgeId = params.edges[0];
                    const edge = edges.get(edgeId);
                    panel.innerHTML = renderEdge(edge.metadata);
                }}

                else {{
                    panel.innerHTML =
                        "<div class='title'>Metadata</div><div>Click a node or edge.</div>";
                }}
            }});
        </script>
    </body>
    </html>
    """

    components.html(
        html_code,
        height=height_px,
        scrolling=False
    )
