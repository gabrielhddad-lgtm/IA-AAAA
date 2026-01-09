import streamlit as st
import numpy as np
from PIL import Image

# =========================
# CONFIGURAÇÃO STREAMLIT
# =========================
st.set_page_config(
    page_title="Homebrokee AI",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Homebrokee AI")
st.caption("Análise visual de gráfico • OTC • Binário • Timeframe 1M")

st.divider()

# =========================
# UPLOAD DA IMAGEM
# =========================
uploaded_file = st.file_uploader(
    "📤 Envie o print do gráfico (HomeBroker / OTC)",
    type=["png", "jpg", "jpeg"]
)

# =========================
# FUNÇÃO DE ANÁLISE
# =========================
def analisar_grafico(pil_image):
    # Converter para array
    img = np.array(pil_image)

    # Converter para escala de cinza manualmente
    gray = np.mean(img[:, :, :3], axis=2)

    # Normalizar
    gray = gray / 255.0

    # Região central (onde ficam as velas)
    h, w = gray.shape
    region = gray[int(h*0.3):int(h*0.85), int(w*0.15):int(w*0.9)]

    # Detectar intensidade média (simula força da vela)
    intensidade = np.mean(region)

    # Detectar variação (volatilidade curta)
    variacao = np.std(region)

    # Lógica estatística simples e estável
    if intensidade < 0.48 and variacao > 0.12:
        sinal = "📈 CALL (COMPRA)"
        confianca = 60 + int(variacao * 100)
    elif intensidade > 0.55 and variacao > 0.12:
        sinal = "📉 PUT (VENDA)"
        confianca = 60 + int(variacao * 100)
    else:
        sinal = "⏸ NEUTRO"
        confianca = 50

    # Limitar confiança
    confianca = min(confianca, 75)

    return sinal, confianca

# =========================
# EXECUÇÃO
# =========================
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Gráfico enviado", use_column_width=True)

    if st.button("🔍 Analisar gráfico"):
        with st.spinner("Analisando padrão da próxima vela..."):
            sinal, confianca = analisar_grafico(image)

        st.success("Análise concluída")

        st.markdown("### 🔮 Previsão da próxima vela")
        st.markdown(f"**Resultado:** {sinal}")
        st.markdown(f"**Confiança:** `{confianca}%`")

        st.caption("⚠️ Análise estatística visual. Não é recomendação financeira.")

else:
    st.info("Envie um print de gráfico para iniciar a análise.")
