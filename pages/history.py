import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Prediction History", layout="wide")

# Sidebar Navigation
st.sidebar.title("🔍 Navigation")
st.sidebar.page_link("app.py", label="Home")
st.sidebar.page_link("pages/history.py", label="Prediction History")

st.title("📊 Prediction History")

# Load history
if os.path.exists("history.csv"):
    df = pd.read_csv("history.csv")

    # Convert timestamp column to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Sort and filter controls
        sort_order = st.radio("Sort by time:", ["Newest First", "Oldest First"])
        if sort_order == "Newest First":
            df = df.sort_values(by="timestamp", ascending=False)
        else:
            df = df.sort_values(by="timestamp", ascending=True)

        st.dataframe(df)

        # Clear history
        if st.button("🗑️ Clear History"):
            open("history.csv", "w").write("timestamp,predicted_class,confidence\n")
            st.success("History cleared!")
    else:
        st.warning("No timestamp column found in history.")
else:
    st.warning("No history available yet.")
