import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Configurazione Dashboard
st.set_page_config(page_title="CAS Maintenance Predictor", layout="wide")

st.title("🏗️ CAS Asset Management Tool")
st.subheader("Modello Parametrico di Budgeting Manutentivo")

# --- INPUT SIDEBAR ---
with st.sidebar:
    st.header("📊 Dati Immobile")
    area = st.number_input("Superficie Lorda (mq)", value=600)
    guests = st.number_input("Capacità (Ospiti)", value=45)
    year = st.number_input("Anno Costruzione", value=1990, max_value=2026)
    revenue = st.number_input("Fatturato Annuo (€)", value=450000)
    
    st.header("⚙️ Flag Impianti Complessi")
    f_elev = st.checkbox("Ascensore")
    f_hvac = st.checkbox("Climatizzazione")
    f_vmc = st.checkbox("VMC")
    f_fire = st.checkbox("Antincendio Attivo")
    f_cctv = st.checkbox("CCTV/Allarme")

# --- MOTORE DI CALCOLO ---
VRN = 1050
asset_val = area * VRN
age = 2026 - year

# Coefficienti
kv = 1.0 if age < 15 else (1.2 if age <= 30 else 1.4)
kd = 1.0 if (area/guests) > 20 else (1.25 if (area/guests) >= 15 else 1.5)

# Delta Aliquote
d_mo = (0.0025 if f_elev else 0) + (0.0035 if f_hvac else 0) + (0.0015 if f_vmc else 0) + (0.0010 if f_fire else 0) + (0.0005 if f_cctv else 0)
d_as = (0.0015 if f_elev else 0) + (0.0025 if f_hvac else 0) + (0.0010 if f_vmc else 0) + (0.0005 if f_fire else 0) + (0.0010 if f_cctv else 0)

# Risultati
mo_fin = (asset_val * kv * kd * 0.014) + (asset_val * d_mo)
as_fin = (asset_val * kv * 0.007) + (asset_val * d_as)
total = mo_fin + as_fin
incidenza = (total / revenue) * 100

# --- LAYOUT VISUALE ---
c1, c2, c3 = st.columns(3)
c1.metric("Valore Ricostruzione", f"€ {asset_val:,.0f}")
c2.metric("Budget Annuo", f"€ {total:,.0f}")
c3.metric("Incidenza/Fatturato", f"{incidenza:.2f}%", 
          delta="CRITICO" if incidenza > 10 else "OK", delta_color="inverse")

st.divider()

col_l, col_r = st.columns([1, 1])

with col_l:
    st.write("### Ripartizione Costi")
    fig, ax = plt.subplots()
    ax.pie([mo_fin, as_fin, revenue-total], labels=['Ord.', 'Straord.', 'Margine'], 
           autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'])
    st.pyplot(fig)

with col_r:
    st.write("### Giustificazione Tecnica")
    st.table(pd.DataFrame({
        "Parametro": ["Coeff. Vetustà (Kv)", "Coeff. Densità (Kd)", "Mq/Ospite"],
        "Valore": [kv, kd, round(area/guests, 2)]
    }))
    if incidenza > 10:
        st.error("Il costo di mantenimento eccede i parametri di sostenibilità per questa tipologia di asset.")