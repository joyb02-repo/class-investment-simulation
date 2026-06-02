import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Set up page layout
st.set_page_config(page_title="Class Investment Dashboard", layout="centered")

# 1. PRE-ALLOCATED STUDENT CREDENTIALS
STUDENT_DB = {
    "student1": "pass123",
    "student2": "blue456",
    "student3": "green789",
    "student4": "apple000",
    "student5": "soccer11"
}

# 2. SPREADSHEET CONFIGURATION
# Paste your spreadsheet URL or ID here
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1zn9AQFSMaB5lKRR-FTKJ07SQP8MGaRYH5nrVwBc0uzc/edit?usp=sharing"

# Initialize Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. SESSION STATE INITIALIZATION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.title("🔐 Student Login Portal")
    st.markdown("Please enter your pre-allocated credentials to access the simulation.")
    
    username_input = st.text_input("Username").strip().lower()
    password_input = st.text_input("Password", type="password")
    
    if st.button("Login", use_container_width=True):
        if username_input in STUDENT_DB and STUDENT_DB[username_input] == password_input:
            st.session_state.logged_in = True
            st.session_state.username = username_input
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

# --- MAIN DASHBOARD SIMULATION ---
else:
    st.title("💼 Class Investment Dashboard")
    st.write(f"Welcome back, **{st.session_state.username.capitalize()}**!")
    st.markdown("---")

    STARTING_BALANCE = 100000.00
    companies = ["Company A", "Company B", "Company C", "Company D", "Company E", "Company F"]

    st.write("### 🏦 Your Portfolio Allocations")
    st.write("Allocate your funds below. Your total investment cannot exceed **$100,000**.")

    # Create input boxes dynamically
    allocations = {}
    total_allocated = 0.0

    col1, col2 = st.columns(2)
    for idx, company in enumerate(companies):
        with col1 if idx % 2 == 0 else col2:
            amount = st.number_input(
                f"Allocation for {company} ($)", 
                min_value=0.0, 
                max_value=100000.0, 
                step=1000.0, 
                value=0.0,
                key=f"input_{company}"
            )
            allocations[company] = amount
            total_allocated += amount

    remaining_balance = STARTING_BALANCE - total_allocated

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Bank Balance", "$100,000")
    m2.metric("Total Invested", f"${total_allocated:,.2f}")
    
    if remaining_balance < 0:
        m3.metric("Remaining Cash", f"${remaining_balance:,.2f}", delta="OVER BUDGET", delta_color="inverse")
        st.error(f"🚨 You are over budget! Please reduce your allocations before finalising.")
    else:
        m3.metric("Remaining Cash", f"${remaining_balance:,.2f}")

    st.markdown("---")

    if st.button("🚀 Finalise Investment", type="primary", use_container_width=True, disabled=(remaining_balance < 0)):
        with st.spinner("Connecting to master sheet and saving your choices..."):
            try:
                # 1. Pull the current data safely from the public sharing URL
                df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
                
                # Clean up columns if the sheet is completely pristine/empty
                if df.empty or "Student" not in df.columns:
                    df = pd.DataFrame(columns=["Student", "Company A", "Company B", "Company C", "Company D", "Company E", "Company F"])

                # Ensure values are strings for clean checking
                df["Student"] = df["Student"].astype(str).str.strip().str.lower()
                current_user = st.session_state.username.strip().lower()

                # 2. Build the new data dictionary row
                new_data = {
                    "Student": st.session_state.username,
                    "Company A": allocations["Company A"],
                    "Company B": allocations["Company B"],
                    "Company C": allocations["Company C"],
                    "Company D": allocations["Company D"],
                    "Company E": allocations["Company E"],
                    "Company F": allocations["Company F"]
                }

                # 3. Check for duplicates or append a new entry
                if current_user in df["Student"].values:
                    # Update row index where student is found
                    idx = df[df["Student"] == current_user].index[0]
                    for col, val in new_data.items():
                        df.at[idx, col] = val
                    msg = "📝 Your existing allocations have been successfully updated!"
                else:
                    # Append row if student doesn't exist yet
                    new_row_df = pd.DataFrame([new_data])
                    df = pd.concat([df, new_row_df], ignore_index=True)
                    msg = "🎯 Investment successfully completed! Your allocations have been registered."

                # 4. Push the modified dataframe right back up to Google Sheets
                conn.update(spreadsheet=SPREADSHEET_URL, data=df)
                st.success(msg)
                
            except Exception as ex:
                st.error(f"Failed to submit data to the sheet. Verify link accessibility settings. Details: {ex}")

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
