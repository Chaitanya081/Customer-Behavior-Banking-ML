import streamlit as st
import pandas as pd

# ---------------------------------------
# PAGE CONFIG
# ---------------------------------------
st.set_page_config(
    page_title="Customer Management System",
    layout="wide"
)

# ---------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------
if "customers" not in st.session_state:
    st.session_state.customers = []

# ---------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select Page",
    ["Add Customer", "View Customers"]
)

# ---------------------------------------
# ADD CUSTOMER PAGE
# ---------------------------------------
if menu == "Add Customer":
    st.title("➕ Add Customer")

    name = st.text_input("Customer Name")
    balance = st.number_input("Balance", value=0.0)
    campaign = st.number_input("Campaign Calls", min_value=0, step=1)

    if st.button("Add Customer"):
        if name.strip() == "":
            st.error("Customer name cannot be empty")
        else:
            st.session_state.customers.append({
                "name": name,
                "balance": balance,
                "campaign": campaign
            })
            st.success("Customer added successfully")

    st.markdown("---")
    st.write("### Total Customers:", len(st.session_state.customers))

# ---------------------------------------
# VIEW & DELETE CUSTOMERS PAGE
# ---------------------------------------
if menu == "View Customers":
    st.title("👥 View & Delete Customers")

    st.write("### Customers Stored:", len(st.session_state.customers))

    if len(st.session_state.customers) == 0:
        st.warning("No customers available.")
    else:
        df = pd.DataFrame(st.session_state.customers)

        # DISPLAY TABLE
        st.subheader("Customer Table")
        st.dataframe(df, use_container_width=True)

        # DELETE SECTION (ALWAYS VISIBLE)
        st.subheader("🗑 Delete Customers")

        selected_names = st.multiselect(
            "Select customer(s) to delete",
            options=df["name"].tolist()
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Delete Selected"):
                st.session_state.customers = [
                    c for c in st.session_state.customers
                    if c["name"] not in selected_names
                ]
                st.success("Selected customers deleted")
                st.experimental_rerun()

        with col2:
            if st.button("Delete ALL"):
                st.session_state.customers = []
                st.warning("All customers deleted")
                st.experimental_rerun()
