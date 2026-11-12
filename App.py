import base64
import html
from pathlib import Path

import requests
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SharkTank Investment Simulator",
    page_icon="🦈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 1. WEB APP MACRO LINK
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz-9n2foZ57LRw6WM-C6CRYewWTy-cv6ftMZ-dTqSr4zRZ1Q8mvHgT3TPq1CLeVOdrY/exec"

# 2. SESSION STATE INITIALIZATION
DEFAULTS = {
    "logged_in": False,
    "username": "",
    "starting_balance": 0.0,
    "has_submitted": False,
    "companies": [],
    "descriptions": {},
    "user_own_company": "",
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
esc = html.escape


def money(x: float) -> str:
    return f"${x:,.0f}"


@st.cache_data
def logo_b64() -> str:
    path = Path(__file__).parent / "logo.png"
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode()
    return ""


def logo_html(height: int) -> str:
    data = logo_b64()
    if not data:
        return "<span class='wordmark'>SHARK TANK</span>"
    return f'<img class="logo" src="data:image/png;base64,{data}" style="height:{height}px" alt="Shark Tank">'


def budget_panel(total: float, invested: float, state: str, message: str) -> str:
    """Dark budget bar. state is one of: pending, ready, over, locked."""
    left = total - invested
    pct = 0 if total <= 0 else max(0, min(invested / total * 100, 100))
    left_txt = ("-" if left < 0 else "") + money(abs(left))
    return (
        f'<div class="budget {state}">'
        f'<div class="budget-row">'
        f'<div><div class="budget-label">Left to invest</div><div class="budget-num">{left_txt}</div></div>'
        f'<div class="budget-side"><div class="budget-label">Invested</div>'
        f'<div class="budget-num small">{money(invested)}</div>'
        f'<div class="budget-of">of {money(total)}</div></div>'
        f"</div>"
        f'<div class="bar"><div class="fill" style="width:{pct:.1f}%"></div></div>'
        f'<div class="budget-msg">{esc(message)}</div>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --ink: #2A2933;
    --slate: #55525E;
    --paper: #F4F3F7;
    --card: #FFFFFF;
    --line: #DEDCE6;
    --muted: #6E6B7B;
    --accent: #7B2CBF;
    --accent-dark: #621F9C;
    --ok: #4ADE80;
    --bad: #F87171;
}

html, body, [data-testid="stAppViewContainer"],
[class*="st-"]:not([data-testid="stIconMaterial"]):not([class*="material"]) {
    font-family: 'Inter', sans-serif !important;
}
/* Keep Streamlit's icon glyphs (password eye, sidebar arrows) on their icon font */
[data-testid="stIconMaterial"], [class*="material-symbols"], [class*="material-icons"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
}
/* The "Press Enter to submit form" hint collides with the password eye icon */
[data-testid="InputInstructions"] { display: none !important; }
[data-testid="stAppViewContainer"], [data-testid="stApp"] { background: var(--paper); }
.block-container { padding-top: 5.5rem; padding-bottom: 4rem; max-width: 760px; }
#MainMenu, footer { visibility: hidden; }

/* ---------- Logo and headings ---------- */
.logo { display: block; }
.wordmark { font-family: 'Anton', sans-serif; color: var(--slate); font-size: 1.6rem; letter-spacing: 0.02em; }

.login-head { text-align: center; margin: 1rem 0 1.5rem 0; }
.login-head .logo { margin: 0 auto 1.4rem auto; }
.login-head .login-title {
    font-family: 'Anton', sans-serif !important;
    font-weight: 400;
    font-size: 2.2rem;
    letter-spacing: 0.01em;
    color: var(--ink);
    margin: 0 0 0.3rem 0;
    padding: 0;
}
.login-head p { color: var(--muted); margin: 0; font-size: 0.98rem; }

.topbar-user { color: var(--muted); font-size: 0.9rem; line-height: 1.3; }
.topbar-user b { color: var(--ink); font-size: 1rem; }
.topbar { display: flex; align-items: center; gap: 1rem; }

/* ---------- Login form ---------- */
[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 1.5rem;
}

/* ---------- Buttons ---------- */
button[data-testid="stBaseButton-primary"], button[kind="primary"], [data-testid="stFormSubmitButton"] button {
    background: var(--accent);
    border: 1px solid var(--accent);
    color: #fff;
    font-weight: 600;
    border-radius: 10px;
    min-height: 2.9rem;
}
button[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] button:hover {
    background: var(--accent-dark);
    border-color: var(--accent-dark);
    color: #fff;
}
button[data-testid="stBaseButton-primary"]:disabled, button[kind="primary"]:disabled {
    background: var(--line);
    border-color: var(--line);
    color: #9A97A8;
}
button[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--card);
    color: var(--ink);
    font-weight: 500;
}
button:focus-visible { outline: 3px solid rgba(123, 44, 191, 0.45) !important; outline-offset: 2px; }

