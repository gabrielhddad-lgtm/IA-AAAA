import streamlit as st
import numpy as np
from PIL import Image

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="HB Signals AI PRO",
    page_icon="📊",
    layout="centered"
)

st.title("📊 HB Signals AI PRO")
st.caption("IA Estatística • Tendência • Pullback • OTC • 1M")

# =========================
# FUNÇÃO OTIMIZADA (CACHE)
# =========================
@st.cache_data(show_spinner=False)
def analyze_chart(image: Image.Image):
    # Reduz imagem (evita travamento)
    image = image.resize((400, int(400 * image.height / image.width)))
    img = np.array(image.convert("L"))

    h, w = img.shape
    price = np.empty(w)

    for x in range(w):
        price[x] = h - np.argmin(img[:, x])

    # Suavização
    smooth = np.convolve(price, np.ones(15) / 15, mode="valid")

    # Métricas
    x_axis = np.arange(len(smooth))
    slope = np.polyfit(x_axis, smooth, 1)[0]
    delta = smooth[-1] - smooth[0]
    volatility = np.std(np.diff(smooth))

    recent = smooth[-12:]
    pullback = recent.max() - recent.min()

    return slope, delta, volatility, pullback

# =========================
# UPLOAD
# =========================
uploaded_file = st.file_uploader(
    "📤 Envie a imagem do gráfico",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gráfico analisado", use_container_width=True)

    with st.spinner("🔍 Analisando gráfico..."):
        slope, delta, volatility, pullback_strength = analyze_chart(image)

    # =========================
    # SCORE BASE
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
    # FILTRO ANTI-LATERAL
    # =========================
    lateral = (
        abs(slope) < 0.015 and
        abs(delta) < 6 and
        pullback_strength > 7
    )

    # =========================
    # MODO PRO TRADER (OCULTO)
    # =========================
    pro_trader = (
        abs(slope) > 0.035 and
        abs(delta) > 14 and
        volatility > 2.5 and
        pullback_strength < 5
    )

    # =========================
    # DECISÃO FINAL
    # =========================
    if lateral:
        signal = "🚫 MERCADO LATERAL"
        color = "#ffaa00"
        score = 35

    elif slope > 0.025 and delta > 10 and volatility > 2:
        signal = "📈 CALL COMPRA"
        color = "#00ff55"

    elif slope < -0.025 and delta < -10 and volatility > 2:
        signal = "📉 CALL VENDA"
        color = "#ff4444"

    else:
        signal = "⏸️ SEM ENTRADA"
        color = "#aaaaaa"
        score = max(score - 20, 40)

    # BOOST PRO TRADER
    if pro_trader and not lateral:
        signal += " 💎 PRO TRADER"
        score = min(score + 12, 99)

    # =========================
    # RESULTADO
    # =========================
    st.markdown("---")
    st.markdown(
        f"<h2 style='text-align:center;color:{color};font-weight:700'>{signal}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<h3 style='text-align:center;color:#00ffcc'>🔥 SCORE: {score}%</h3>",
        unsafe_allow_html=True
    )

    # =========================
    # DIAGNÓSTICO AVANÇADO
    # =========================
    with st.expander("🧠 Diagnóstico Avançado (PRO)"):
        st.write(f"Slope: {slope:.5f}")
        st.write(f"Delta: {delta:.2f}")
        st.write(f"Volatilidade: {volatility:.2f}")
        st.write(f"Pullback: {pullback_strength:.2f}")
        st.write("Mercado Lateral:", lateral)
        st.write("Modo PRO:", pro_trader)
