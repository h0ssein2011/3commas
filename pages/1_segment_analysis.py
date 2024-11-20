import pandas as pd
import streamlit as st
import random
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from utils.funcs import load_logo,create_stacked_bar_chart

load_logo()
from utils.funcs import preprocess_data


# Set wide layout for the app
st.set_page_config(layout='wide')

# Load the dataset
path = Path(__file__).parent.parent
path_csv = path / 'data/3Commas Volumes.csv'
df = pd.read_csv(path_csv)

# Preprocess the data
df, df_monthly = preprocess_data(df)

# Streamlit Application
st.markdown("""
    <div style='background-color: #00B0A3; padding: 20px; border-radius: 10px;'>
        <h1 style='text-align: center; color: white;'>Segment Analysis </h1>
    </div>
""", unsafe_allow_html=True)
# Sidebar for filtering segments and additional filters
segments = ['A', 'B', 'C', 'D']
selected_segments = st.sidebar.multiselect('Select User Segments', segments, default=segments)

# Additional filters in the sidebar
selected_account_type = st.sidebar.multiselect('Select Account Type', df['account_type'].unique(), default=df['account_type'].unique())
selected_exchange_type = st.sidebar.multiselect('Select Exchange Type', df['exchange_type'].unique(), default=df['exchange_type'].unique())
selected_subscription = st.sidebar.multiselect('Select Subscription', df['subscription'].unique(), default=df['subscription'].unique())
selected_subscription_type = st.sidebar.multiselect('Select Subscription Type', df['subscription_type'].unique(), default=df['subscription_type'].unique())

# Filter data based on selected segments and additional filters
df_filtered = df_monthly[df_monthly['user_segment'].isin(selected_segments)]
df_filtered = df_filtered.merge(df[['user_id', 'account_type', 'exchange_type', 'subscription', 'subscription_type']], on='user_id')
df_filtered = df_filtered[(df_filtered['account_type'].isin(selected_account_type)) &
                          (df_filtered['exchange_type'].isin(selected_exchange_type)) &
                          (df_filtered['subscription'].isin(selected_subscription)) &
                          (df_filtered['subscription_type'].isin(selected_subscription_type))]

# Layout with two columns
col1, col2 = st.columns(2)

# 1. Trader Count Monthly by Segment
monthly_segment_count = df_filtered.groupby(['month', 'user_segment'])['user_id'].nunique().unstack().fillna(0)

with col1:
    # Plot stacked bar chart using Plotly for user count
    fig_count = create_stacked_bar_chart(monthly_segment_count, 'Trader Count Monthly by Segment', 'User Count')
    st.plotly_chart(fig_count)

# 2. Segment Percent by Total User Count Monthly
monthly_total_users = df_filtered.groupby('month')['user_id'].nunique()
monthly_segment_percent = monthly_segment_count.div(monthly_total_users, axis=0) * 100

with col2:
    # Plot stacked bar chart using Plotly for percentage
    fig_percent = create_stacked_bar_chart(monthly_segment_percent, 'Segment Percent by Total User Count Monthly', 'Percentage of Users',percent=True)
    st.plotly_chart(fig_percent)
st.markdown("<hr style='border: 2px solid #00B0A3;'>", unsafe_allow_html=True)
# 3. Average Volume per User
monthly_avg_volume = df_filtered.groupby(['month', 'user_segment'])['usd_amount'].mean().unstack().fillna(0)
fig_avg_volume = create_stacked_bar_chart(monthly_avg_volume, 'Average Volume per User', 'Average Volume($)')
st.plotly_chart(fig_avg_volume)

