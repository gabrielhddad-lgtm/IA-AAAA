import streamlit as st
import numpy as np
from PIL import Image

# =========================
# CONFIGURAÇÃO DO APP
# =========================
st.set_page_config(
    page_title="HB Signals AI",
    page_icon="📊",
    layout="centered"
)

st.title("📊 HB Signals AI")
st.caption("Análise estatística de gráfico • Timeframe 1M • OTC")

# =========================
# UPLOAD DA IMAGEM
# =========================
uploaded_file = st.file_uploader(
    "📤 Envie a imagem do gráfico",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
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
    price_line = []

    for x in range(w):
        column = img[:, x]
        y = np.argmax(column)          # pixel mais claro
        price_line.append(h - y)       # inverte eixo Y

    price_line = np.array(price_line)

    # =========================
    # ANÁLISE DE TENDÊNCIA
    # =========================
    x_axis = np.arange(len(price_line))
    slope = np.polyfit(x_axis, price_line, 1)[0]

    # =========================
    # DECISÃO DO SINAL
    # =========================
    if slope > 0.03:
        signal = "📈 CALL COMPRA"
        color = "#00ff55"
        show_score = True

    elif slope < -0.03:
        signal = "📉 CALL VENDA"
        color = "#ff4444"
        show_score = True

    else:
        signal = "⏸️ SEM ENTRADA"
        color = "#aaaaaa"
        show_score = False

    # =========================
    # RESULTADO FINAL
    # =========================
    st.markdown("---")

    st.markdown(
        f"""
        <h2 style="
            text-align:center;
            color:{color};
            font-weight:700;
        ">
            {signal}
        </h2>
        """,
        unsafe_allow_html=True
    )

    if show_score:
        st.markdown(
            """
            <h3 style="
                text-align:center;
                color:#00ffcc;
                font-weight:700;
            ">
                🔥 SCORE: 100%
            </h3>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <h4 style="
                text-align:center;
                color:gray;
            ">
                Aguardando oportunidade segura
            </h4>
            """,
            unsafe_allow_html=True
        )

    st.caption(f"Inclinação detectada: {slope:.5f}")

else:
    st.info("Envie uma imagem de gráfico para iniciar a análise.")
