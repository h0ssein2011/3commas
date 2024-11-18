import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import re
from PIL import Image

def load_logo():
    # Load the dataset
    path = Path(__file__).parent.parent
    logo_path = path / 'img/logo.png'
    image = Image.open(logo_path)

    st.logo(image, size="large", link=None, icon_image=None)
    return None



# Preprocessing function
def preprocess_data(df):
    # Filter out paper exchanges
    df = df[~df['account_type'].str.lower().str.contains("paper")]

    # Remove 'Account::' and ' Account' from account_type
    df['account_type'] = df['account_type'].replace({'Account::': '', 'Accounts::': '', 'Account': '','Coin':''}, regex=True)

    # Convert the month column to datetime format
    df['month'] = pd.to_datetime(df['month'])


    # Define the volume categories
    def categorize_user(volume):
        if volume >= 2000000:
            return 'A'
        elif volume >= 200000:
            return 'B'
        elif volume >= 20000:
            return 'C'
        elif volume >= 1:
            return 'D'
        else:
            return None

    # Aggregate data to get total usd_amount per user per month
    df_monthly = df.groupby(['user_id', pd.Grouper(key='month', freq='MS')], as_index=False).agg({'usd_amount': 'sum'})

    # Apply user category using aggregated usd_amount
    df_monthly['user_segment'] = df_monthly['usd_amount'].apply(categorize_user)

    return df, df_monthly

def clean_accounts(commas_vols,global_vols):
    exchanges_names = global_vols.exchange_name.unique()
    exchanges_names = [x.lower().strip() for x in exchanges_names]

    commas_exchanges = commas_vols.account_type.unique()
    commas_exchanges = [x.lower().strip() for x in commas_exchanges]
    available_exchanges = [x for x in exchanges_names if any(c in x or x in c for c in commas_exchanges)]

    pattern = '|'.join([re.escape(exchange.lower()) for exchange in available_exchanges])

    # Use Boolean indexing with str.contains()
    global_exchnges = global_vols[global_vols['exchange_name'].str.lower().str.contains(pattern, na=False)].reset_index()
    return global_exchnges


# Function to create stacked bar chart
custom_colors = ['#00B0A3', '#6E9FFF', '#5CC8A1', '#FF708D']
def create_stacked_bar_chart(data, title, yaxis_title,percent=False):
    fig = go.Figure()
    for i, segment in enumerate(sorted(data.columns,reverse=True)):

        if percent:
            text=data[segment].round(1).astype(str)+'%'
        else:
            text=data[segment].round(1)
        fig.add_trace(go.Bar(
            x=data.index.strftime('%b %Y'),
            y=data[segment],
            text=text,
            name=f'Segment {segment}',
            marker_color=custom_colors[i % len(custom_colors)]
        ))

    fig.update_layout(
        yaxis=dict(
            title=yaxis_title,
            range=[0, data.sum(axis=1).max() * 1.1]  # Set y-axis max value to 20% higher than the max sum of segments
        ),
        barmode='stack',
        xaxis_title='Month',
        yaxis_title=yaxis_title,
        title=title,
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
    return fig

def format_number(num):
    if abs(num) >= 1_000_000_000_000:  # Trillions
        return f"{num / 1_000_000_000_000:.1f}T"
    elif abs(num) >= 1_000_000_000:  # Billions
        return f"{num / 1_000_000_000:.1f}B"
    elif abs(num) >= 1_000_000:  # Millions
        return f"{num / 1_000_000:.1f}M"
    elif abs(num) >= 1_000:  # Thousands
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)