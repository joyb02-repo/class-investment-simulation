import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Set up page layout
st.set_page_config(page_title="Class Investment Dashboard", layout="centered")

# 1. 50 PRE-ALLOCATED STUDENT CREDENTIALS
STUDENT_DB = {
    "user101": "fox32",   "user102": "bear7",   "user103": "wolf9",   "user104": "lion4",
    "user105": "deer2",   "user106": "hawk6",   "user107": "frog5",   "user108": "duck8",
    "user109": "swan3",   "user110": "crab1",   "user111": "fish8",   "user112": "bird4",
    "user113": "cats9",   "user114": "dogs2",   "user115": "mice5",   "user116": "owls7",
    "user117": "seals1",  "user118": "ants3",   "user119": "bees6",   "user120": "bugs8",
    "user121": "blue4",   "user122": "red95",   "user123": "green2",  "user124": "pink7",
    "user125": "gold3",   "user126": "neon6",   "user127": "aqua1",   "user128": "plum8",
    "user129": "gray5",   "user130": "mint9",   "user131": "zinc4",   "user132": "iron2",
    "user133": "clay7",   "user134": "rock3",   "user135": "sand5",   "user136": "wave1",
    "user137": "wind8",   "user138": "fire6",   "user139": "star2",   "user140": "moon9",
    "user141": "tree4",   "user142": "leaf7",   "user143": "root1",   "user144": "fern5",
    "user145": "bark3",   "user146": "seed8",   "user147": "rose2",   "user148": "iris6",
    "user149": "moss9",   "user150": "vine1"
}

# 2. SPREADSHEET CONFIGURATION
# 🔴 Paste your actual Google Sheet sharing URL or ID inside the quotes below:
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
    st.write("You must allocate **exactly $100,000** across the companies before you can submit.")

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
    
    # Check balance status and show appropriate warnings
    if remaining_balance < 0:
        m3.metric("Remaining Cash", f"${remaining_balance:,.2f}", delta="OVER BUDGET", delta_color="inverse")
        st.error(f"🚨 You are over budget! Please reduce your allocations by ${abs(remaining_balance):,.2f}.")
        is_ready_to_submit = False
    elif remaining_balance > 0:
        m3.metric("Remaining Cash", f"${remaining_balance:,.2f}", delta="FUNDS REMAINING", delta_color="off")
        st.warning(f"⚠️ You must allocate your remaining **${remaining_balance:,.2f}** to finalise your investment.")
        is_ready_to_submit = False
    else:
        m3.metric("Remaining Cash", "$0.00", delta="FULLY ALLOCATED", delta_color="normal")
        st.success("✅ Perfect! Your full $100,000 balance has been deployed.")
        is_ready_to_submit = True

    st.markdown("---")

    # The button is disabled unless the remaining balance is exactly 0
    if st.button("🚀 Finalise Investment", type="primary", use_container_width=True, disabled=not is_ready_to_submit):
        with st.spinner("Connecting to master sheet and saving your choices..."):
            try:
                # 1. Pull current data from the shared sheet
                df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
                
                if df.empty or "Student" not in df.columns:
                    df = pd.DataFrame(columns=["Student", "Company A", "Company B", "Company C", "Company D", "Company E", "Company F"])

                df["Student"] = df["Student"].astype(str).str.strip().str.lower()
                current_user = st.session_state.username.strip().lower()

                # 2. Build the new data row
                new_data = {
                    "Student": st.session_state.username,
                    "Company A": allocations["Company A"],
                    "Company B": allocations["Company B"],
                    "Company C": allocations["Company C"],
                    "Company D": allocations["Company D"],
                    "Company E": allocations["Company E"],
                    "Company F": allocations["Company F"]
                }

                # 3. Overwrite existing data or append as a new entry
                if current_user in df["Student"].values:
                    idx = df[df["Student"] == current_user].index[0]
                    for col, val in new_data.items():
                        df.at[idx, col] = val
                    msg = "📝 Your existing investment selections have been updated!"
                else:
                    new_row_df = pd.DataFrame([new_data])
                    df = pd.concat([df, new_row_df], ignore_index=True)
                    msg = "🎯 Investment successfully completed! Your allocations have been registered."

                # 4. Push data back to Google Sheets
                conn.update(spreadsheet=SPREADSHEET_URL, data=df)
                st.success(msg)
                
            except Exception as ex:
                st.error(f"Failed to submit data to the sheet. Verify spreadsheet link access permissions. Details: {ex}")

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
