import streamlit as st
from datetime import datetime
import json
import os
import pandas as pd

# ---------- Constants ----------
DATA_FILE = "expenses.json"

# ---------- OOP Classes ----------
class Expense:
    def __init__(self, amount, category, date, description):
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

class User:
    def __init__(self, name):
        self.name = name
        self.expenses = []

    def add_expense(self, expense):
        self.expenses.append(expense)

    def get_total_by_category(self, category):
        return sum(exp.amount for exp in self.expenses if exp.category == category)

    def get_all_expenses(self):
        return self.expenses

# ---------- File Handling ----------
def save_data(user):
    data = [{"amount": exp.amount, "category": exp.category, "date": exp.date, "description": exp.description}
            for exp in user.expenses]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data(user):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                exp = Expense(item["amount"], item["category"], item["date"], item["description"])
                user.add_expense(exp)

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Expense Tracker", layout="centered")

if 'user' not in st.session_state:
    st.session_state.user = User("Faiza")
    load_data(st.session_state.user)

st.title("Personal Expense Tracker")

# ---------- Add Expense ----------
st.header("Add New Expense")
with st.form("expense_form"):
    amount = st.number_input("Amount (Rs)", min_value=0.0, format="%.2f")
    category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"])
    date = st.date_input("Date", value=datetime.today())
    description = st.text_input("Description")

    submitted = st.form_submit_button("Add Expense")
    if submitted and amount > 0:
        expense = Expense(amount, category, date.strftime("%Y-%m-%d"), description)
        st.session_state.user.add_expense(expense)
        save_data(st.session_state.user)
        st.success("Expense added successfully!")

# ---------- Filter & View Expenses ----------
st.header("All Expenses")
month = st.selectbox("Filter by Month", ["All"] + sorted({exp.date[:7] for exp in st.session_state.user.expenses}))
filtered_expenses = st.session_state.user.get_all_expenses()
if month != "All":
    filtered_expenses = [exp for exp in filtered_expenses if exp.date.startswith(month)]

for exp in filtered_expenses:
    st.write(f"**{exp.date}** | {exp.category} - Rs.{exp.amount} | _{exp.description}_")

# ---------- Summary ----------
st.header("Summary by Category")
category_totals = {
    cat: st.session_state.user.get_total_by_category(cat)
    for cat in ["Food", "Transport", "Shopping", "Bills", "Other"]
}
for cat, total in category_totals.items():
    st.write(f"{cat}: Rs.{total}")

# ---------- Chart ----------
st.header("Expense Chart")
df = pd.DataFrame.from_dict(category_totals, orient='index', columns=["Total"])
st.bar_chart(df)
