import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Function to process and clean the uploaded TB files
def process_tb(file, year, income_negative):
    try:
        df = pd.read_excel(file)
        df["Financial Year"] = year
        if income_negative:
            df.loc[df["Type"] == "Income", "Amount"] *= -1
            df.loc[df["Type"] == "Expense", "Amount"] = df.loc[df["Type"] == "Expense", "Amount"].abs()
        else:
            df["Amount"] = df["Amount"].abs()
        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return pd.DataFrame()

# Streamlit app
st.title("📊 MSME Trial Balance Analyzer")

st.markdown("""
Upload your Trial Balance files (Excel format) for one or more financial years.
Ensure each file includes the following columns:
- **Account Head**
- **Type** (Asset, Liability, Income, Expense)
- **Amount**
""")

uploaded_files = st.file_uploader("Upload Trial Balance file(s)", type=["xlsx", "xls"], accept_multiple_files=True)
income_negative = st.radio("Are income and expense amounts negative in your file(s)?", ["Yes", "No"]) == "Yes"
years = []
dataframes = []

if uploaded_files:
    for i, uploaded_file in enumerate(uploaded_files):
        year = st.selectbox(f"Select Financial Year for file {uploaded_file.name}", options=[
            "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025"
        ], key=f"year_{i}")
        years.append(year)
        df = process_tb(uploaded_file, year, income_negative)
        if not df.empty:
            dataframes.append(df)

    if st.button("Submit and Analyze") and dataframes:
        full_data = pd.concat(dataframes, ignore_index=True)

        st.header("🔍 Summary")
        summary_table = full_data.groupby(["Financial Year", "Type"])["Amount"].sum().reset_index()
        st.dataframe(summary_table)

        st.header("📌 Top 5 Expense Heads per Year")
        for year in full_data["Financial Year"].unique():
            top_expenses = full_data[(full_data["Type"] == "Expense") & (full_data["Financial Year"] == year)]
            top_expenses_grouped = top_expenses.groupby("Account Head")["Amount"].sum().nlargest(5).reset_index()
            st.subheader(f"FY {year}")
            st.bar_chart(top_expenses_grouped.set_index("Account Head"))

        st.header("📈 Year-on-Year Income vs Expense")
        yoy_data = full_data[full_data["Type"].isin(["Income", "Expense"])]
        yoy_summary = yoy_data.groupby(["Financial Year", "Type"])["Amount"].sum().unstack().fillna(0)
        st.line_chart(yoy_summary)

        st.success("Analysis complete.")

else:
    st.info("Upload one or more TB files to begin analysis.")
