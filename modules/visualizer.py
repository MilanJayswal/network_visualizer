import json
import streamlit.components.v1 as components


def render_network(nodes, edges, height_px=760):
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    html = f"""
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
                grid-template-columns: 78% 22%;
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
                overflow: auto;
                background: #ffffff;
                font-size: 13px;
            }}

            .meta-title {{
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
            }}

            .meta-block {{
                margin-bottom: 10px;
                padding-bottom: 8px;
                border-bottom: 1px solid #eee;
            }}

            .key {{
                font-weight: bold;
                color: #333;
            }}

            pre {{
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 12px;
            }}
        </style>
    </head>

    <body>
        <div id="layout">
            <div id="network"></div>
            <div id="metadata">
                <div class="meta-title">Metadata Panel</div>
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
                size: 12,
                metadata: n.metadata
            }})));

            const edges = new vis.DataSet(edgesData.map(e => ({{
                id: e.id,
                from: e.from,
                to: e.to,
                label: e.label,
                arrows: e.arrows,
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
                        iterations: 200
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
                    }},
                    borderWidth: 1
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

            function renderObject(obj) {{
                let html = "";

                for (const key in obj) {{
                    const value = obj[key];

                    html += "<div class='meta-block'>";
                    html += "<div class='key'>" + key + "</div>";

                    if (Array.isArray(value) || typeof value === "object") {{
                        html += "<pre>" + JSON.stringify(value, null, 2) + "</pre>";
                    }} else {{
                        html += "<div>" + value + "</div>";
                    }}

                    html += "</div>";
                }}

                return html;
            }}

            network.on("click", function(params) {{
                const panel = document.getElementById("metadata");

                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const node = nodes.get(nodeId);

                    panel.innerHTML =
                        "<div class='meta-title'>Node Metadata</div>" +
                        renderObject(node.metadata);
                }}

                else if (params.edges.length > 0) {{
                    const edgeId = params.edges[0];
                    const edge = edges.get(edgeId);

                    panel.innerHTML =
                        "<div class='meta-title'>Edge / Cluster Metadata</div>" +
                        renderObject(edge.metadata);
                }}

                else {{
                    panel.innerHTML =
                        "<div class='meta-title'>Metadata Panel</div>" +
                        "<div>Click a node or edge.</div>";
                }}
            }});
        </script>
    </body>
    </html>
    """

    components.html(
        html,
        height=height_px,
        scrolling=False
    )
