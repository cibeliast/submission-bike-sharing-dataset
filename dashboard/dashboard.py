import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

day_df = pd.read_csv("dashboard/day_clean.csv")
hour_df = pd.read_csv("dashboard/hour_clean.csv")

day_df["dteday"] = pd.to_datetime(day_df["dteday"])
hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    return daily_orders_df

def create_by_season_df(df):
    by_season_df = df.groupby(by="season_label")[["casual", "registered"]].sum().reset_index()
    return by_season_df

def create_hourly_trend_df(df):
    hourly_trend = df.groupby("hr")[["cnt", "casual", "registered"]].mean().reset_index()
    return hourly_trend

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    st.header("Filter Rentang Waktu")
    
    date_range = st.date_input(
            label='Pilih Rentang Waktu',
            min_value=min_date,
            max_value=max_date,
            value=[min_date, max_date]
        )

if len(date_range) < 2:
    st.warning("⚠️ Pilih tanggal akhir untuk memuat data.")
    st.stop()
else:
    start_date, end_date = date_range

main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

main_hour_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                       (hour_df["dteday"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
season_df = create_by_season_df(main_df)
hourly_df = create_hourly_trend_df(main_hour_df)

st.title('🚲 Bike Sharing Analysis Dashboard')

st.subheader('Daily Key Metrics')
col1, col2, col3 = st.columns(3)

with col1:
    total_orders = main_df.cnt.sum()
    st.metric("Total Rides", value=f"{total_orders:,}")

with col2:
    total_casual = main_df.casual.sum()
    st.metric("Total Casual Users", value=f"{total_casual:,}")

with col3:
    total_registered = main_df.registered.sum()
    st.metric("Total Registered Users", value=f"{total_registered:,}")

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 Tren Harian", "🍂 Analisis Musim", "⏰ Analisis Jam"])

with tab1:
    st.subheader("Tren Penyewaan Sepeda Harian")
    
    user_type = st.radio(
        label="Pilih Tipe Pengguna:",
        options=["All", "Casual", "Registered"],
        horizontal=True
    )
    
    if user_type == "All":
        y_col = "cnt"
        line_color = "#90CAF9"
        title_text = "Total Penyewaan Harian"
    elif user_type == "Casual":
        y_col = "casual"
        line_color = "#66BB6A" 
        title_text = "Penyewaan Harian (Casual)"
    else: 
        y_col = "registered"
        line_color = "#FFA726" 
        title_text = "Penyewaan Harian (Registered)"

    fig, ax = plt.subplots(figsize=(16, 6))
    
    ax.plot(
        daily_orders_df["dteday"],
        daily_orders_df[y_col], 
        marker='o', 
        linewidth=2,
        color=line_color 
    )
    
    ax.set_title(f"Grafik Pergerakan {title_text}", fontsize=20)
    ax.set_xlabel("Tanggal", fontsize=15)
    ax.set_ylabel("Jumlah Sewa", fontsize=15)
    ax.tick_params(axis='y', labelsize=12)
    ax.tick_params(axis='x', labelsize=12)
    
    st.pyplot(fig)
    
    with st.expander("Penjelasan Insight"):
        st.write(f"""
        - **Pola:** Terlihat tren peningkatan dari tahun 2011 ke 2012.
        - **Fluktuasi:** Penurunan tajam biasanya terjadi saat cuaca buruk atau hari libur (khusus Registered).
        """)

with tab2:
    st.subheader("Pengaruh Musim Terhadap Tipe Pengguna")
    
    melted_season = season_df.melt(id_vars='season_label', 
                                   value_vars=['casual', 'registered'], 
                                   var_name='User Type', 
                                   value_name='Rides')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='season_label', y='Rides', hue='User Type', data=melted_season, palette='Set2', ax=ax)
    
    ax.set_xlabel("Musim", fontsize=15)
    ax.set_ylabel("Total Rides", fontsize=15)
    ax.set_title("Performa: Casual vs Registered per Musim", fontsize=20)
    st.pyplot(fig)
    
    with st.expander("Penjelasan Insight"):
        st.write("""
        - **Casual User:** Sangat sensitif terhadap musim. Penurunan paling drastis terjadi di **Musim Semi (Spring)**.
        - **Registered User:** Lebih stabil dan loyal, penurunan di musim dingin/semi tidak sedrastis Casual user.
        - **Rekomendasi:** Hindari promosi agresif untuk turis di musim Semi, fokuskan di Musim Gugur (Fall).
        """)

with tab3:
    st.subheader("Pola Jam Operasional")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(x='hr', y='cnt', data=hourly_df, label='Total', color='blue', ax=ax)
    sns.lineplot(x='hr', y='casual', data=hourly_df, label='Casual', color='green', ax=ax)
    sns.lineplot(x='hr', y='registered', data=hourly_df, label='Registered', color='orange', ax=ax)
    
    ax.set_xlabel("Jam (0-23)", fontsize=15)
    ax.set_ylabel("Rata-rata Sewa", fontsize=15)
    ax.set_title("Rata-rata Penyewaan per Jam", fontsize=20)
    ax.set_xticks(range(0, 24))
    ax.legend()
    st.pyplot(fig)

    with st.expander("Penjelasan Insight"):
        st.write("""
        - **Pola:** Terjadi dua puncak utama, yaitu jam **08:00** dan **17:00**.
        - **Dominasi:** Jam sibuk didominasi oleh user **Registered**.
        - **Rekomendasi:** Pastikan ketersediaan unit sepeda maksimal pada jam 07:00 dan 16:00. Lakukan maintenance di jam 00:00 - 05:00.
        """)