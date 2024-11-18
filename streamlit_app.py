import streamlit as st
from utils.funcs import load_logo

from pathlib import Path
from PIL import Image

load_logo()

# Set wide layout for the app
st.set_page_config(layout='wide')

# Streamlit App - Main Overview Page
st.markdown(
    """
    <div style="background-color:#22b0a4;padding:10px;border-radius:5px;text-align:center;color:white;">
    <h1>3Commas Exchange Volume Analysis Dashboard</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    ### Steps for Data Analysis:

    1. <span style='font-size: 18px; font-weight: bold; font-family: "Arial, Helvetica, sans-serif";'>Data Preprocessing</span>: <span style='font-size: 18px; font-family: "Georgia, serif";'>At first step, I conducted data cleaning to ensure next steps could be executed effectively. For example, the following function was used to exclude "paper" exchanges, clean account types, and segment users each month by volume according to the task description:</span>

    ```python
    def preprocess_data(df):
        # Exclude paper exchanges
        df = df[~df['account_type'].str.lower().str.contains("paper")]
        # Remove extra text from account_type column
        df['account_type'] = df['account_type'].replace({'Account::': '', 'Accounts::': '', 'Account': '', 'Coin': ''}, regex=True)

        # Convert month to datetime format
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
            ...
    ```

    2. <span style='font-size: 18px; font-weight: bold;'>Segment Analysis</span>: <span style='font-size: 18px;'>In this step, I provided the number and percentage of traders per month for each segment (A, B, C, D) based on previous cleaning step.</span>

    3. <span style='font-size: 18px; font-weight: bold;'>User Analysis</span>: <span style='font-size: 18px;'>This page provides user selection options in the left sidebar, allowing users to filter from the list. Other information, such as the account type used by the selected user, is updated accordingly.<br> On the right side, metric cards are displayed to show Total Volume, Segment Changes, the segments the user belonged to during the period, and the count of times the user reached 'A' Segment.</span>

    4. <span style='font-size: 18px; font-weight: bold;'>Benchmarking Analysis</span>: <span style='font-size: 18px;'>This page presents a benchmark analysis of global volume versus 3Commas exchange volume by account type. For instance, it compares Binance's global exchange volume with Binance's volume on 3Commas.<br>
   <br>Notes:
    <li> To connect global volumes to 3commas volums I did a preprocessing step to create an id for each volume to be able to join them together. </li>
    <li>Since the volumes are not on the same scale, 3Commas volumes are presented on the right axis to better illustrate the trend.</li></span>

    ### Please Use the Sidebar to Explore Further
    ### Thank you
    """,
    unsafe_allow_html=True
)
