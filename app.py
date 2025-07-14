import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

# Koneksi ke MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='coba'  # Ganti sesuai database kamu
)

# Fungsi load data dari tiap tabel
def load_data(table_name):
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    df['category'] = table_name.capitalize()
    df['total_revenue'] = df['price_idr'] * df['quantity_sold']
    return df

# Mapping nama tabel dan label menu
category_tables = {
    "💻 Laptop": "laptops",
    "📱 Handphone": "handphones",
    "⌨️ Keyboard": "keyboards",
    "🔊 Speaker": "speakers",
    "🖥️ Monitor": "monitors",
    "📊 Dashboard Gabungan": "all"
}

# Sidebar menu navigasi
st.sidebar.title("📦 Pilih Menu Dashboard")
selected = st.sidebar.selectbox("Kategori Produk", list(category_tables.keys()))

# ---------- INDIVIDU DASHBOARD ----------
if selected != "📊 Dashboard Gabungan":
    table_name = category_tables[selected]
    df = load_data(table_name)

    st.title(f"{selected} Dashboard Penjualan")
    st.markdown("Versi **Streamlit + Plotly II**")

    # Filter harga
    min_price = st.slider("Filter produk dengan harga minimal (Rp):",
                          int(df['price_idr'].min()), int(df['price_idr'].max()), int(df['price_idr'].min()))
    filtered_df = df[df['price_idr'] >= min_price]

    # Data Tabel
    st.subheader("📋 Data Produk")
    st.dataframe(filtered_df)

    # Grafik Jumlah Terjual
    st.subheader("📦 Jumlah Produk Terjual")
    fig1 = px.bar(filtered_df, x='product_name', y='quantity_sold',
                  title="Jumlah Terjual per Produk", color='quantity_sold')
    st.plotly_chart(fig1)

    # Grafik Pendapatan
    st.subheader("💰 Pendapatan per Produk")
    fig2 = px.bar(filtered_df, x='product_name', y='total_revenue',
                  title="Total Pendapatan per Produk", color='total_revenue')
    st.plotly_chart(fig2)

    # Statistik Total
    st.markdown("### 📈 Statistik Total")
    col1, col2 = st.columns(2)
    col1.metric("Total Unit Terjual", f"{filtered_df['quantity_sold'].sum()}")
    col2.metric("Total Pendapatan", f"Rp {filtered_df['total_revenue'].sum():,.0f}")

# ---------- DASHBOARD GABUNGAN ----------
else:
    st.title("📊 Dashboard Gabungan Seluruh Produk")
    st.markdown("Analisis komparatif lintas kategori produk")

    # Load semua data
    df_all = pd.concat([
        load_data('laptops'),
        load_data('handphones'),
        load_data('keyboards'),
        load_data('speakers'),
        load_data('monitors')
    ])

    # Filter harga seluruh kategori
    min_price = st.slider("Filter semua produk dengan harga minimal (Rp):",
                          int(df_all['price_idr'].min()), int(df_all['price_idr'].max()),
                          int(df_all['price_idr'].min()))
    filtered_all = df_all[df_all['price_idr'] >= min_price]

    # Tabel
    st.subheader("📋 Data Gabungan Produk")
    st.dataframe(filtered_all)

    # Grafik: Jumlah Terjual per Kategori
    st.subheader("📦 Jumlah Terjual per Kategori")
    sold_by_cat = filtered_all.groupby("category")["quantity_sold"].sum().reset_index()
    fig3 = px.bar(sold_by_cat, x="category", y="quantity_sold", color="quantity_sold",
                  title="Total Unit Terjual per Kategori")
    st.plotly_chart(fig3)

    # Grafik: Pendapatan per Kategori
    revenue_by_cat = filtered_all.groupby("category")["total_revenue"].sum().reset_index()
    st.subheader("💰 Pendapatan per Kategori")
    fig4 = px.bar(revenue_by_cat, x="category", y="total_revenue", color="total_revenue",
                  title="Total Pendapatan per Kategori (Rp)")
    st.plotly_chart(fig4)

    # Statistik keseluruhan
    st.markdown("### 📈 Statistik Gabungan")
    col1, col2 = st.columns(2)
    col1.metric("Total Unit Terjual", f"{filtered_all['quantity_sold'].sum()}")
    col2.metric("Total Pendapatan", f"Rp {filtered_all['total_revenue'].sum():,.0f}")

# Tutup koneksi
conn.close()
