import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import random
import time

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Monitoring Gizi", page_icon=None, layout="wide")

# --- 2. LOGIKA KEAMANAN ---
if 'verified' not in st.session_state:
    st.session_state.verified = False
if 'attempts' not in st.session_state:
    st.session_state.attempts = 0
if 'cooldown_until' not in st.session_state:
    st.session_state.cooldown_until = 0

def check_answer():
    user_val = st.session_state.captcha_input
    correct_val = st.session_state.num1 + st.session_state.num2
    if user_val == correct_val:
        st.session_state.verified = True
        st.session_state.attempts = 0
    else:
        st.session_state.attempts += 1
        if st.session_state.attempts >= 3:
            st.session_state.cooldown_until = time.time() + 30
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

# --- 3. TAMPILAN HALAMAN VERIFIKASI ---
if not st.session_state.verified:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); 
        }
        .auth-container {
            background-color: white; padding: 40px; border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); max-width: 450px;
            margin: 100px auto; text-align: center; border: 1px solid #e1e4e8;
        }
        .auth-title { color: #2c3e50; font-family: 'Segoe UI', sans-serif; font-weight: 600; }
        </style>
    """, unsafe_allow_html=True)

    current_time = time.time()
    if current_time < st.session_state.cooldown_until:
        remaining = int(st.session_state.cooldown_until - current_time)
        st.error(f"Terlalu banyak percobaan. Silakan tunggu {remaining} detik.")
        time.sleep(1)
        st.rerun()

    if 'num1' not in st.session_state:
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h2 class="auth-title">Verifikasi Akses</h2>', unsafe_allow_html=True)
    st.write("Selesaikan perhitungan di bawah untuk melanjutkan ke dashboard.")
    
    st.number_input(
        f"Berapa hasil dari {st.session_state.num1} + {st.session_state.num2}?", 
        step=1, value=0, key="captcha_input", on_change=check_answer
    )
    
    if st.session_state.attempts > 0:
        st.caption(f"Percobaan gagal: {st.session_state.attempts}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DASHBOARD UTAMA ---
else:
    # UI Styling yang lebih profesional
    st.markdown("""
        <style>
        .main { background: #f8f9fa; }
        .stMetric {
            background-color: #ffffff;
            border-left: 5px solid #2980b9;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-radius: 8px; padding: 15px;
        }
        .chart-container {
            background-color: #ffffff;
            padding: 20px; border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            margin-bottom: 20px;
        }
        .analysis-text {
            font-size: 0.9rem; color: #555; line-height: 1.6;
            background: #f1f3f5; padding: 12px; border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        df = pd.read_csv('data_balita.csv')
        st.title("Dashboard Analisis Gizi Balita")
        st.markdown("Sistem pemantauan kesehatan dan distribusi status nutrisi anak.")
        
        # Metrics Row
        m = st.columns(4)
        m[0].metric("Total Subjek", len(df))
        m[1].metric("Rerata Tinggi (cm)", f"{df['Tinggi Badan (cm)'].mean():.1f}")
        m[2].metric("Rerata Umur (Bulan)", f"{df['Umur (bulan)'].mean():.1f}")
        m[3].metric("Status Gizi Normal", len(df[df['Status Gizi'] == 'normal']))

        st.divider()

        # Row 1: Umur & Gender
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Distribusi Umur")
            fig1 = px.histogram(df, x="Umur (bulan)", nbins=10, template="plotly_white", color_discrete_sequence=['#3498db'])
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('<p class="analysis-text">Grafik di atas menunjukkan sebaran usia balita dalam populasi. Puncak distribusi membantu mengidentifikasi kelompok usia mana yang paling mendominasi dalam pengumpulan data ini.</p>', unsafe_allow_html=True)

        with col2:
            st.subheader("Proporsi Jenis Kelamin")
            gc = df['Jenis Kelamin'].value_counts().reset_index()
            fig2 = px.bar(gc, x="Jenis Kelamin", y="count", color="Jenis Kelamin",
                         color_discrete_map={'laki-laki': '#2980b9', 'perempuan': '#d35400'}, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('<p class="analysis-text">Visualisasi ini membandingkan jumlah balita laki-laki dan perempuan. Keseimbangan data sangat penting untuk memastikan tidak ada bias gender dalam analisis kesehatan.</p>', unsafe_allow_html=True)

        # Row 2: Status Gizi & Boxplot
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Persentase Status Gizi")
            fig3 = px.pie(df, names='Status Gizi', hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown('<p class="analysis-text">Bagan donat ini merangkum status gizi keseluruhan. Ini adalah indikator kunci untuk menentukan efektivitas program intervensi gizi di wilayah tersebut.</p>', unsafe_allow_html=True)
            
        with col4:
            st.subheader("Analisis Varians Tinggi Badan")
            fig4 = px.box(df, y="Tinggi Badan (cm)", points="all", color_discrete_sequence=['#27ae60'])
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('<p class="analysis-text">Boxplot digunakan untuk mendeteksi outlier dan sebaran tinggi badan. Rentang interkuartil menunjukkan konsistensi pertumbuhan fisik balita dalam sampel.</p>', unsafe_allow_html=True)

        # Data Table
        st.divider()
        st.subheader("Detail Data")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Sistem tidak dapat menemukan file data: {e}")