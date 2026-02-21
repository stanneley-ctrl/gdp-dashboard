import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ─── Helper ────────────────────────────────────────────────────────────────────
def hex_to_rgba(hex_color, alpha=0.7):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c*2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ─── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Démo Streamlit", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stMetric { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); border-radius: 12px; padding: 1rem 1.2rem; }
    .stMetric label { color: #94a3b8 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important; }
    section[data-testid="stSidebar"] { background: #0f172a; }
    section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .section-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.15em; margin: 2rem 0 1rem 0; border-left: 3px solid #3b82f6; padding-left: 0.75rem; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Contrôleurs")
    st.markdown("---")
    st.markdown("### 📅 Période")
    annee_debut, annee_fin = st.select_slider("Années", options=list(range(2010, 2031)), value=(2015, 2024))
    st.markdown("### 🏭 Secteurs")
    secteurs = st.multiselect("Sélectionner les secteurs",
        ["Énergie", "Transport", "Agriculture", "Industrie", "Bâtiment", "Déchets"],
        default=["Énergie", "Transport", "Industrie"])
    st.markdown("### ⚙️ Scénarios")
    scenario = st.radio("Trajectoire", ["Tendanciel", "Modéré", "Ambitieux", "Neutralité carbone"], index=1)
    st.markdown("### 🔧 Paramètres")
    taux_reduction = st.slider("Taux de réduction annuel (%)", 0, 15, 5)
    budget_carbone = st.slider("Budget carbone (MtCO₂eq)", 100, 1000, 400, step=50)
    facteur_rebond = st.slider("Effet rebond (%)", 0, 50, 10)
    st.markdown("### 🎨 Affichage")
    afficher_tendance = st.toggle("Ligne de tendance", value=True)
    afficher_cible = st.toggle("Afficher la cible 2050", value=True)

if not secteurs:
    st.warning("Sélectionne au moins un secteur dans la sidebar.")
    st.stop()

# ─── Données ──────────────────────────────────────────────────────────────────
np.random.seed(42)
annees = list(range(annee_debut, annee_fin + 1))
n = len(annees)
mult = {"Tendanciel": 1.0, "Modéré": 0.75, "Ambitieux": 0.5, "Neutralité carbone": 0.25}[scenario]
base_reduction = (1 - taux_reduction / 100)

couleurs_secteurs = {
    "Énergie": "#3b82f6", "Transport": "#f59e0b", "Agriculture": "#10b981",
    "Industrie": "#ef4444", "Bâtiment": "#8b5cf6", "Déchets": "#6b7280"
}

data_secteurs = {}
for s in secteurs:
    base = np.random.randint(80, 200)
    data_secteurs[s] = [base * (base_reduction ** i) * mult + np.random.normal(0, 3) for i in range(n)]

df = pd.DataFrame(data_secteurs, index=annees)
df.index.name = "Année"

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🌿 Tableau de bord Émissions Carbone")
st.markdown(f"*Scénario : **{scenario}** · Réduction annuelle : **{taux_reduction}%** · Budget : **{budget_carbone} MtCO₂eq***")
st.markdown("---")

# ─── KPIs ─────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
total_debut = df.iloc[0].sum()
total_fin = df.iloc[-1].sum()
reduction_pct = ((total_fin - total_debut) / total_debut) * 100
budget_restant = budget_carbone - df.sum().sum() / 10

with col1: st.metric("Émissions initiales", f"{total_debut:.0f} MtCO₂", f"{annee_debut}")
with col2: st.metric("Émissions finales", f"{total_fin:.0f} MtCO₂", f"{annee_fin}")
with col3: st.metric("Réduction totale", f"{abs(reduction_pct):.1f}%", f"{'▼' if reduction_pct < 0 else '▲'} {abs(reduction_pct):.1f}%")
with col4: st.metric("Budget restant", f"{budget_restant:.0f} MtCO₂")

st.markdown("")

LAYOUT = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)",
              font=dict(family="Inter", color="#e2e8f0"), margin=dict(l=0, r=0, t=40, b=0),
              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), hovermode="x unified")

# ─── Ligne + Aire ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Évolution temporelle</div>', unsafe_allow_html=True)
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_line = go.Figure()
    for s in secteurs:
        fig_line.add_trace(go.Scatter(x=annees, y=df[s], name=s, mode='lines+markers',
            line=dict(width=2.5, color=couleurs_secteurs.get(s, "#888888")), marker=dict(size=5),
            hovertemplate=f"<b>{s}</b> : %{{y:.1f}} MtCO₂<extra></extra>"))
    if afficher_tendance:
        fig_line.add_trace(go.Scatter(x=annees, y=df.sum(axis=1), name="Total", mode='lines',
            line=dict(width=3, dash='dot', color='white'),
            hovertemplate="<b>Total</b> : %{y:.1f} MtCO₂<extra></extra>"))
    if afficher_cible and annee_fin >= 2030:
        fig_line.add_hline(y=budget_carbone * 0.1, line_dash="dash", line_color="#f59e0b",
                           annotation_text="Cible 2050", annotation_position="right")
    fig_line.update_layout(**LAYOUT, title=dict(text="Émissions par secteur", font=dict(size=14, family="Syne")))
    st.plotly_chart(fig_line, use_container_width=True)

