import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ================================
# VALORES IDEAIS DAS CULTURAS
# ================================
valores_ideais = {
    "Soja": {"pH": 6.0, "P": 12, "K": 80, "Ca": 3.0, "Mg": 1.0, "S": 10, "M.O": 30},
    "Milho": {"pH": 6.0, "P": 15, "K": 100, "Ca": 4.0, "Mg": 1.5, "S": 12, "M.O": 30},
    "Trigo": {"pH": 6.0, "P": 12, "K": 80, "Ca": 3.5, "Mg": 1.3, "S": 10, "M.O": 30}
}

# Mapeamento inteligente para detectar nomes diferentes no arquivo
aliases = {
    "pH": ["ph", "pH", "ph solo"],
    "P": ["p", "fosforo", "fósforo", "p mehlich", "p_mehlich", "p2o5"],
    "K": ["k", "potassio", "potássio", "k2o"],
    "Ca": ["ca", "calcio", "cálcio"],
    "Mg": ["mg", "magnesio", "magnésio"],
    "S": ["s", "enxofre"],
    "M.O": ["m.o", "mo", "materia organica", "matéria orgânica"]
}

# 🔄 Função de conversão de unidades
def converter_unidade(valor, unidade):
    if unidade == "mg/dm³":
        return valor
    elif unidade == "ppm":
        return valor
    elif unidade == "mg/L":
        return valor
    elif unidade == "kg/ha":
        return valor / 2
    else:
        return valor

# ==========================================
# TÍTULO
# ==========================================
st.markdown("<h1 style='color:#2E7D32; text-align:center;'>📊 Web App – Lei do Mínimo para Análise de Solo</h1>", unsafe_allow_html=True)
st.write("")

# ==========================================
# IMPORTAÇÃO + CULTURA
# ==========================================
colA, colB = st.columns([1.2, 1])

with colA:
    st.subheader("📂 Importar análise de solo (opcional)")
    arquivo = st.file_uploader("Envie um arquivo CSV, XLSX, XLS ou TXT", type=["csv", "xlsx", "xls", "txt"])

with colB:
    st.subheader(" Selecione a cultura:")
    cultura = st.selectbox("Cultura:", ["Soja", "Milho", "Trigo"])

ideais = valores_ideais[cultura]

# ==========================================
# CAMPOS MANUAIS + UNIDADE
# ==========================================
st.markdown("### ✏️ Inserção Manual dos Nutrientes")
st.markdown(f"Os valores ideais para **{cultura}** aparecem nos balões verdes ao lado dos campos.")

unidade = st.selectbox("Selecione a unidade dos resultados:", ["mg/dm³", "ppm", "mg/L", "kg/ha"])

def balao_verde(nome, valor_ideal, valor_digitado):
    diferenca = round(valor_ideal - valor_digitado, 2)
    if diferenca > 0:
        texto = f"Ideal: {valor_ideal} | Falta: {diferenca}"
    else:
        texto = f"Ideal: {valor_ideal} | OK"
    return f"""<span style='background-color:#c8f7c5; color:#1b5e20; padding:4px 8px; border-radius:12px; font-size:12px; margin-left:8px; white-space:nowrap;'>{texto}</span>"""

col1, col2, col3 = st.columns(3)

with col1:
    ph = st.number_input("pH (H₂O)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("pH", ideais["pH"], ph), unsafe_allow_html=True)

    p = st.number_input("Fósforo (P)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("P", ideais["P"], p), unsafe_allow_html=True)

with col2:
    k = st.number_input("Potássio (K)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("K", ideais["K"], k), unsafe_allow_html=True)

    ca = st.number_input("Cálcio (Ca)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("Ca", ideais["Ca"], ca), unsafe_allow_html=True)

with col3:
    mg = st.number_input("Magnésio (Mg)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("Mg", ideais["Mg"], mg), unsafe_allow_html=True)

    s = st.number_input("Enxofre (S)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("S", ideais["S"], s), unsafe_allow_html=True)

    mo = st.number_input("Matéria Orgânica (M.O)", min_value=0.0, step=0.1)
    st.markdown(balao_verde("M.O", ideais["M.O"], mo), unsafe_allow_html=True)

# Conversão
valores_digitados = {
    "pH": ph,
    "P": converter_unidade(p, unidade),
    "K": converter_unidade(k, unidade),
    "Ca": ca, "Mg": mg, "S": s, "M.O": mo
}

# ==========================================
# BOTÃO CALCULAR
# ==========================================
st.markdown("---")
if st.button("📈 Gerar Gráfico e Relatório", use_container_width=True):

    niveis = {n: (valores_digitados[n] / ideais[n]) * 100 for n in valores_digitados}
    nutriente_lim = min(niveis, key=niveis.get)

    st.subheader("📉 Gráfico – Lei do Mínimo")
    fig, ax = plt.subplots(figsize=(3, 1))
    barras = ax.bar(niveis.keys(), niveis.values(), width=0.52, edgecolor="black")

    ax.set_ylim(0, 120)
    ax.axhline(100, color="gray", linestyle="--", linewidth=1)

    for i, bar in enumerate(barras):
        nutr = list(niveis.keys())[i]
        if niveis[nutr] < 100:
            bar.set_color("#D32F2F")
        else:
            bar.set_color("#2E7D32")

    st.pyplot(fig)

    st.subheader(" Relatório da Análise:", divider="green")
    deficientes = [n for n, v in niveis.items() if v < 100]

    if len(deficientes) == 0:
        st.success("O solo não apresenta deficiências nutricionais em relação aos valores ideais desta cultura.")
    else:
        texto = "O solo apresenta deficiência em: " + ", ".join(deficientes)
        texto += f". O nutriente mais limitante é **{nutriente_lim}**."
        st.warning(texto)

    st.write("### Interpretação Geral")
    st.write("""
    A Lei do Mínimo indica que o crescimento das plantas é limitado pelo nutriente que estiver
    em menor quantidade em relação ao ideal. Esses nutrientes abaixo do ideal podem comprometer
    o desenvolvimento da cultura escolhida. Recomenda-se avaliar a necessidade de correção conforme
    orientações técnicas para a cultura escolhida.
    """)

# ==========================================
# RODAPÉ
# ==========================================
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:green; font-size:16px;'>Desenvolvido por <b>Ketlhin Nezi</b> e <b>Gabrielly Pulga</b> - Academicas do curso de Big Data no Agronegócio.</p> ", unsafe_allow_html=True)
