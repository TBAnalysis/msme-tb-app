import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Trial Balance Analyzer", layout="wide")
st.title("🧮 MSME Trial Balance Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload your Trial Balance file (Excel or CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Read uploaded file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            import openpyxl  # Ensure openpyxl is available
            df = pd.read_excel(uploaded_file)

        # Validate required columns
        required_cols = ["Account Head", "Type", "Amount"]
        if not all(col in df.columns for col in required_cols):
            st.error("Please make sure your file has columns: Account Head, Type, Amount")
        else:
            # Financial year and month input
            col1, col2 = st.columns(2)
            with col1:
                year = st.selectbox("Select Financial Year Start", [2022, 2023, 2024])
            with col2:
                month = st.selectbox("Select Month", ["April", "May", "June", "July", "August", "September",
                                                      "October", "November", "December", "January", "February", "March"])
            
            # Sign selection
            sign_option = st.radio("How are income and expenses represented in your TB?", 
                                   ["Income & Expenses are positive", "Income is negative, Expenses positive"])

            # Clean and adjust data
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
            df["Type"] = df["Type"].str.strip().str.title()

            if sign_option == "Income is negative, Expenses positive":
                # Invert income to positive for calculations
                df.loc[df["Type"] == "Income", "Amount"] = df.loc[df["Type"] == "Income", "Amount"].abs()

            # Total summaries
            income_total = df[df["Type"] == "Income"]["Amount"].sum()
            expense_total = df[df["Type"] == "Expense"]["Amount"].sum()
            profit = income_total - expense_total

            assets = df[df["Type"] == "Asset"]["Amount"].sum()
            liabilities = df[df["Type"] == "Liability"]["Amount"].sum()

            # Display summary
            st.subheader("Summary")
            st.markdown(f"""
            - **Financial Year:** {year}-{year+1}
            - **Month:** {month}
            - **Total Income:** ₹{income_total:,.2f}  
            - **Total Expenses:** ₹{expense_total:,.2f}  
            - **Profit:** ₹{profit:,.2f}  
            - **Assets:** ₹{assets:,.2f}  
            - **Liabilities:** ₹{liabilities:,.2f}  
            """)

            # Key ratios
            st.subheader("Key Financial Ratios")
            try:
                ratios = {
                    "Profit Margin": f"{(profit / income_total * 100):.2f}%" if income_total else "N/A",
                    "Expense to Income Ratio": f"{(expense_total / income_total * 100):.2f}%" if income_total else "N/A",
                    "Debt to Asset Ratio": f"{(liabilities / assets * 100):.2f}%" if assets else "N/A"
                }
                st.table(pd.DataFrame(ratios.items(), columns=["Metric", "Value"]))
            except:
                st.error("Error computing ratios due to missing or zero values.")

            # Visuals
            st.subheader("Breakdowns")

            col3, col4 = st.columns(2)

            with col3:
                # Income breakdown
                income_df = df[df["Type"] == "Income"].groupby("Account Head")["Amount"].sum()
                if not income_df.empty:
                    fig1, ax1 = plt.subplots()
                    ax1.pie(income_df, labels=income_df.index, autopct='%1.1f%%')
                    ax1.set_title("Income Breakdown")
                    st.pyplot(fig1)

            with col4:
                # Expense breakdown
                expense_df = df[df["Type"] == "Expense"].groupby("Account Head")["Amount"].sum()
                if not expense_df.empty:
                    fig2, ax2 = plt.subplots()
                    ax2.pie(expense_df, labels=expense_df.index, autopct='%1.1f%%')
                    ax2.set_title("Expense Breakdown")
                    st.pyplot(fig2)

            # Optional: Add more visualizations, comparisons, year-on-year trends, etc.
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a file to begin analysis.")
