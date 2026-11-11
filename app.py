import streamlit as st
import pandas as pd
import json, os
from datetime import datetime

st.title("💰 Expense Tracker")

FILE = "data.json"

# Load data
def load():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

# Save data
def save(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

records = load()

# Menu
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Add Income", "Add Expense", "View Records"]
)
if st.sidebar.button("Reset All Data"):
    save([])
    st.success("All data has been reset!")
    st.rerun()
# Add Income / Expense
if menu in ["Add Income", "Add Expense"]:

    st.header(menu)

    with st.form("transaction_form", clear_on_submit=True):

        amount = st.number_input("Amount", min_value=0.0)
        category = st.text_input("Category")
        note = st.text_input("Note")

        submit = st.form_submit_button("Submit")

        if submit:

            if amount > 0 and category.strip():

                records.append({
                    "type": menu.replace("Add ", ""),
                    "amount": amount,
                    "category": category,
                    "note": note,
                    "date": datetime.now().strftime("%d-%m-%Y"),
                    "time": datetime.now().strftime("%I:%M %p")
                })

                save(records)
                st.success("Transaction Added!")

            else:
                st.warning("Enter valid details")

# View Records
elif menu == "View Records":

    st.header("Transaction History")

    if records:

        df = pd.DataFrame(records)

        dates = pd.to_datetime(
            df["date"], format="%d-%m-%Y", errors="coerce"
        ).dropna()

        if not dates.empty:

            start, end = st.date_input(
                "Select Date Range",
                value=(dates.min().date(), dates.max().date())
            )

            df["_date"] = pd.to_datetime(
                df["date"], format="%d-%m-%Y", errors="coerce"
            )

            df = df[
                (df["_date"].dt.date >= start) &
                (df["_date"].dt.date <= end)
            ]

        st.dataframe(
            df.drop(columns=["_date"], errors="ignore"),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No records found")

# Dashboard
elif menu == "Dashboard":

    income = sum(
        r["amount"] for r in records
        if r["type"] == "Income"
    )

    expense = sum(
        r["amount"] for r in records
        if r["type"] == "Expense"
    )

    st.header("Financial Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric("Income", f"₹{income:,.2f}")
    c2.metric("Expense", f"₹{expense:,.2f}")
    c3.metric("Balance", f"₹{income-expense:,.2f}")

    st.subheader("Income vs Expense")

    st.bar_chart(pd.DataFrame({
        "Amount": [income, expense]
    }, index=["Income", "Expense"]))

    # Category-wise expenses
    expenses = pd.DataFrame([
        r for r in records if r["type"] == "Expense"
    ])

    if not expenses.empty:

        st.subheader("Category-wise Expenses")

        st.bar_chart(
            expenses.groupby("category")["amount"].sum()
        )

    # Recent records
    st.subheader("Recent Transactions")

    if records:
        st.dataframe(
            records[-5:][::-1],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No transactions yet")