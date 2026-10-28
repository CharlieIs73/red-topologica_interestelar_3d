import streamlit as st
import numpy as np
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(page_title="Red Topológica Interestelar · 3D", layout="wide")
st.title("Red Topológica Interestelar — prototipo 3D")
st.caption("Modelo exploratorio para visualizar nodos, corredores y perturbaciones. No representa física validada.")

with st.sidebar:
    st.header("Configuración")
    n_nodes = st.slider("Número de nodos", 8, 60, 24, 2)
    k_neighbors = st.slider("Conexiones aproximadas por nodo", 1, 6, 3)
    seed = st.number_input("Semilla aleatoria", min_value=0, max_value=99999, value=12, step=1)
    stiffness = st.slider("Rigidez de corredores", 0.2, 3.0, 1.0, 0.1)
    damping = st.slider("Amortiguamiento", 0.0, 0.95, 0.25, 0.05)
    threshold = st.slider("Umbral de ruptura", 0.5, 3.0, 1.6, 0.1)
    st.divider()
    st.subheader("Perturbación")
    selected_node = st.number_input("Nodo perturbado (ID)", min_value=0, max_value=n_nodes-1, value=0, step=1)
    impulse = st.slider("Intensidad inicial", 0.1, 4.0, 1.8, 0.1)
    steps = st.slider("Pasos de propagación", 0, 20, 5)

@st.cache_data
def build_graph(n, k, seed):
    rng = np.random.default_rng(seed)
    coords = rng.uniform(-10, 10, size=(n, 3))
    graph = nx.Graph()
    for i, p in enumerate(coords):
        graph.add_node(i, pos=p)
    for i in range(n):
        distances = np.linalg.norm(coords - coords[i], axis=1)
        for j in np.argsort(distances)[1:k+1]:
            d = float(distances[j])
            graph.add_edge(i, int(j), length=d, rest=d, stiffness=1.0, strain=0.0, broken=False)
    return graph, coords

G, coords = build_graph(n_nodes, k_neighbors, int(seed))
for _, _, data in G.edges(data=True):
    data["stiffness"] = stiffness

strain = np.zeros(n_nodes)
strain[int(selected_node)] = impulse
broken_edges = set()

for _ in range(steps):
    next_strain = strain * damping
    for u, v, data in G.edges(data=True):
        if data.get("broken"):
            continue
        transfer = min(abs(strain[u]), abs(strain[v])) * 0.12 * stiffness
        next_strain[v] += transfer
        next_strain[u] += transfer
    strain = np.clip(next_strain, 0, 10)
    for u, v, data in G.edges(data=True):
        edge_strain = (strain[u] + strain[v]) / max(0.1, 2 * stiffness)
        data["strain"] = float(edge_strain)
        if edge_strain > threshold:
            data["broken"] = True
            broken_edges.add((u, v))

edge_x, edge_y, edge_z = [], [], []
broken_x, broken_y, broken_z = [], [], []
for u, v, d in G.edges(data=True):
    target = (broken_x, broken_y, broken_z) if d.get("broken") else (edge_x, edge_y, edge_z)
    target[0].extend([coords[u,0], coords[v,0], None])
    target[1].extend([coords[u,1], coords[v,1], None])
    target[2].extend([coords[u,2], coords[v,2], None])

fig = go.Figure()
fig.add_trace(go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode="lines",
    line=dict(color="rgba(100,160,210,0.55)", width=3), hoverinfo="skip", name="Corredores activos"))
fig.add_trace(go.Scatter3d(x=broken_x, y=broken_y, z=broken_z, mode="lines",
    line=dict(color="rgba(230,75,75,0.9)", width=5, dash="dash"), hoverinfo="skip", name="Corredores rotos"))
fig.add_trace(go.Scatter3d(
    x=coords[:,0], y=coords[:,1], z=coords[:,2], mode="markers+text",
    text=[str(i) for i in range(n_nodes)], textposition="top center",
    marker=dict(size=6 + np.minimum(strain, 5)*2, color=strain, colorscale="Plasma",
                showscale=True, colorbar=dict(title="Tensión"), line=dict(width=1, color="white")),
    customdata=np.column_stack([strain, np.array([G.degree(i) for i in range(n_nodes)])]),
    hovertemplate="Nodo %{text}<br>Tensión: %{customdata[0]:.2f}<br>Conexiones: %{customdata[1]}<extra></extra>",
    name="Nodos"))
fig.update_layout(height=680, margin=dict(l=0,r=0,t=25,b=0),
    scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z", aspectmode="cube",
               bgcolor="rgba(10,15,30,0.95)"),
    paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E8EEF8"),
    legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0))

left, right = st.columns([2.2, 1])
with left:
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Estado de la red")
    active_graph = G.copy()
    active_graph.remove_edges_from(list(broken_edges))
    st.metric("Nodos", n_nodes)
    st.metric("Corredores totales", G.number_of_edges())
    st.metric("Corredores marcados como rotos", len(broken_edges))
    st.metric("Componentes conectados", nx.number_connected_components(active_graph))
    st.metric("Tensión máxima", f"{float(np.max(strain)):.2f}")
    st.markdown("**Cómo leerlo**")
    st.markdown("- Los nodos son anclas o puntos de tránsito.\n- Las líneas azules son corredores activos.\n- Las líneas rojas discontinuas representan corredores que superaron el umbral.\n- El color y tamaño del nodo indican la tensión estimada.")
    st.warning("La propagación y la ruptura son reglas heurísticas para experimentar, no leyes físicas.")

st.divider()
st.subheader("Prueba rápida")
st.write("Cambia la semilla para generar otra geometría, elige un nodo e incrementa la intensidad para explorar cómo cambia la red.")
st.caption("Consejo: puedes rotar, acercar y alejar la escena con el ratón.")
