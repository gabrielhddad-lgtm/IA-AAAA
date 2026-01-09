import streamlit as st
import numpy as np
from PIL import Image

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(
    page_title="HB Signals AI PRO",
    page_icon="📊",
    layout="centered"
)

st.title("📊 HB Signals AI PRO")
st.caption("IA estatística • Tendência • Pullback • OTC • 1M")

# =========================
# UPLOAD DA IMAGEM
# =========================
uploaded_file = st.file_uploader(
    "📤 Envie a imagem do gráfico",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    # =========================
    # LEITURA DA IMAGEM
    # =========================
    image = Image.open(uploaded_file).convert("L")
    img = np.array(image)

    st.image(image, caption="Gráfico analisado", use_container_width=True)

    # =========================
    # EXTRAÇÃO DA LINHA DE PREÇO
    # =========================
    h, w = img.shape
    price = []

    for x in range(w):
        col = img[:, x]
        y = np.argmin(col)          # linha do preço (escura)
        price.append(h - y)

    price = np.array(price)

    # =========================
    # SUAVIZAÇÃO (ANTI-RUÍDO)
    # =========================
    smooth = np.convolve(
        price,
        np.ones(20) / 20,
        mode="valid"
    )

    # =========================
    # MÉTRICAS PRO
    # =========================
    x = np.arange(len(smooth))
    slope = np.polyfit(x, smooth, 1)[0]

    delta = smooth[-1] - smooth[0]
    volatility = np.std(np.diff(smooth))

    # Pullback detection
    recent = smooth[-15:]
    pullback_strength = recent.max() - recent.min()

    # =========================
    # SCORE INTELIGENTE
    # =========================
    score = 50

    if abs(slope) > 0.02:
        score += 20
    if abs(delta) > 8:
        score += 15
    if volatility > 2:
        score += 10
    if pullback_strength < 6:
        score += 10

    score = min(score, 98)

    # =========================
    # DECISÃO FINAL
    # =========================
    if slope > 0.025 and delta > 10 and volatility > 2:
        signal = "📈 CALL COMPRA"
        color = "#00ff55"

    elif slope < -0.025 and delta < -10 and volatility > 2:
        signal = "📉 CALL VENDA"
        color = "#ff4444"

    else:
        signal = "⏸️ SEM ENTRADA"
        color = "#aaaaaa"
        score = max(score - 20, 40)

    # =========================
    # RESULTADO NA TELA
    # =========================
    st.markdown("---")

    st.markdown(
        f"""
        <h2 style="text-align:center; color:{color}; font-weight:700;">
            {signal}
        </h2>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <h3 style="text-align:center; color:#00ffcc;">
            🔥 SCORE: {score}%
        </h3>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # DEBUG PRO (OCULTO)
    # =========================
    with st.expander("📊 Detalhes técnicos (PRO)"):
        st.write(f"Inclinação (slope): {slope:.5f}")
        st.write(f"Delta preço: {delta:.2f}")
        st.write(f"Volatilidade: {volatility:.2f}")
        st.write(f"Pullback: {pullback_strength:.2f}")

else:
    st.info("Envie uma imagem de gráfico para iniciar a análise.")
