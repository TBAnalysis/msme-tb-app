
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trial Balance Dashboard", layout="wide")

st.title("📊 Trial Balance Analyzer for MSMEs")

uploaded_file = st.file_uploader("Upload your Trial Balance (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    required_cols = {'Account Head', 'Type', 'Amount'}
    if not required_cols.issubset(df.columns):
        st.error("Please ensure your file has these columns: Account Head, Type (Asset/Liability/Income/Expense), Amount")
        st.stop()

    df['Amount'] = df['Amount'].abs()
    summary = df.groupby('Type')['Amount'].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔹 Summary by Type")
        st.dataframe(summary, use_container_width=True)

    with col2:
        st.subheader("🔸 Distribution by Type")
        fig, ax = plt.subplots()
        ax.pie(summary['Amount'], labels=summary['Type'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

    st.subheader("📌 Account-Level Breakdown")
    st.dataframe(df.sort_values(by='Type'), use_container_width=True)

    st.subheader("📈 Key Financial Metrics")
    total_income = df[df['Type'] == 'Income']['Amount'].sum()
    total_expense = df[df['Type'] == 'Expense']['Amount'].sum()
    profit = total_income - total_expense

    st.metric("Total Income", f"₹ {total_income:,.2f}")
    st.metric("Total Expense", f"₹ {total_expense:,.2f}")
    st.metric("Profit / Surplus", f"₹ {profit:,.2f}")
