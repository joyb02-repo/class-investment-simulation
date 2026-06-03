import streamlit as st
import requests
import os

# Page configuration
st.set_page_config(page_title="SharkTank Investment Simulator", layout="centered")

# 1. UPDATED WEB APP MACRO LINK
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz-9n2foZ57LRw6WM-C6CRYewWTy-cv6ftMZ-dTqSr4zRZ1Q8mvHgT3TPq1CLeVOdrY/exec"

# 2. SESSION STATE INITIALIZATION
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "starting_balance" not in st.session_state:
    st.session_state.starting_balance = 0.0
if "has_submitted" not in st.session_state:
    st.session_state.has_submitted = False
if "companies" not in st.session_state:
    st.session_state.companies = []
if "user_own_company" not in st.session_state:
    st.session_state.user_own_company = ""

# --- LOGO RENDERING ENGINE ---
def render_top_logo():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    else:
        st.markdown("<h2 style='text-align: center; color: #8B5CF6; letter-spacing: 2px; font-weight:700; margin-bottom:0;'>SHARK TANK</h2>", unsafe_allow_html=True)

# --- CORE PREMIUM LIGHT UI SYSTEM OVERRIDES (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Typography Normalization */
        html, body, [data-testid="stAppViewContainer"], [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Center Logo Automatically */
        [data-testid="stImage"] {
            margin: 0 auto !important;
            display: block;
        }

        /* Workspace Header Elements */
        .main-header {
            text-align: center;
            margin-top: 0.5rem;
            margin-bottom: 2rem;
        }
        .main-header h1 {
            font-weight: 700;
            letter-spacing: -0.05rem;
            color: #1E293B;
            margin-bottom: 0.2rem;
            font-size: 1.8rem;
        }
        .main-header p {
            color: #64748B;
            font-size: 1rem;
        }
        
        /* TARGETED SLIDER STYLING - Forces Purple Handles and Tracks Only */
        div[data-testid="stSlider"] [data-testid="stThumbvalue"] {
            font-weight: 700 !important;
            color: #8B5CF6 !important;
        }
        div[data-testid="stSlider"] > div > div > div {
            background-color: #8B5CF6 !important;
            height: 8px !important;              
            border-radius: 9999px !important;
        }
        div[data-testid="stSlider"] [role="slider"] {
            width: 20px !important;              
            height: 20px !important;
            background-color: #FFFFFF !important;
            border: 4px solid #8B5CF6 !important;
            box-shadow: 0px 2px 4px rgba(139, 92, 246, 0.3);
        }
        
        /* Enforces slider scale markers to stay dark gray, stopping the red color bleed */
        div[data-testid="stSlider"] div[data-testid="styledTickBar"] div {
            color: #64748B !important;
            font-weight: 500 !important;
        }
        
        /* Targets the text labels inside the container card block */
        div[data-testid="stVerticalBlockBorderWrapper"] label p {
            font-size: 1.05rem !important;
            color: #1E293B !important;
        }
        
        /* Custom Curving Container Box Injection */
        div[data-testid="stVerticalBlockBorderWrapper"]:has(div[id^="slider_"]) {
            background-color: rgba(139, 92, 246, 0.04) !important;
            border: 1px solid rgba(139, 92, 246, 0.15) !important;
            border-radius: 18px !important;
            padding: 28px !important;
        }
        
        /* Layout Metrics Architecture Configuration */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.03rem;
        }
        div[data-testid="stMetricLabel"] {
            font-weight: 600 !important;
            color: #475569 !important;
        }
        
        /* Premium Curved Theme Primary Actions Button */
        div.stButton > button[kind="primary"] {
            background-color: #8B5CF6 !important;
            border: none !important;
            color: white !important;
            font-weight: 600 !important;
            border-radius: 9999px !important;
            padding: 0.6rem 2rem !important;
            transition: all 0.2s ease;
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: #7C3AED !important;
            box-shadow: 0px 4px 12px rgba(124, 58, 237, 0.3);
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ENGINE ---
if not st.session_state.logged_in:
    render_top_logo()
    st.markdown("<div class='main-header'><h1>Investment Portal</h1><p>Enter your assigned authorization credentials</p></div>", unsafe_allow_html=True)
    
    username_input = st.text_input("Username").strip().lower()
    password_input = st.text_input("Password", type="password")
    
    if st.button("Access Dashboard", use_container_width=True, type="primary"):
        if not username_input or not password_input:
            st.warning("Please enter both fields.")
        else:
            with st.spinner("Authenticating credential access parameters..."):
                try:
                    params = {"username": username_input, "password": password_input}
                    response = requests.get(WEB_APP_URL, params=params, timeout=10)
                    res_data = response.json()
                    
                    if response.status_code == 200 and res_data.get("status") == "success" and res_data.get("auth") == True:
                        st.session_state.username = username_input
                        st.session_state.starting_balance = float(res_data.get("balance", 0.0))
                        st.session_state.user_own_company = res_data.get("restricted", "")
                        st.session_state.has_submitted = res_data.get("hasSubmitted", False)
                        
                        if res_data.get("companies"):
                            st.session_state.companies = res_data.get("companies")
                            
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Access Denied. Invalid username or password verified by sheet.")
                except Exception as e:
                    st.error(f"Failed to communicate with authentication servers: {e}")

# --- LIVE PORTFOLIO ---
else:
    render_top_logo()
    st.markdown(f"<div class='main-header'><h1>Portfolio Console</h1><p>Agent Ledger: <b>{st.session_state.username.upper()}</b></p></div>", unsafe_allow_html=True)
    
    # CASE A: SUBMISSION FINALISED & BLOCKED
    if st.session_state.has_submitted:
        m1, m2, m3 = st.columns(3)
        m1.metric("Available Bank Balance", "$0.00")
        m2.metric("Investment Portfolio Deployed", f"${st.session_state.starting_balance:,.2f}")
        m3.metric("Ledger Status", "LOCKED", delta="SUBMITTED", delta_color="normal")
        
        st.markdown("---")
        st.success("Your investment portfolio has been finalised. Active modifications are restricted by the ledger admin.")
        
    # CASE B: UNLOCKED LIVE GAME SESSION
    else:
        # Layout metrics container pinned safely at the absolute top layout
        top_metrics_container = st.container()
        
        st.markdown("---")
        
        total_allocated = 0.0
        allocations = {}
        
        # Native safe block wrapping behind sliders
        with st.container(border=True):
            col1, col2 = st.columns(2)
            for idx, company in enumerate(st.session_state.companies):
                with col1 if idx % 2 == 0 else col2:
                    if company.strip().lower() == st.session_state.user_own_company.strip().lower():
                        amt = st.slider(
                            label=f"Invest in **{company}** (Your Assigned Company - Restricted)",
                            min_value=0,
                            max_value=5000,
                            step=5000,
                            value=0,
                            format="$%d",
                            key=f"slider_{company}",
                            disabled=True
                        )
                    else:
                        amt = st.slider(
                            label=f"Invest in **{company}**",
                            min_value=0,
                            max_value=int(st.session_state.starting_balance),
                            step=5000,
                            value=0,
                            format="$%d",
                            key=f"slider_{company}"
                        )
                    allocations[company] = float(amt)
                    total_allocated += float(amt)
                
        remaining_balance = st.session_state.starting_balance - total_allocated
        
        # --- RENDER TOP METRICS & COLOR CHECKS ---
        with top_metrics_container:
            m1, m2, m3 = st.columns(3)
            
            if remaining_balance < 0:
                # DEEP DEFCIT RED: Strictly targets metric block text values without bleeding into sliders
                st.markdown("""
                    <style>
                        div[data-testid="stMetricBlock"]:nth-of-type(1) div[data-testid="stMetricValue"] > div {
                            color: #DC2626 !important;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                m1.metric("Available Bank Balance", f"-${abs(remaining_balance):,.00f}")
                m2.metric("Investment Total", f"${total_allocated:,.00f}")
                m3.metric("Deficit Check", f"${abs(remaining_balance):,.00f}", delta="OVER BUDGET", delta_color="inverse")
                
                st.error(f"Account overallocated! Adjust your sliders down to balance budget by ${abs(remaining_balance):,.2f}.")
                is_ready = False
            else:
                # VIBRANT ACCENT PURPLE: Formats normal balance metrics safely
                st.markdown("""
                    <style>
                        div[data-testid="stMetricBlock"]:nth-of-type(1) div[data-testid="stMetricValue"] > div {
                            color: #8B5CF6 !important;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                m1.metric("Available Bank Balance", f"${remaining_balance:,.00f}")
                m2.metric("Investment Total", f"${total_allocated:,.00f}")
                
                if remaining_balance > 0:
                    m3.metric("Ledger Status", "PENDING", delta="UNALLOCATED FUNDS", delta_color="off")
                    st.warning(f"Allocation required: Complete deployment of remaining ${remaining_balance:,.00f} to finalize.")
                    is_ready = False
                else:
                    m3.metric("Ledger Status", "READY", delta="BALANCED", delta_color="normal")
                    st.success(f"Complete assignment of your ${st.session_state.starting_balance:,.00f} budget validated.")
                    is_ready = True

        st.markdown("---")

        if st.button("Finalise Investment", type="primary", use_container_width=True, disabled=not is_ready):
            with st.spinner("Encrypting allocations and signing to master node..."):
                try:
                    payload = {"Student": st.session_state.username}
                    payload.update(allocations)
                    
                    response = requests.post(WEB_APP_URL, json=payload, timeout=10)
                    result = response.json()
                    
                    if response.status_code == 200 and result.get("status") == "success":
                        st.session_state.has_submitted = True
                        st.success("Data signed cleanly.")
                        st.rerun()
                    else:
                        st.error(f"Error: {result.get('message')}")
                except Exception as ex:
                    st.error(f"Network processing failed: {ex}")

    if st.sidebar.button("Exit Console"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.starting_balance = 0.0
        st.session_state.has_submitted = False
        st.session_state.companies = []
        st.session_state.user_own_company = ""
        st.rerun()
