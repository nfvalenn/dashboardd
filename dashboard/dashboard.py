import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_order = df.resample(rule='D', on='order_approved_at').agg({
        'order_id': 'count',
        'price': 'sum'
    })
    daily_order = daily_order.reset_index(drop= False)
    daily_order.rename(columns = {
        'order_approved_at': 'order_date',
        'order_id': 'order_count',
        'price': 'revenue'
    }, inplace= True)
    return daily_order

def create_top_10_city(df):
    top_10_city = df.groupby("customer_city").customer_id.nunique().sort_values(ascending=False).reset_index()
    top_10_city.columns = ["customer_city", "customer_count"]
    return top_10_city

def create_top_10_state(df):
    top_10_state = df.groupby("customer_state").customer_id.nunique().sort_values(ascending=False).reset_index()
    top_10_state.columns = ["customer_state", "customer_count"]
    return top_10_state

def create_sum_order_items_df(df):
    sum_order_items_df= df.groupby("product_category_name").order_item_id.count().sort_values(ascending=False).reset_index()
    sum_order_items_df.columns = ["product_name", "sales_count"]
    return sum_order_items_df

def create_order_payments_df(df):
    order_payments_df = df.groupby("payment_type").order_id.nunique().reset_index()
    return order_payments_df


url = "https://raw.githubusercontent.com/nfvalenn/dashboardd/main/dashboard/all_data_a.csv"
all_data = pd.read_csv(url)

all_data.dropna(subset=["order_approved_at"], inplace=True)
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

datatime_columns = ["order_approved_at"]
for column in datatime_columns:
    all_data[column] =  pd.to_datetime(all_data[column])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

with st.sidebar:
    st.image("https://raw.githubusercontent.com/nfvalenn/dashboardd/main/logo.png")
    start_date, end_date = st.date_input(
        label="Rentang Waktu", min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    main_df = all_data[(all_data["order_approved_at"] >= str(start_date)) & 
                (all_data["order_approved_at"] <= str(end_date))]
    
    daily_orders = create_daily_orders_df(main_df)
    top_10_city = create_top_10_city(main_df)
    top_10_state = create_top_10_state(main_df)
    sum_order_item = create_sum_order_items_df(main_df)
    order_payment = create_order_payments_df(main_df)

st.header('E-Commarce Dashboard Data Analysis:sparkles:')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders["order_count"].sum()
    print(f"Total Orders: {total_orders}")
    st.metric('Total orders', value= total_orders)
with col2:
    total_revenue = format_currency(daily_orders.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders["order_date"],
    daily_orders["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

st.subheader("10 Kota dan Negara dengan Pelanggan Terbanyak")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(50, 12))

colors = ["#663399", "#75489D", "#865FA9", "#9775B5", "#A88CC2", "#B9A2CE", "#CBB9DA", "#D1BCD8", "#D9C4E0", "#E1CDE7"]

sns.barplot(x="customer_count", y="customer_city", hue="customer_city", data=top_10_city.head(10), palette=colors, ax=ax[0])
ax[0].set_ylabel("Kota", fontsize = 40)
ax[0].set_xlabel("Jumlah Pelanggan", fontsize = 40)
ax[0].set_title("10 Kota dengan Pelanggan Terbanyak", loc="center", fontsize=50, pad=30)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(x="customer_count", y="customer_state", hue="customer_state", data=top_10_state.head(10), palette=colors, ax=ax[1])
ax[1].set_ylabel("Negara", fontsize = 40)
ax[1].set_xlabel("Jumlah Pelanggan", fontsize = 40)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("10 Negara dengan Pelanggan Terbanyak", loc="center", fontsize=50, pad=30)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.subheader("Penjualan Jenis Produk tertinggi")
fig, ax = plt.subplots(figsize=(10, 5))

colors_red = ["#993333", "#A54444", "#B25555", "#C06666", "#CD7777", "#DA8888", "#E79999", "#F5AAAA", "#FFBBBB", "#FFCCCC"]

sns.barplot(
    y="sales_count", 
    x="product_name",
    hue="product_name",
    data=sum_order_item.sort_values(by="sales_count", ascending=False).head(10),
    palette=colors_red
)
ax.set_ylabel(None)
ax.set_xlabel(None)

ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=12)
st.pyplot(fig)

st.subheader("Metode Pembayaran Yang Paling Sering Digunakan")
plt.figure(figsize=(10, 7))
palette_color = sns.color_palette('pink') 

plt.pie(order_payment["order_id"], labels=order_payment["payment_type"], colors=palette_color, autopct='%.0f%%', pctdistance=0.85)
plt.tight_layout()

st.pyplot(plt)

st.caption('Copyright © Nabila Febriyanti Valentin 2025')
