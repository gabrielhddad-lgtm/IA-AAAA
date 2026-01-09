import streamlit as st
import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np
import cv2
from PIL import Image
from torchvision import models

# -------------------------
# Configurações internas
# -------------------------
class Config:
    crop_x = 0
    crop_y = 0
    crop_w = 800
    crop_h = 600
    img_size = 224
    best_model_path = "best_model.pth"  # Coloque o seu modelo aqui

cfg = Config()
ID2LABEL = {0: "UP", 1: "DOWN", 2: "NEUTRAL"}
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
THRESHOLD_OPERAR = 0.65

# -------------------------
# Carregar modelo
# -------------------------
@st.cache_resource(show_spinner=True)
def load_model():
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 3)
    model.load_state_dict(torch.load(cfg.best_model_path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model

model = load_model()

# -------------------------
# Pré-processamento
# -------------------------
def preprocess(img_pil):
    img = np.array(img_pil)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    x, y, w, h = cfg.crop_x, cfg.crop_y, cfg.crop_w, cfg.crop_h
    cropped = img[y:y+h, x:x+w]
    if cropped.size == 0:
        return None
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(cropped)
    tf = T.Compose([
        T.Resize((cfg.img_size, cfg.img_size)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])
    return tf(pil).unsqueeze(0)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="IA HomeBroker 1m", layout="centered")
st.title("🧠 IA de Leitura de Gráfico – 1 Minuto")
st.markdown("Upload de **print do gráfico (1m)** e análise probabilística.")

uploaded = st.file_uploader("📷 Envie o print do gráfico", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded).convert("RGB")
    st.image(img, caption="Print enviado", use_column_width=True)

    x = preprocess(img)
    if x is None:
        st.error("Erro no crop. Ajuste os valores de crop no código.")
    else:
        with torch.no_grad():
            logits = model(x.to(DEVICE))[0]
            probs = torch.softmax(logits, dim=0).cpu().numpy()

        results = {ID2LABEL[i]: float(probs[i]) for i in range(3)}
        ordered = sorted(results.items(), key=lambda x: -x[1])

        st.subheader("📊 Probabilidades")
        for k, v in ordered:
            st.write(f"**{k}**: {v*100:.1f}%")

        best_label, best_prob = ordered[0]

        st.divider()
        st.subheader("🚦 Leitura da IA")

        if best_prob >= THRESHOLD_OPERAR and best_label != "NEUTRAL":
            if best_label == "UP":
                st.success(f"📈 Tendência de ALTA ({best_prob*100:.1f}%)")
            else:
                st.error(f"📉 Tendência de BAIXA ({best_prob*100:.1f}%)")
            st.markdown("**Condição estatística atendida**")
        else:
            st.warning("⏸️ SEM OPERAÇÃO")
            st.markdown("Probabilidade insuficiente ou mercado neutro")

st.caption("Uso educacional • IA probabilística • Timeframe 1 minuto")