with col_g2:
    fig_area = go.Figure()
    for s in secteurs:
        c = couleurs_secteurs.get(s, "#888888")
        fig_area.add_trace(go.Scatter(x=annees, y=df[s], name=s, stackgroup='one',
            line=dict(width=0.5, color=c), fillcolor=hex_to_rgba(c, 0.7),
            hovertemplate=f"<b>{s}</b> : %{{y:.1f}} MtCO₂<extra></extra>"))
    fig_area.update_layout(**LAYOUT, title=dict(text="Répartition empilée", font=dict(size=14, family="Syne")))
    st.plotly_chart(fig_area, use_container_width=True)

# ─── Barres + Donut ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Répartition & Comparaison</div>', unsafe_allow_html=True)
col_g3, col_g4 = st.columns([2, 1])

with col_g3:
    colors = [couleurs_secteurs.get(s, "#888888") for s in secteurs]
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name=str(annee_debut), x=secteurs, y=[df[s].iloc[0] for s in secteurs], marker_color=colors, opacity=0.45))
    fig_bar.add_trace(go.Bar(name=str(annee_fin), x=secteurs, y=[df[s].iloc[-1] for s in secteurs], marker_color=colors, opacity=1.0))
    layout_bar = {k: v for k, v in LAYOUT.items() if k != 'hovermode'}
    fig_bar.update_layout(**layout_bar, barmode='group',
                          title=dict(text=f"Comparaison {annee_debut} vs {annee_fin}", font=dict(size=14, family="Syne")))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g4:
    fig_pie = go.Figure(go.Pie(
        labels=secteurs, values=[df[s].mean() for s in secteurs], hole=0.5,
        marker_colors=[couleurs_secteurs.get(s, "#888888") for s in secteurs],
        textfont=dict(family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value:.1f} MtCO₂ moy. · %{percent}<extra></extra>"))
    fig_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#e2e8f0"), margin=dict(l=0, r=0, t=40, b=0), showlegend=False,
        title=dict(text="Part moyenne", font=dict(size=14, family="Syne")),
        annotations=[dict(text="Moy.", x=0.5, y=0.5, font_size=13, showarrow=False, font_color="#94a3b8")])
    st.plotly_chart(fig_pie, use_container_width=True)

# ─── Scatter + Heatmap ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔬 Analyse avancée</div>', unsafe_allow_html=True)
col_g5, col_g6 = st.columns(2)

with col_g5:
    reductions = [((df[s].iloc[-1] - df[s].iloc[0]) / df[s].iloc[0]) * 100 for s in secteurs]
    moyennes = [df[s].mean() for s in secteurs]
    tailles = [df[s].iloc[0] for s in secteurs]
    fig_scatter = go.Figure(go.Scatter(
        x=reductions, y=moyennes, mode='markers+text', text=secteurs, textposition="top center",
        marker=dict(size=[max(t / 5, 8) for t in tailles],
                    color=[couleurs_secteurs.get(s, "#888888") for s in secteurs],
                    opacity=0.85, line=dict(width=1, color='white')),
        hovertemplate="<b>%{text}</b><br>Réduction : %{x:.1f}%<br>Moyenne : %{y:.1f} MtCO₂<extra></extra>"))
    fig_scatter.add_vline(x=0, line_dash="dash", line_color="#475569")
    layout_sc = {k: v for k, v in LAYOUT.items() if k not in ('hovermode', 'legend')}
    fig_scatter.update_layout(**layout_sc, title=dict(text="Réduction vs Niveau moyen", font=dict(size=13, family="Syne")),
                              xaxis_title="Réduction (%)", yaxis_title="Émissions moyennes (MtCO₂)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_g6:
    df_heat = df.T
    df_heat.columns = [str(a) for a in annees]
    fig_heat = go.Figure(go.Heatmap(z=df_heat.values, x=df_heat.columns, y=df_heat.index,
        colorscale="Blues", reversescale=True,
        hovertemplate="<b>%{y}</b> · %{x}<br>%{z:.1f} MtCO₂<extra></extra>",
        colorbar=dict(title="MtCO₂", tickfont=dict(family="Inter"))))
    layout_hm = {k: v for k, v in LAYOUT.items() if k not in ('hovermode', 'legend')}
    fig_heat.update_layout(**layout_hm, title=dict(text="Heatmap émissions", font=dict(size=14, family="Syne")))
    st.plotly_chart(fig_heat, use_container_width=True)

# ─── Tableau ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Données brutes</div>', unsafe_allow_html=True)
with st.expander("Afficher le tableau de données"):
    st.dataframe(df.style.format("{:.1f}").background_gradient(cmap='Blues_r', axis=None), use_container_width=True)

st.markdown("---")
st.caption("Démo Streamlit · Données simulées à titre illustratif")
