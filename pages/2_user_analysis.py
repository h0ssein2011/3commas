import pandas as pd
import streamlit as st
import random
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from utils.funcs import load_logo,format_number

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
        <h1 style='text-align: center; color: white;'>User Analysis Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# Additional filters in the sidebar
user_ids = df['user_id'].unique().tolist()
default_id = 259930
# selected_user_id = st.sidebar.text_input('Or Enter User ID to see detailed metrics:', value=default_id)
# selected_user_id = int(selected_user_id)
selected_user_id = st.sidebar.selectbox('Select a User ID from the list:', options=user_ids, index=user_ids.index(default_id))


user_data = df[df['user_id'] == selected_user_id]
df_monthly = df_monthly[df_monthly['user_id'] == selected_user_id]

# Filter data based on selected segments and additional filters
user_data = user_data[['user_id','month','account_type', 'exchange_type', 'subscription', 'subscription_type']].merge(df_monthly, on=['user_id','month'])


selected_account_type = st.sidebar.multiselect('Select Account Type', user_data['account_type'].unique(), default=user_data['account_type'].unique())
selected_exchange_type = st.sidebar.multiselect('Select Exchange Type', user_data['exchange_type'].unique(), default=user_data['exchange_type'].unique())
selected_subscription = st.sidebar.multiselect('Select Subscription', user_data['subscription'].unique(), default=user_data['subscription'].unique())
selected_subscription_type = st.sidebar.multiselect('Select Subscription Type', user_data['subscription_type'].unique(), default=user_data['subscription_type'].unique())
df_filtered = user_data[(user_data['account_type'].isin(selected_account_type)) &
                          (user_data['exchange_type'].isin(selected_exchange_type)) &
                          (user_data['subscription'].isin(selected_subscription)) &
                          (user_data['subscription_type'].isin(selected_subscription_type))]

df_filtered = df_filtered.drop_duplicates(subset=['month','usd_amount'])
# Generate a list of random user IDs to select from
col1,col2 ,col3,col4 = st.columns(4)
with col1:
    total_volume = df_filtered['usd_amount'].sum()
    st.markdown(
    f"""
    <div style='background-color: #00B0A3; padding: 8px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); margin-bottom: 20px; transform: scale(0.75);'>
        <h4 style='margin: 0; text-align: center;'> Total Volume</h4>
        <p style='font-size: 44px; color: white;text-align:center;'>{format_number(total_volume)}</p>
    </div>
    """,unsafe_allow_html=True)
with col2:
    volume_dynamics = df_filtered.groupby(['month','user_segment'], as_index=False).agg({'usd_amount': 'sum'})  # Volume dynamics
    segment_changes = volume_dynamics['user_segment'].unique().tolist()  # How many times the user hit different segments
    segment_names = ','.join(segment_changes)
    segment_changes_counts = len(segment_changes)  # How many times the user hit different segments
    st.markdown(
    f"""
    <div style='background-color: #00B0A3; padding: 8px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); margin-bottom: 20px; transform: scale(0.75);'>
        <h4 style='margin: 0; text-align: center;'>Segment Change Count</h4>
        <p style='font-size: 44px; color: white;text-align:center;'>{segment_changes_counts:.0f}  </p>
    </div>
    """,unsafe_allow_html=True)
with col3:
        st.markdown(
    f"""
    <div style='background-color: #00B0A3; padding: 8px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); margin-bottom: 20px; transform: scale(0.75);'>
        <h4 style='margin: 0; text-align: center;'>Segments </h4>
        <p style='font-size: 44px; color: white;text-align: center;'>{segment_names} </p>
    </div>
    """,unsafe_allow_html=True)
with col4:
    a_segment_count = volume_dynamics[volume_dynamics.user_segment=='A'].shape[0]  # How many times the user hit segment A
    st.markdown(
    f"""
    <div style='background-color: #00B0A3; padding: 8px; border-radius: 15px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); margin-bottom: 20px; transform: scale(0.75);'>
        <h4 style='margin: 0; text-align: center;'>A Segment Count</h4>
        <p style='font-size: 44px; color: white;text-align: center;'>{a_segment_count:.0f} </p>
    </div>
    """,unsafe_allow_html=True)

if selected_user_id:
    if not df_filtered.empty:
        fig_volume_dynamics = go.Figure()
        fig_volume_dynamics.add_trace(go.Scatter(
            x=volume_dynamics['month'].dt.strftime('%b %Y'),
            y=volume_dynamics['usd_amount'],
            mode='lines+markers',
            name='Volume Dynamics',
            line=dict(color='#00B0A3')
        ))
        fig_volume_dynamics.update_layout(
            xaxis_title='Month',
            yaxis_title='Volume',
            title='Volume Dynamics Over Time',
            font=dict(
                family="Helvetica, Arial, sans-serif",
                size=14,
                color="#333"
            ),
            title_font=dict(
                family="Helvetica, Arial, sans-serif",
                size=18,
                color="#00B0A3"
            ),
            legend=dict(
                font=dict(
                    family="Helvetica, Arial, sans-serif",
                    size=12,
                    color="#333"
                )
            )
        )
        st.plotly_chart(fig_volume_dynamics)
    else:
        st.write('User ID not found in the dataset.')
