import streamlit as st
import requests

# Page configuration
st.set_page_config(page_title="SharkTank Investment Simulator", layout="wide")

# 1. WEB APP MACRO LINK
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

# --- PURPLE THEME CUSTOM UI CUSTOMIZATION (CSS) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [data-testid="stAppViewContainer"], [class*="st-"] {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Banner Header Styling */
        .banner-header {
            background-color: #5B1491;
            color: #FFFFFF;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .banner-header h1 {
            color: #FFFFFF !important;
            font-weight: 700;
            margin: 0;
            font-size: 2.2rem;
        }
        .banner-header p {
            color: #E2D4F0 !important;
            margin: 0.3rem 0 0 0;
            font-size: 1rem;
        }
        
        /* Status Alerts */
        .status-bar-pending {
            background-color: #7B2CBF;
            color: white;
            padding: 0.75rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-bar-success {
            background-color: #EEDFFC;
            color: #4A1275;
            border: 1px solid #CDB4DB;
            padding: 0.75rem 1.2rem;
            border-radius: 8px;
            font-weight: 500;
            margin-bottom: 1.5rem;
        }

        /* Project Card Styling */
        .project-card {
            background-color: #F3E8FF;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border: 1px solid #E9D5FF;
        }
        .project-card-disabled {
            background-color: #E5E7EB;
            border-radius: 8px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            border: 1px solid #D1D5DB;
            color: #6B7280;
        }
        
        /* Metric Box Tweaks */
        div[data-testid="stMetricValue"] {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #4A1275 !important;
        }
        
        /* Progress Bar Base Wrapper */
        .progress-wrapper {
            background-color: #F3E8FF;
            border-radius: 20px;
            padding: 0.3rem;
            border: 1px solid #D8B4FE;
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ENGINE ---
if not st.session_state.logged_in:
    st.markdown("<div class='banner-header'><h1>🔑 Shark Tank Investment Portal</h1><p>Enter your credentials provided by the ledger admin</p></div>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        username_input = st.text_input("Username").strip().lower()
        password_input = st.text_input("Password", type="password")
        
        # Styled Login Button using custom primary style
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
    # Banner Header mirroring UI layout
    st.markdown(f"<div class='banner-header'><h1>🔑 Shark Tank Investment Portal</h1><p>Agent Ledger: {st.session_state.username.title()}</p></div>", unsafe_allow_html=True)
    
    # CASE A: SUBMISSION FINALISED & BLOCKED
    if st.session_state.has_submitted:
        st.markdown("<div class='status-bar-pending'>🔒 SUBMISSION LOCKED: Your investment ledger data has been sent safely to the master node.</div>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Available Bank Balance", "$0")
        m2.metric("Investment Portfolio Deployed", f"${st.session_state.starting_balance:,.00f}")
        m3.metric("Ledger Status", "SUBMITTED")
        
        st.markdown("---")
        st.success("Your changes have been locked dynamically by the admin ledger setup.")
        
    # CASE B: UNLOCKED LIVE GAME SESSION
    else:
        # 1. Top Message Status Bar
        st.markdown("<div class='status-bar-pending'>🛑 PENDING: Please allocate all funds dynamically using the allocation tools.</div>", unsafe_allow_html=True)
        
        # Temporary allocation logic block to evaluate balance state before rendering sliders
        total_allocated = 0.0
        temp_allocations = {}
        for company in st.session_state.companies:
            if company.strip().lower() != st.session_state.user_own_company.strip().lower():
                # Fetch what is currently in widget state, default to 0
                temp_allocations[company] = float(st.session_state.get(f"slider_{company}", 0))
                total_allocated += temp_allocations[company]
        
        remaining_balance = st.session_state.starting_balance - total_allocated

        # 2. Key Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Available Bank Balance", f"${max(0.0, remaining_balance):,.00f}")
        m2.metric("Investment Portfolio Deployed", f"${total_allocated:,.00f}")
        
        if remaining_balance == 0:
            m3.metric("Ledger Status", "READY")
        elif remaining_balance < 0:
            m3.metric("Ledger Status", "OVER BUDGET")
        else:
            m3.metric("Ledger Status", "PENDING")

        # 3. Success Feedback Row
        st.markdown("<div class='status-bar-success'>✓ Portfolio settings successfully rendered. Ready for changes.</div>", unsafe_allow_html=True)
        
        st.markdown("### Student Projects for Investment")
        
        # 4. Two-Column Dynamic Sliders Grid
        col1, col2 = st.columns(2)
        allocations = {}
        
        for idx, company in enumerate(st.session_state.companies):
            is_restricted = company.strip().lower() == st.session_state.user_own_company.strip().lower()
            target_col = col1 if idx % 2 == 0 else col2
            
            with target_col:
                if is_restricted:
                    # Restricted UI Block (Grayed Out Card)
                    st.markdown(f"""
                        <div class='project-card-disabled'>
                            <b style='font-size:1.1rem;'>{company} - OWN PROJECT - RESTRICTED</b><br/>
                            <small>You cannot invest in your own team's project to preserve fair play metrics.</small>
                        </div>
                    """, unsafe_allow_html=True)
                    # Disabled element placeholder to visually fill space perfectly
                    st.button("Investment Disabled", key=f"btn_{company}", disabled=True, use_container_width=True)
                    allocations[company] = 0.0
                else:
                    # Active Card Box Wrapper open
                    st.markdown(f"<div class='project-card'><b style='font-size:1.1rem; color:#4A1275;'>{company}</b>", unsafe_allow_html=True)
                    
                    # UX Improvement: Cap the slider max at remaining balance + whatever is already in this slider
                    current_val = st.session_state.get(f"slider_{company}", 0)
                    allowed_max = int(remaining_balance + current_val)
                    
                    # Prevent edge-case errors if allowed max drops below 0 due to structural modifications
                    allowed_max = max(0, allowed_max)
                    
                    amt = st.slider(
                        label="Drag slider to set allocation amount",
                        min_value=0,
                        max_value=max(int(st.session_state.starting_balance), allowed_max), # Keeps range healthy but limits interaction gracefully
                        step=5000,
                        format="$%d",
                        key=f"slider_{company}"
                    )
                    
                    # Small calculation to compute percent distribution metric
                    pct = (amt / st.session_state.starting_balance) * 100 if st.session_state.starting_balance > 0 else 0
                    st.markdown(f"<div style='text-align:right; font-weight:600; color:#5B1491;'>Allocated: ${amt:,.00f} ({pct:.0f}%)</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True) # Active Card Box Wrapper Close
                    
                    allocations[company] = float(amt)

        # Recompute totals clearly based on actual changes 
        final_allocated = sum(allocations.values())
        final_remaining = st.session_state.starting_balance - final_allocated
        progress_percentage = min(100, int((final_allocated / st.session_state.starting_balance) * 100))
        
        st.markdown("---")
        
        # 5. Bottom Control Row (Progress Meter + Finalise submission button)
        b_col1, b_col2 = st.columns([3, 1])
        
        with b_col1:
            st.markdown(f"<div style='text-align:center; font-weight:600; margin-bottom:2px;'>Overall Investment Progress: {progress_percentage}%</div>", unsafe_allow_html=True)
            st.progress(progress_percentage / 100)
            
            # Budget warnings displayed right below progress layout
            if final_remaining > 0:
                st.warning(f"⚠️ Allocation remaining: Please deploy your leftover ${final_remaining:,.00f} budget.")
                is_ready = False
            elif final_remaining < 0:
                st.error(f"🚨 Deficit error! Please lower allocations to clean up your balance deficit.")
                is_ready = False
            else:
                st.success("✅ Budget perfectly distributed! Ready to log entries.")
                is_ready = True

        with b_col2:
            st.write("") # Spacer logic alignment check
            if st.button("Sign and Finalise Investment", type="primary", use_container_width=True, disabled=not is_ready):
                with st.spinner("Signing to master ledger node..."):
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

    # Sidebar Log-off controls configuration
    if st.sidebar.button("Exit Console"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.starting_balance = 0.0
        st.session_state.has_submitted = False
        st.session_state.companies = []
        st.session_state.user_own_company = ""
        st.rerun()
