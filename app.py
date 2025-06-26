import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Trial Balance Analyzer", layout="wide")

st.title("📊 MSME Trial Balance Analyzer")

# Upload file
uploaded_file = st.file_uploader("Upload your Trial Balance (Excel or CSV)", type=["xlsx", "xls", "csv"])

# Period selection
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Select Financial Year", ["2022-23", "2023-24", "2024-25"])
with col2:
    selected_month = st.selectbox("Select Month", ["April", "May", "June", "July", "August", "September", 
                                                   "October", "November", "December", "January", "February", "March"])

# Polarity selection
polarity = st.radio(
    "How is your TB represented?",
    ["Income/Expense shown as Positive", "Income shown Negative, Expense Positive"]
)

# Define RAG thresholds
RAG_THRESHOLDS = {
    "Salaries": 0.5,       # e.g. Salaries > 50% of total expenses → Red
    "Rent": 0.3,           # Rent > 30% → Red
    "Professional Fees": 0.3,
    "Travel": 0.2,
    "Utilities": 0.2
}

# Analysis
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip()
        required_cols = ["Account Head", "Type", "Amount"]
        if not all(col in df.columns for col in required_cols):
            st.error("Please ensure the file has these 3 columns: Account Head, Type, Amount")
        else:
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)

            # Adjust polarity
            if polarity == "Income shown Negative, Expense Positive":
                income_df = df[df["Type"].str.lower() == "income"]
                expense_df = df[df["Type"].str.lower() == "expense"]
                asset_df = df[df["Type"].str.lower() == "asset"]
                liability_df = df[df["Type"].str.lower() == "liability"]

                income_df["Amount"] = income_df["Amount"].abs()
                df = pd.concat([income_df, expense_df, asset_df, liability_df], ignore_index=True)

            # Summary calculations
            total_income = df[df["Type"].str.lower() == "income"]["Amount"].sum()
            total_expense = df[df["Type"].str.lower() == "expense"]["Amount"].sum()
            profit = total_income - total_expense

            st.subheader("📌 Summary")
            st.metric("Total Income", f"₹{total_income:,.0f}")
            st.metric("Total Expenses", f"₹{total_expense:,.0f}")
            st.metric("Profit", f"₹{profit:,.0f}")

            st.divider()

            # Expense Breakdown
            st.subheader("🧾 Expense Breakdown by Account Head")
            expense_data = df[df["Type"].str.lower() == "expense"].groupby("Account Head")["Amount"].sum().sort_values(ascending=False)

            fig1, ax1 = plt.subplots()
            ax1.pie(expense_data, labels=expense_data.index, autopct='%1.1f%%')
            ax1.axis('equal')
            st.pyplot(fig1)

            st.bar_chart(expense_data)

            st.divider()

            # RAG Analysis
            st.subheader("🚦 Expense Hygiene Check (RAG Status)")
            rag_summary = []
            for head, threshold in RAG_THRESHOLDS.items():
                value = expense_data.get(head, 0)
                pct = value / total_expense if total_expense else 0
                status = "🟢 Good"
                if pct > threshold:
                    status = "🔴 High"
                elif pct > threshold * 0.75:
                    status = "🟠 Amber"
                rag_summary.append((head, f"₹{value:,.0f}", f"{pct:.1%}", status))

            rag_df = pd.DataFrame(rag_summary, columns=["Account Head", "Amount", "% of Expenses", "Status"])
            st.dataframe(rag_df)

            st.divider()

            # Balance Sheet Overview
            st.subheader("📚 Balance Sheet Overview")

            col1, col2 = st.columns(2)
            with col1:
                asset_sum = df[df["Type"].str.lower() == "asset"]["Amount"].sum()
                st.metric("Total Assets", f"₹{asset_sum:,.0f}")
            with col2:
                liability_sum = df[df["Type"].str.lower() == "liability"]["Amount"].sum()
                st.metric("Total Liabilities", f"₹{liability_sum:,.0f}")

            st.caption(f"Data shown for period: {selected_month} {selected_year}")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload your Trial Balance file to begin.")