/* ---------- Budget bar (sticky) ---------- */
.st-key-budgetbar {
    position: sticky;
    top: 3.6rem;
    z-index: 50;
    background: var(--paper);
    padding: 0.5rem 0 0.75rem 0;
}
.budget {
    background: var(--ink);
    color: #fff;
    border-radius: 14px;
    padding: 1.1rem 1.4rem 1rem 1.4rem;
}
.budget-row { display: flex; justify-content: space-between; align-items: flex-end; gap: 1rem; }
.budget-label { font-size: 0.85rem; color: #B9B6C6; margin-bottom: 0.15rem; }
.budget-num { font-family: 'Anton', sans-serif; font-size: 2.8rem; line-height: 1.05; letter-spacing: 0.01em; }
.budget-num.small { font-size: 1.5rem; }
.budget-side { text-align: right; }
.budget-of { font-size: 0.8rem; color: #B9B6C6; margin-top: 0.1rem; }
.bar { height: 8px; background: #43414E; border-radius: 99px; margin: 0.9rem 0 0.7rem 0; overflow: hidden; }
.fill { height: 100%; border-radius: 99px; background: #B57BEA; transition: width 0.25s ease; }
.budget-msg { font-size: 0.92rem; color: #E6E4EE; }
.budget.ready .fill, .budget.locked .fill { background: var(--ok); }
.budget.ready .budget-num:first-of-type, .budget.locked .budget-num:first-of-type { color: var(--ok); }
.budget.over .fill { background: var(--bad); }
.budget.over .budget-num:first-of-type { color: var(--bad); }

/* ---------- Company cards ---------- */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border-color: var(--line);
    border-radius: 12px;
}
.co-name { font-weight: 600; color: var(--ink); font-size: 1.02rem; line-height: 1.25; margin: 0; }
.co-name:last-child { margin-bottom: 1rem; }   /* no description: still space above the slider */
.co-note { font-size: 0.85rem; color: var(--muted); line-height: 1.3; margin: 0.05rem 0 1rem 0; }
.co-tag {
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--slate);
    background: #ECEAF1;
    border-radius: 6px;
    padding: 0.1rem 0.5rem;
    margin-left: 0.5rem;
    vertical-align: middle;
}

/* ---------- Sliders (purple accents; config.toml primaryColor also handles this) ---------- */
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background-color: #7B2CBF !important;
    border-color: #7B2CBF !important;
    box-shadow: 0 0 4px rgba(123, 44, 191, 0.4) !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] div,
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] ~ div {
    color: #7B2CBF !important;
    font-weight: 600 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] div[data-disabled="true"] > div > div,
div[data-testid="stSlider"] [data-baseweb="slider"] div[data-disabled="true"] div {
    background-color: #E2E8F0 !important;
    background: #E2E8F0 !important;
    color: #94A3B8 !important;
}

/* ---------- Confirm dialog summary ---------- */
.sum { border: 1px solid var(--line); border-radius: 10px; padding: 0.4rem 1rem; margin: 0.8rem 0 1rem 0; }
.sum-row { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid var(--line); }
.sum-row:last-child { border-bottom: none; }
.sum-row.total { font-weight: 700; }

@media (max-width: 640px) {
    .budget-num { font-size: 2.2rem; }
    .budget-num.small { font-size: 1.25rem; }
}
@media (prefers-reduced-motion: reduce) {
    .fill { transition: none; }
}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# ACTIONS
# ---------------------------------------------------------------------------
def sign_out():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value
    st.rerun()


@st.dialog("Confirm your investment")
def confirm_dialog(allocations: dict, total: float):
    st.write("This is final. You won't be able to change your allocations after you submit.")

    rows = "".join(
        f'<div class="sum-row"><span>{esc(company)}</span><span>{money(amount)}</span></div>'
        for company, amount in allocations.items()
        if amount > 0
    )
    st.markdown(
        f'<div class="sum">{rows}<div class="sum-row total"><span>Total</span><span>{money(total)}</span></div></div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    if c1.button("Go back", use_container_width=True):
        st.rerun()

    if c2.button("Confirm and finalise", type="primary", use_container_width=True):
        with st.spinner("Saving your allocations..."):
            try:
                payload = {"Student": st.session_state.username}
                payload.update(allocations)

                response = requests.post(WEB_APP_URL, json=payload, timeout=10)
                result = response.json()

                if response.status_code == 200 and result.get("status") == "success":
                    st.session_state.has_submitted = True
                    st.rerun()
                else:
                    st.error(f"Your investment wasn't saved: {result.get('message')}")
            except Exception as ex:
                st.error(f"Couldn't reach the ledger. Check your connection and try again. ({ex})")


# ---------------------------------------------------------------------------
# LOGIN
# ---------------------------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown(
        f"<div class='login-head'>{logo_html(150)}"
        "<div class='login-title' role='heading' aria-level='1'>Sign in to your ledger</div>"
        "<p>Use the username and password from your ledger admin.</p></div>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username_input = st.text_input("Username").strip().lower()
        password_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True, type="primary")

    if submitted:
        if not username_input or not password_input:
            st.warning("Enter your username and password.")
        else:
            with st.spinner("Signing you in..."):
                try:
                    params = {"username": username_input, "password": password_input}
                    response = requests.get(WEB_APP_URL, params=params, timeout=10)
                    res_data = response.json()

                    if response.status_code == 200 and res_data.get("status") == "success" and res_data.get("auth") == True:
                        st.session_state.username = username_input
                        st.session_state.starting_balance = float(res_data.get("balance", 0.0))
                        st.session_state.user_own_company = res_data.get("restricted", "")  # Received from backend tab column 4
                        st.session_state.has_submitted = res_data.get("hasSubmitted", False)

                        if res_data.get("companies"):
                            st.session_state.companies = res_data.get("companies")
                        st.session_state.descriptions = res_data.get("descriptions") or {}

                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Sign-in failed. Check your username and password and try again.")
                except Exception as e:
                    st.error(f"Couldn't reach the ledger. Check your connection and try again. ({e})")

# ---------------------------------------------------------------------------
# PORTFOLIO
# ---------------------------------------------------------------------------
else:
    # Top bar: logo, who is signed in, sign out
    left, right = st.columns([4, 1], vertical_alignment="center")
    with left:
        st.markdown(
            f"<div class='topbar'>{logo_html(48)}"
            f"<div class='topbar-user'>Signed in as<br><b>{esc(st.session_state.username.upper())}</b></div></div>",
            unsafe_allow_html=True,
        )
    with right:
        if st.button("Sign out", use_container_width=True, key="signout"):
            sign_out()

    st.write("")

    # CASE A: SUBMISSION FINALISED & BLOCKED
    if st.session_state.has_submitted:
        st.markdown(
            budget_panel(
                st.session_state.starting_balance,
                st.session_state.starting_balance,
                "locked",
                "Your portfolio is finalised and locked. Only the ledger admin can change it.",
            ),
            unsafe_allow_html=True,
        )

    # CASE B: UNLOCKED LIVE GAME SESSION
    else:
        if int(st.session_state.starting_balance) < 5000:
            st.error("Your budget isn't set up correctly. Ask your ledger admin to check it.")
            st.stop()

        # Budget bar pinned at the top (sticks while scrolling)
        top_metrics_container = st.container(key="budgetbar")

        total_allocated = 0.0
        allocations = {}

        # Dynamic company grid: two cards per row so the sliders line up
        companies = st.session_state.companies
        descriptions = st.session_state.descriptions
        for row_start in range(0, len(companies), 2):
            cols = st.columns(2)
            for offset, company in enumerate(companies[row_start:row_start + 2]):
                with cols[offset]:
                    is_restricted = company.strip().lower() == st.session_state.user_own_company.strip().lower()

                    # Optional company name / description from row 2 of the sheet
                    note = str(descriptions.get(company, "") or "").strip()
                    note_html = f"<div class='co-note'>{esc(note)}</div>" if note else ""

                    with st.container(border=True):
                        if is_restricted:
                            st.markdown(
                                f"<div class='co-name'>{esc(company)}<span class='co-tag'>Your company</span></div>{note_html}",
                                unsafe_allow_html=True,
                            )
                            # Rule check: lock slider completely if it matches the restricted company from the sheet
                            amt = st.slider(
                                label=f"Invest in {company} (Restricted)",
                                min_value=0,
                                max_value=5000,
                                step=5000,
                                value=0,
                                format="$%d",
                                key=f"slider_{company}",
                                disabled=True,
                                label_visibility="collapsed",
                            )
                        else:
                            st.markdown(
                                f"<div class='co-name'>{esc(company)}</div>{note_html}",
                                unsafe_allow_html=True,
                            )
                            amt = st.slider(
                                label=f"Invest in {company}",
                                min_value=0,
                                max_value=int(st.session_state.starting_balance),
                                step=5000,
                                value=0,
                                format="$%d",
                                key=f"slider_{company}",
                                label_visibility="collapsed",
                            )
                        allocations[company] = float(amt)
                        total_allocated += float(amt)

        remaining_balance = round(st.session_state.starting_balance - total_allocated, 2)

        # Render budget bar
        with top_metrics_container:
            if remaining_balance < 0:
                state = "over"
                message = f"You're {money(abs(remaining_balance))} over budget. Lower a slider to continue."
                is_ready = False
            elif remaining_balance > 0:
                state = "pending"
                message = f"Invest the remaining {money(remaining_balance)} to finalise."
                is_ready = False
            else:
                state = "ready"
                message = "Your full budget is allocated. You're ready to finalise."
                is_ready = True

            st.markdown(
                budget_panel(st.session_state.starting_balance, total_allocated, state, message),
                unsafe_allow_html=True,
            )

        st.write("")

        if st.button("Finalise investment", type="primary", use_container_width=True, disabled=not is_ready):
            confirm_dialog(allocations, total_allocated)
