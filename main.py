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
    try:
        user_val = st.session_state.captcha_input
        correct_val = st.session_state.num1 + st.session_state.num2
        if user_val == correct_val:
            st.session_state.verified = True
            st.session_state.attempts = 0
        else:
            st.session_state.attempts += 1
            if st.session_state.attempts >= 3:
                st.session_state.cooldown_until = time.time() + 30
            # Reset angka baru
            st.session_state.num1 = random.randint(1, 10)
            st.session_state.num2 = random.randint(1, 10)
    except:
        pass

# --- 3. TAMPILAN HALAMAN VERIFIKASI (UI NYAMAN DI MATA) ---
if not st.session_state.verified:
    st.markdown("""
        <style>
        /* Latar belakang dengan warna abu-abu kebiruan yang tenang */
        [data-testid="stAppViewContainer"] { 
            background-color: #f0f2f6;
            background-image: radial-gradient(#d1d9e6 1px, transparent 1px);
            background-size: 20px 20px;
        }
        
        /* Container Verifikasi yang Elegan */
        .auth-card {
            background: #ffffff;
            padding: 50px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.05);
            max-width: 480px;
            margin: 100px auto;
            text-align: center;
            border: 1px solid #e0e0e0;
        }
        
        .auth-title { 
            color: #2c3e50; 
            font-family: 'Helvetica Neue', sans-serif; 
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .auth-subtitle {
            color: #7f8c8d;
            font-size: 0.95rem;
            margin-bottom: 30px;
        }

        /* Menghaluskan input box */
        .stNumberInput input {
            border-radius: 8px !important;
            border: 1px solid #dcdde1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Cooldown Logic
    current_time = time.time()
    if current_time < st.session_state.cooldown_until:
        remaining = int(st.session_state.cooldown_until - current_time)
        st.warning(f"Sistem terkunci. Silakan coba lagi dalam {remaining} detik.")
        time.sleep(1)
        st.rerun()

    if 'num1' not in st.session_state:
        st.session_state.num1 = random.randint(1, 10)
        st.session_state.num2 = random.randint(1, 10)

    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    st.markdown('<h2 class="auth-title">Verifikasi Keamanan</h2>', unsafe_allow_html=True)
    st.markdown('<p class="auth-subtitle">Mohon selesaikan perhitungan sederhana ini.</p>', unsafe_allow_html=True)
    
    st.number_input(
        f"Berapa hasil dari {st.session_state.num1} + {st.session_state.num2}?", 
        step=1, value=0, key="captcha_input", on_change=check_answer
    )
    
    if st.session_state.attempts > 0:
        st.caption(f"Percobaan gagal: {st.session_state.attempts}/3")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 4. DASHBOARD UTAMA ---
else:
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] { background: #fafafa; }
        .stMetric {
            background-color: #ffffff;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            border-radius: 8px; padding: 15px;
        }
        .analysis-text {
            font-size: 0.9rem; color: #444; line-height: 1.6;
            background: #ffffff; padding: 15px; border-radius: 8px;
            border: 1px solid #eee; margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    try:
        df = pd.read_csv('data_balita.csv')
        st.title("Dashboard Analisis Gizi Balita")
        st.write("Visualisasi terpadu mengenai data kesehatan dan status gizi balita.")
        
        # Metrics
        m = st.columns(4)
        m[0].metric("Total Subjek", len(df))
        m[1].metric("Rerata Tinggi", f"{df['Tinggi Badan (cm)'].mean():.1f} cm")
        m[2].metric("Rerata Umur", f"{df['Umur (bulan)'].mean():.1f} bln")
        m[3].metric("Status Normal", len(df[df['Status Gizi'] == 'normal']))

        st.divider()

        # Row 1
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Distribusi Umur")
            fig1 = px.histogram(df, x="Umur (bulan)", nbins=10, template="plotly_white", color_discrete_sequence=['#54a0ff'])
            fig1.update_traces(marker_line_color='#2c3e50', marker_line_width=1)
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown('<div class="analysis-text">Grafik ini menunjukkan sebaran usia dalam populasi balita. Memahami distribusi usia sangat penting untuk melakukan klasifikasi status gizi yang akurat sesuai standar WHO.</div>', unsafe_allow_html=True)

        with col2:
            st.subheader("Proporsi Jenis Kelamin")
            gc = df['Jenis Kelamin'].value_counts().reset_index()
            fig2 = px.bar(gc, x="Jenis Kelamin", y="count", color="Jenis Kelamin",
                         color_discrete_map={'laki-laki': '#2e86de', 'perempuan': '#ee5253'}, template="plotly_white")
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('<div class="analysis-text">Visualisasi ini membandingkan komposisi antara balita laki-laki dan perempuan. Data yang seimbang membantu mengurangi bias dalam pengambilan keputusan kesehatan masyarakat.</div>', unsafe_allow_html=True)

        # Row 2
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Persentase Status Gizi")
            fig3 = px.pie(df, names='Status Gizi', hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig3, use_container_width=True)
            st.markdown('<div class="analysis-text">Persentase status gizi memberikan gambaran umum mengenai tingkat kesehatan nutrisi di wilayah terkait, memudahkan pemangku kebijakan untuk melihat tren gizi.</div>', unsafe_allow_html=True)
            
        with col4:
            st.subheader("Variasi Tinggi Badan")
            fig4 = px.box(df, y="Tinggi Badan (cm)", points="outliers", color_discrete_sequence=['#1dd1a1'])
            st.plotly_chart(fig4, use_container_width=True)
            st.markdown('<div class="analysis-text">Boxplot ini digunakan untuk mengidentifikasi keberadaan outlier (data pencilan) pada tinggi badan balita dan melihat konsistensi pertumbuhan fisik dalam kelompok data ini.</div>', unsafe_allow_html=True)

        # Tabel Data
        st.divider()
        st.subheader("Detail Informasi Data")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal memuat file data_balita.csv. Pesan sistem: {e}")