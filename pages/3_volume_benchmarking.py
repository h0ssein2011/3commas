import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from pathlib import Path

from utils.funcs import preprocess_data, clean_accounts,load_logo

load_logo()
# Set wide layout for the app

# Header for User Analysis Dashboard
st.markdown("""
    <div style='background-color: #00B0A3; padding: 20px; border-radius: 10px;'>
        <h1 style='text-align: center; color: white;'>3Commas vs Global Exchange Volumes by Account Type</h1>
    </div>
""", unsafe_allow_html=True)

# Load the dataset
path = Path(__file__).parent.parent
path_3commas = path / 'data/3Commas Volumes.csv'
path_rates = path / 'data/Currency Rates.csv'
path_global = path / 'data/Exchange Volumes.csv'
account_id_path = path / 'data/account_ids.csv'

# Read CSV files
t_commas = pd.read_csv(path_3commas)
global_vols = pd.read_csv(path_global)
rates = pd.read_csv(path_rates)
account_ids = pd.read_csv(account_id_path)

# Convert date columns to date type
global_vols['report_date'] = pd.to_datetime(global_vols['report_date']).dt.date
t_commas['month'] = pd.to_datetime(t_commas['month']).dt.date
rates['date'] = pd.to_datetime(rates['date']).dt.date

# Preprocess data
t_commas, _ = preprocess_data(t_commas)
t_commas = t_commas.merge(account_ids[['3commas', 'account_id']], left_on='account_type', right_on='3commas', how='inner')
global_vols = global_vols.merge(account_ids[['Global', 'account_id']], left_on='exchange_name', right_on='Global', how='inner')
global_vols = clean_accounts(t_commas, global_vols)
global_vols = global_vols.merge(rates[['date', 'open']], left_on='report_date', right_on='date', how='left')
global_vols['usd_amount'] = global_vols['btc_volume'] * global_vols['open']

# Create monthly period for aggregation
global_vols['month'] = pd.to_datetime(global_vols['date']).dt.to_period('M')
global_vols['month'] = global_vols['month'].astype(str) + '-01'
global_vols['exchange_type'] = global_vols['exchange_type'].str.replace('futures', 'future')

# Aggregate volumes by month, account, and exchange type
global_vols_grouped = global_vols.groupby(['month', 'account_id', 'exchange_type'], as_index=False).agg({'usd_amount': 'sum'})
global_vols_grouped.rename(columns={'usd_amount': 'usd_amount_global'}, inplace=True)
global_vols_grouped['month'] = pd.to_datetime(global_vols_grouped['month'])

t_commas_grouped = t_commas.groupby(['month', 'account_id', 'exchange_type', 'account_type'], as_index=False).agg({'usd_amount': 'sum'})
t_commas_grouped.rename(columns={'usd_amount': 'usd_amount_3commas'}, inplace=True)

# Merge global and 3Commas volumes for comparison
benchmark = global_vols_grouped.merge(t_commas_grouped, on=['month', 'account_id'], how='left')
benchmark.dropna(axis=0, inplace=True)
benchmark.drop('exchange_type_y', inplace=True, axis=1)
benchmark.rename(columns={'exchange_type_x': 'exchange_type'}, inplace=True)
benchmark['month'] = pd.to_datetime(benchmark['month']).dt.strftime('%b %Y')
# Sidebar for filtering
st.sidebar.title('Filters')
selected_month = st.sidebar.multiselect('Select Month', benchmark['month'].unique(), default=benchmark['month'].unique())
selected_account_types = st.sidebar.multiselect('Select Account Type', benchmark['account_type'].unique(), default=benchmark['account_type'].unique())

# Filter data based on selections
filtered_data = benchmark[(benchmark['month'].isin(selected_month)) & (benchmark['account_type'].isin(selected_account_types))]

# Plotting Simple Bar and Line Charts for Each Account Type
account_types = filtered_data['account_type'].unique()

for account in account_types:
    account_data = filtered_data[filtered_data['account_type'] == account]
    dual_axis_fig = go.Figure()
    dual_axis_fig.add_trace(go.Bar(
        x=account_data['month'],
        y=account_data['usd_amount_global'],
        name='Global Volume',
        marker=dict(color='#17a2b8', line=dict(width=0.5, color='white'))
    ))
    dual_axis_fig.add_trace(go.Scatter(
        x=account_data['month'],
        y=account_data['usd_amount_3commas'],
        name='3Commas Volume',
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=2),
        marker=dict(color='#ff7f0e', size=6),
        yaxis='y2'
    ))

    dual_axis_fig.update_layout(
    title=f'3Commas vs Global Exchange Volumes for Account Type: {account}',
    title_font=dict(size=24, family='Arial', color='#007b7f'),
    xaxis_title='Month',
    yaxis=dict(
        title='Global Volume (USD)',
        title_font=dict(size=16, family='Arial', color='#007b7f'),
        tickfont=dict(size=14, family='Arial', color='#007b7f'),
        side='left'
    ),
    yaxis2=dict(
        title='3Commas Volume (USD)',
        title_font=dict(size=12, family='Arial', color='#ff7f0e'),
        tickfont=dict(size=14, family='Arial', color='#ff7f0e'),
        overlaying='y',
        side='right'
    ),
    legend_title='Volume Type',
    legend=dict(
        font=dict(size=14, family='Arial', color='#007b7f'),
        x=0,y=1,xanchor='left', yanchor='top'
    ),
    template='plotly_white'
)


    st.plotly_chart(dual_axis_fig, use_container_width=True)
