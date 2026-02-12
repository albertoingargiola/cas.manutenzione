import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Configurazione Dashboard
st.set_page_config(page_title="CAS Maintenance Predictor", layout="wide")

st.title("🏗️ CAS Asset Management Tool")
st.subheader("Modello Parametrico di Budgeting e Accantonamento")

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

# Delta Aliquote (Parametri tecnici giustificati)
d_mo = (0.0025 if f_elev else 0) + (0.0035 if f_hvac else 0) + (0.0015 if f_vmc else 0) + (0.0010 if f_fire else 0) + (0.0005 if f_cctv else 0)
d_as = (0.0015 if f_elev else 0) + (0.0025 if f_hvac else 0) + (0.0010 if f_vmc else 0) + (0.0005 if f_fire else 0) + (0.0010 if f_cctv else 0)

# Calcolo Quote Separate
mo_fin = (asset_val * kv * kd * 0.014) + (asset_val * d_mo)
as_fin = (asset_val * kv * 0.007) + (asset_val * d_as)
total_op = mo_fin + as_fin
incidenza = (total_op / revenue) * 100

# --- LAYOUT VISUALE ---
# Esposizione delle 4 metriche chiave
c1, c2, c3, c4 = st.columns(4)
c1.metric("Valore Asset", f"€ {asset_val:,.0f}")
c2.metric("Manut. Ordinaria (OPEX)", f"€ {mo_fin:,.0f}")
c3.metric("Accant. Straord. (CAPEX)", f"€ {as_fin:,.0f}")
c4.metric("Incidenza Totale", f"{incidenza:.2f}%", 
          delta="CRITICO" if incidenza > 10 else "OK", delta_color="inverse")

st.divider()

col_l, col_r = st.columns([1, 1])

with col_l:
    st.write("### Ripartizione Budget Totale")
    fig, ax = plt.subplots()
    ax.pie([mo_fin, as_fin, revenue - total_op], 
           labels=['Ordinaria', 'Accant. Straord.', 'Margine Residuo'], 
           autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'],
           wedgeprops={'edgecolor': 'white'})
    st.pyplot(fig)

with col_r:
    st.write("### Riepilogo Tecnico-Economico")
    dati_tabella = {
        "Voce di Costo": ["Manutenzione Ordinaria", "Accantonamento Straordinaria", "TOTALE ONERI"],
        "Importo Annuo": [f"€ {mo_fin:,.2f}", f"€ {as_fin:,.2f}", f"€ {total_op:,.2f}"],
        "% su Fatturato": [f"{(mo_fin/revenue)*100:.2f}%", f"{(as_fin/revenue)*100:.2f}%", f"{incidenza:.2f}%"]
    }
    st.table(pd.DataFrame(dati_tabella))
    
    st.info(f"**Nota Tecnica:** Il calcolo include un coefficiente di vetustà di {kv} e un carico antropico (densità) di {kd}.")