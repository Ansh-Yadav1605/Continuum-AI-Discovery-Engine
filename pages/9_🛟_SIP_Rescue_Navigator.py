"""
pages/9_🛟_SIP_Rescue_Navigator.py — Interactive SIP Rescue Navigator MVP.

Part of Continuum AI — SIP Continuation Discovery Engine.
Addresses Problem 3: Inflexible Contribution Scheduling & Cash Flow Friction During Short-Term Liquidity Crunches.

Hypothesis under test:
"When first-time SIP investors face temporary cash-flow pressure, context-aware guidance
based on their situation, SIP rules, and payment timing may help them identify and complete
an appropriate next step more successfully than a generic pause/skip interface."
"""

import streamlit as st
from datetime import date, timedelta
from core.database import init_db
from core.ui_helpers import apply_custom_styles, render_sidebar_status
from core.sip_navigator_rules import (
    evaluate_sip_guidance,
    create_comeback_plan,
    generate_ics_calendar_file,
    save_feedback_record,
    get_discovery_metrics,
    PLATFORM_RULES,
    SITUATION_OPTIONS,
    PLATFORM_OPTIONS,
    SIP_SETUP_OPTIONS,
    TIMING_OPTIONS,
    GuidanceCard
)

# 1. Page Configuration
st.set_page_config(
    page_title="SIP Rescue Navigator | MVP",
    page_icon="🛟",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
apply_custom_styles()
render_sidebar_status()

# 2. Session State Initialization
if "nav_step" not in st.session_state:
    st.session_state.nav_step = 1  # 1: Welcome, 2: Situation, 3: Timing & Setup, 4: Guidance, 5: Comeback, 6: Feedback
if "selected_situation" not in st.session_state:
    st.session_state.selected_situation = SITUATION_OPTIONS[0]
if "selected_platform" not in st.session_state:
    st.session_state.selected_platform = PLATFORM_OPTIONS[0]
if "selected_setup" not in st.session_state:
    st.session_state.selected_setup = SIP_SETUP_OPTIONS[0]
if "selected_timing" not in st.session_state:
    st.session_state.selected_timing = TIMING_OPTIONS[2]
if "comeback_created" not in st.session_state:
    st.session_state.comeback_created = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False


def reset_journey():
    st.session_state.nav_step = 1
    st.session_state.comeback_created = None
    st.session_state.feedback_submitted = False


# Quick scenario presets for assessors
PRESETS = {
    "1. Groww — Medical Emergency T-1 Day (Cutoff Passed)": {
        "situation": "My next SIP debit is approaching, and I may not have enough money.",
        "platform": "Groww",
        "setup": "Platform-managed SIP",
        "timing": "Within 1–2 days"
    },
    "2. Groww — Temporary Break with Buffer (T-4 Days)": {
        "situation": "I need a temporary break from my SIP.",
        "platform": "Groww",
        "setup": "Platform-managed SIP",
        "timing": "Within 3–5 days"
    },
    "3. Zerodha Coin — Payment Failed (Diagnostics)": {
        "situation": "My SIP payment failed.",
        "platform": "Zerodha Coin",
        "setup": "Platform-managed SIP",
        "timing": "Today"
    },
    "4. Affordability Strain — Step Down Contribution": {
        "situation": "My current SIP amount is becoming difficult to afford.",
        "platform": "Groww",
        "setup": "Platform-managed SIP",
        "timing": "More than 5 days"
    },
    "5. Stopping Completely — Reassurance & Unit Safety": {
        "situation": "I want to stop my SIP completely.",
        "platform": "Groww",
        "setup": "Platform-managed SIP",
        "timing": "More than 5 days"
    },
    "6. AMC-Registered SIP — Long 10-15 Day Notice Cutoff": {
        "situation": "I need a temporary break from my SIP.",
        "platform": "Groww",
        "setup": "AMC-registered SIP",
        "timing": "Within 3–5 days"
    },
    "7. Unknown Platform / Date — General Fallback Guidance": {
        "situation": "I'm not sure what my options are.",
        "platform": "Another platform",
        "setup": "I'm not sure",
        "timing": "I'm not sure of the date"
    }
}

# 3. Header & Navigation Hero
st.markdown(
    """
    <div class="hero-header" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.12) 100%); border-color: rgba(16, 185, 129, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
            <div>
                <span class="badge" style="background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4);">
                    Interactive Prototype &bull; Discovery MVP
                </span>
                <div class="hero-title" style="margin-top: 6px;">🛟 SIP Rescue Navigator</div>
                <p class="hero-subtitle">
                    Context-aware guidance for first-time mutual fund investors facing temporary cash-flow pressure.
                </p>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.78rem; color: #94A3B8; background: rgba(255,255,255,0.06); padding: 4px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    Testing Problem 3 Hypothesis
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# 4. Assessor Quick Preset Loader
with st.expander("⚡ Assessor & Evaluator Quick Test Presets (Load 1-Click Scenarios)", expanded=False):
    st.caption("Select a pre-configured investor scenario to immediately inspect deterministic rule evaluation:")
    pcol1, pcol2 = st.columns([3, 1])
    with pcol1:
        chosen_preset = st.selectbox("Choose a test scenario:", list(PRESETS.keys()), label_visibility="collapsed")
    with pcol2:
        if st.button("Apply Preset & View Guidance", type="secondary", use_container_width=True):
            p_data = PRESETS[chosen_preset]
            st.session_state.selected_situation = p_data["situation"]
            st.session_state.selected_platform = p_data["platform"]
            st.session_state.selected_setup = p_data["setup"]
            st.session_state.selected_timing = p_data["timing"]
            st.session_state.nav_step = 4
            st.rerun()

# 5. Progress Stepper Bar
step_labels = [
    ("1. Welcome", 1),
    ("2. Situation", 2),
    ("3. Timing & Setup", 3),
    ("4. Guidance", 4),
    ("5. Comeback Plan", 5),
    ("6. Usability Test", 6)
]

cols = st.columns(6)
for idx, (label, s_num) in enumerate(step_labels):
    with cols[idx]:
        if st.session_state.nav_step == s_num:
            st.markdown(f"<div style='border-bottom: 3px solid #10B981; color: #FFFFFF; font-weight: 700; font-size: 0.84rem; padding-bottom: 6px; text-align: center;'>{label}</div>", unsafe_allow_html=True)
        elif st.session_state.nav_step > s_num:
            st.markdown(f"<div style='border-bottom: 3px solid rgba(16, 185, 129, 0.4); color: #34D399; font-size: 0.84rem; padding-bottom: 6px; text-align: center;'>✓ {label.split(' ')[1]}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='border-bottom: 3px solid rgba(255,255,255,0.1); color: #64748B; font-size: 0.84rem; padding-bottom: 6px; text-align: center;'>{label}</div>", unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 1: Welcome & Context
# ---------------------------------------------------------------------------
if st.session_state.nav_step == 1:
    st.markdown(
        """
        <div class="glass-card" style="padding: 32px 28px; max-width: 820px; margin: 0 auto;">
            <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-bottom: 12px;">
                SIP Rescue Navigator
            </div>
            <p style="color: #E2E8F0; font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">
                Unexpected expenses can make a scheduled investment difficult to manage.
                Let's understand your situation and explore the options that may be available.
            </p>
            <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3B82F6; padding: 14px 18px; border-radius: 8px; margin-bottom: 28px;">
                <div style="font-size: 0.88rem; color: #93C5FD; font-weight: 600; margin-bottom: 4px;">
                    🛡️ Informational Discovery Prototype Disclosure
                </div>
                <div style="font-size: 0.84rem; color: #CBD5E1; line-height: 1.5;">
                    This tool is an educational research prototype. It does not connect to your live investment account,
                    does not access your bank, and never collects sensitive credentials (no PAN, bank accounts, or passwords).
                    Guidance is evaluated using verified, published platform rules.
                </div>
            </div>
            <div style="display: flex; gap: 16px; align-items: center;">
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("🚀 Find my next step", type="primary", use_container_width=True, key="btn_start_wizard"):
            st.session_state.nav_step = 2
            st.rerun()

# ---------------------------------------------------------------------------
# SCREEN 2: Understand the Situation
# ---------------------------------------------------------------------------
elif st.session_state.nav_step == 2:
    st.markdown(
        """
        <div style="max-width: 820px; margin: 0 auto;">
            <h2 style="color: #FFFFFF; font-size: 1.45rem; margin-bottom: 6px;">What are you trying to manage today?</h2>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 20px;">
                Choose the option that closest matches what you are experiencing. There is zero judgment here—managing personal cash flow is part of responsible financial management.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div style='max-width: 820px; margin: 0 auto;'>", unsafe_allow_html=True)
        chosen_situation = st.radio(
            "Select your current situation:",
            SITUATION_OPTIONS,
            index=SITUATION_OPTIONS.index(st.session_state.selected_situation) if st.session_state.selected_situation in SITUATION_OPTIONS else 0,
            label_visibility="collapsed"
        )
        st.session_state.selected_situation = chosen_situation

        st.markdown("<br/>", unsafe_allow_html=True)
        col_back, col_next = st.columns([1, 1])
        with col_back:
            if st.button("← Back to Welcome", use_container_width=True):
                st.session_state.nav_step = 1
                st.rerun()
        with col_next:
            if st.button("Continue to Timing & Setup →", type="primary", use_container_width=True):
                st.session_state.nav_step = 3
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 3: Understand Timing & SIP Setup
# ---------------------------------------------------------------------------
elif st.session_state.nav_step == 3:
    st.markdown(
        """
        <div style="max-width: 820px; margin: 0 auto;">
            <h2 style="color: #FFFFFF; font-size: 1.45rem; margin-bottom: 6px;">Understand Timing and SIP Setup</h2>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 20px;">
                Different platforms and SIP setups have different advance cutoff windows. We use these general inputs to check what rules apply.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div style='max-width: 820px; margin: 0 auto;'>", unsafe_allow_html=True)
        
        q1_col, q2_col = st.columns(2)
        with q1_col:
            st.markdown("##### 📱 Investment Platform")
            platform_choice = st.selectbox(
                "Platform:",
                PLATFORM_OPTIONS,
                index=PLATFORM_OPTIONS.index(st.session_state.selected_platform) if st.session_state.selected_platform in PLATFORM_OPTIONS else 0,
                label_visibility="collapsed"
            )
            st.session_state.selected_platform = platform_choice
            st.caption("E.g. Groww, Zerodha Coin, or another app.")

        with q2_col:
            st.markdown("##### ⚙️ SIP Setup Type")
            setup_choice = st.selectbox(
                "Setup Type:",
                SIP_SETUP_OPTIONS,
                index=SIP_SETUP_OPTIONS.index(st.session_state.selected_setup) if st.session_state.selected_setup in SIP_SETUP_OPTIONS else 0,
                label_visibility="collapsed"
            )
            st.session_state.selected_setup = setup_choice
            st.caption("Platform-managed (AutoPay/e-Mandate) vs Direct AMC mandate.")

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### ⏳ Time Remaining Until Next Scheduled Debit")
        timing_choice = st.selectbox(
            "Approximate time remaining:",
            TIMING_OPTIONS,
            index=TIMING_OPTIONS.index(st.session_state.selected_timing) if st.session_state.selected_timing in TIMING_OPTIONS else 2,
            label_visibility="collapsed"
        )
        st.session_state.selected_timing = timing_choice
        st.caption("Platforms enforce strict cutoffs (typically 2 business days for apps, 10–21 days for direct AMCs).")

        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 12px 16px; margin: 20px 0;">
                <span style="font-size: 0.82rem; color: #94A3B8;">
                    🔒 <strong>Privacy Check:</strong> We do NOT ask for folio numbers, bank account numbers, PAN, or account balances. These selections are purely prototype scenarios.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        col_back, col_next = st.columns([1, 1])
        with col_back:
            if st.button("← Back to Situation", use_container_width=True):
                st.session_state.nav_step = 2
                st.rerun()
        with col_next:
            if st.button("Generate My Next-Step Guidance →", type="primary", use_container_width=True):
                st.session_state.nav_step = 4
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 4: Your Next-Step Guidance (Core Experience)
# ---------------------------------------------------------------------------
elif st.session_state.nav_step == 4:
    card: GuidanceCard = evaluate_sip_guidance(
        situation=st.session_state.selected_situation,
        platform=st.session_state.selected_platform,
        setup_type=st.session_state.selected_setup,
        time_remaining=st.session_state.selected_timing
    )

    st.markdown(
        """
        <div style="max-width: 860px; margin: 0 auto 16px auto; display: flex; justify-content: space-between; align-items: center;">
            <h2 style="color: #FFFFFF; font-size: 1.45rem; margin: 0;">🧭 Your Next-Step Guidance</h2>
            <span style="font-size: 0.82rem; color: #94A3B8;">Context-Aware Rule Synthesis</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Main Guidance Card
    with st.container():
        st.markdown("<div style='max-width: 860px; margin: 0 auto;'>", unsafe_allow_html=True)

        # Cutoff status alert header
        badge_color = "#EF4444" if "CRITICAL" in card.cutoff_status else "#F59E0B" if "URGENT" in card.cutoff_status else "#10B981" if "SAFE" in card.cutoff_status else "#64748B"
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 5px solid {badge_color}; padding: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF;">
                        {card.headline}
                    </div>
                    <span style="background: {badge_color}25; color: {badge_color}; border: 1px solid {badge_color}50; font-size: 0.78rem; font-weight: 700; padding: 4px 10px; border-radius: 9999px;">
                        {card.cutoff_warning_badge}
                    </span>
                </div>
                
                <!-- 1. What your situation means -->
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 0.84rem; text-transform: uppercase; color: #94A3B8; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">
                        1. What your situation means
                    </div>
                    <div style="font-size: 0.95rem; color: #E2E8F0; line-height: 1.55;">
                        {card.situation_meaning}
                    </div>
                </div>

                <!-- 2. What to check now -->
                <div style="margin-bottom: 18px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 14px 16px;">
                    <div style="font-size: 0.84rem; text-transform: uppercase; color: #38BDF8; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">
                        2. What to check now
                    </div>
                    <div style="font-size: 0.92rem; color: #F1F5F9; line-height: 1.5;">
                        {card.what_to_check_now}
                    </div>
                </div>

                <!-- 3. Timing and eligibility -->
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 0.84rem; text-transform: uppercase; color: #F59E0B; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">
                        3. Timing and eligibility for upcoming instalment
                    </div>
                    <div style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.5;">
                        {card.timing_eligibility}
                    </div>
                </div>

                <!-- 4. Available Options -->
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 0.84rem; text-transform: uppercase; color: #34D399; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px;">
                        4. Available options supported for this setup
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px;">
                        {''.join([f'''
                            <div style="background: rgba(16, 185, 129, 0.06); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 12px;">
                                <div style="font-weight: 700; color: #FFFFFF; font-size: 0.88rem; margin-bottom: 3px;">{opt["name"]}</div>
                                <div style="color: #94A3B8; font-size: 0.8rem; line-height: 1.4;">{opt["desc"]}</div>
                            </div>
                        ''' for opt in card.available_options])}
                    </div>
                </div>

                <!-- 5. Limitations -->
                <div style="margin-bottom: 18px;">
                    <div style="font-size: 0.84rem; text-transform: uppercase; color: #94A3B8; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 4px;">
                        5. Limitations of this guidance
                    </div>
                    <ul style="margin: 0; padding-left: 20px; color: #94A3B8; font-size: 0.82rem; line-height: 1.5;">
                        {''.join([f"<li>{lim}</li>" for lim in card.limitations])}
                    </ul>
                </div>

                <!-- 6. Source and Verification Status -->
                <div style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 0.78rem; color: #64748B;">Official Source:</span>
                        <a href="{card.primary_action_url or '#'}" target="_blank" style="color: #38BDF8; font-size: 0.8rem; text-decoration: underline; margin-left: 4px;">
                            {card.applicable_rule.official_source_name} ↗
                        </a>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="font-size: 0.76rem; color: #64748B;">Verified: {card.last_verified_date}</span>
                        <span class="badge" style="background: rgba(16,185,129,0.15); color: #34D399; font-size: 0.7rem;">
                            {card.verification_status}
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 7. Next Actions Bar
        st.markdown("##### 🚀 What would you like to do next?")
        act_col1, act_col2, act_col3 = st.columns([1, 1, 1])

        with act_col1:
            if card.primary_action_url:
                st.link_button(f"🔗 Open {card.applicable_rule.platform} Help", card.primary_action_url, use_container_width=True)
            else:
                st.button("🔗 Platform Help (Unavailable)", disabled=True, use_container_width=True)

        with act_col2:
            if st.button("📅 Create Comeback Reminder", type="primary", use_container_width=True):
                st.session_state.nav_step = 5
                st.rerun()

        with act_col3:
            if st.button("🔄 Change My Answers", use_container_width=True):
                st.session_state.nav_step = 2
                st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)
        with st.expander("🔍 View Complete Raw Rule Specification", expanded=False):
            st.json({
                "rule_id": card.applicable_rule.rule_id,
                "platform": card.applicable_rule.platform,
                "setup_type": card.applicable_rule.setup_type,
                "action_type": card.applicable_rule.action_type,
                "min_notice_days": card.applicable_rule.min_notice_days,
                "notice_cutoff_description": card.applicable_rule.notice_cutoff_description,
                "eligibility_conditions": card.applicable_rule.eligibility_conditions,
                "effective_date_implication": card.applicable_rule.effective_date_implication,
                "official_source_url": card.applicable_rule.official_source_url,
                "last_verified_date": card.applicable_rule.last_verified_date,
                "verification_status": card.applicable_rule.verification_status
            })

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 5: SIP Comeback Plan
# ---------------------------------------------------------------------------
elif st.session_state.nav_step == 5:
    st.markdown(
        """
        <div style="max-width: 820px; margin: 0 auto;">
            <h2 style="color: #FFFFFF; font-size: 1.45rem; margin-bottom: 6px;">📅 SIP Comeback Plan</h2>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 20px;">
                Temporary breaks are healthy when cash is tight. Set an optional, zero-pressure reminder to review your financial situation later.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div style='max-width: 820px; margin: 0 auto;'>", unsafe_allow_html=True)

        st.markdown("##### When would you like to review your SIP plan?")
        review_horizon = st.radio(
            "Select review timeline:",
            [
                "15 Days — Quick check-in after immediate expenses clear",
                "30 Days — Standard 1-cycle review next month",
                "60 Days — Extended 2-month buffer to rebuild savings",
                "Custom Date"
            ],
            index=1,
            label_visibility="collapsed"
        )

        offset_days = 30
        if "15 Days" in review_horizon:
            offset_days = 15
        elif "60 Days" in review_horizon:
            offset_days = 60
        elif "Custom Date" in review_horizon:
            custom_target = st.date_input("Select custom date:", min_value=date.today() + timedelta(days=1), value=date.today() + timedelta(days=45))
            offset_days = (custom_target - date.today()).days

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### What action do you want to revisit?")
        focus_action = st.selectbox(
            "Focus action for reminder:",
            [
                "Review monthly budget and decide whether to resume SIP",
                "Check if salary credit date matches my SIP debit schedule",
                "Consider stepping down to ₹100 or ₹500 scheme minimum",
                "Decide whether to extend pause or cancel mandate"
            ]
        )

        custom_notes = st.text_input(
            "Optional reminder note for yourself:",
            placeholder="E.g., Medical bills paid off; check emergency fund balance."
        )

        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.08); border-left: 4px solid #F59E0B; padding: 12px 16px; border-radius: 6px; margin: 16px 0;">
                <div style="font-size: 0.82rem; color: #FCD34D; font-weight: 600;">
                    ℹ️ Prototype Reminder Simulation Notice
                </div>
                <div style="font-size: 0.8rem; color: #CBD5E1;">
                    In this prototype, reminders are stored in your local session. To add this reminder to your actual device calendar,
                    click <strong>'Download Calendar Event (.ics)'</strong> below. We do not send automated WhatsApp or email messages.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("💾 Set My Comeback Reminder", type="primary", use_container_width=True):
            reminder = create_comeback_plan(offset_days, focus_action, custom_notes)
            st.session_state.comeback_created = reminder
            st.success(f"✅ Reminder scheduled for {reminder.target_date} ({reminder.days_from_now} days from now)!")

        if st.session_state.comeback_created:
            rem = st.session_state.comeback_created
            ics_data = generate_ics_calendar_file(rem)

            st.markdown(
                f"""
                <div class="glass-card" style="margin-top: 16px; border-color: rgba(16, 185, 129, 0.3);">
                    <div style="color: #34D399; font-weight: 700; font-size: 0.95rem; margin-bottom: 6px;">
                        📌 Reminder Active: Review on {rem.target_date}
                    </div>
                    <div style="color: #FFFFFF; font-size: 0.88rem; font-weight: 600;">{rem.focus_action}</div>
                    <p style="color: #94A3B8; font-size: 0.82rem; margin-top: 4px;">{rem.reflection_prompt}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.download_button(
                    label="📥 Download Calendar Event (.ics)",
                    data=ics_data,
                    file_name=f"sip_comeback_{rem.target_date}.ics",
                    mime="text/calendar",
                    use_container_width=True
                )
            with dcol2:
                if st.button("Continue to Feedback →", type="primary", use_container_width=True):
                    st.session_state.nav_step = 6
                    st.rerun()

        st.markdown("<br/>", unsafe_allow_html=True)
        col_back, col_skip = st.columns([1, 1])
        with col_back:
            if st.button("← Back to Guidance", use_container_width=True):
                st.session_state.nav_step = 4
                st.rerun()
        with col_skip:
            if not st.session_state.comeback_created:
                if st.button("Skip Reminder & Give Feedback →", use_container_width=True):
                    st.session_state.nav_step = 6
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SCREEN 6: Feedback & Usability Testing Panel (Hypothesis Test)
# ---------------------------------------------------------------------------
elif st.session_state.nav_step == 6:
    st.markdown(
        """
        <div style="max-width: 860px; margin: 0 auto;">
            <h2 style="color: #FFFFFF; font-size: 1.45rem; margin-bottom: 6px;">🧪 Prototype Usability & Hypothesis Validation</h2>
            <p style="color: #94A3B8; font-size: 0.92rem; margin-bottom: 20px;">
                Help us evaluate our core discovery hypothesis: Does context-aware guidance reduce uncertainty compared to a generic pause button?
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.container():
        st.markdown("<div style='max-width: 860px; margin: 0 auto;'>", unsafe_allow_html=True)

        if not st.session_state.feedback_submitted:
            with st.form("feedback_form"):
                st.markdown("##### 1. Did this guidance help you understand your next step?")
                clarity_response = st.radio(
                    "Clarity response:",
                    [
                        "Yes, I know what to do next.",
                        "Partly, I still have questions.",
                        "No, I couldn't find a useful option."
                    ],
                    label_visibility="collapsed"
                )

                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown("##### 2. What was most useful? (Optional)")
                useful_text = st.text_area(
                    "Feedback comment:",
                    placeholder="E.g., The explanation that missing 1 payment does not cancel my SIP or ruin my credit score gave me peace of mind.",
                    label_visibility="collapsed"
                )

                st.markdown("<br/>", unsafe_allow_html=True)
                st.markdown("##### 3. Diagnostic Comprehension Checks")
                c_check1, c_check2 = st.columns(2)
                with c_check1:
                    understood_deadline = st.checkbox("I clearly understand my platform's cutoff deadline.", value=True)
                with c_check2:
                    identified_action = st.checkbox("I identified an appropriate action to take.", value=True)

                st.markdown(
                    """
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 10px;">
                        🔒 All responses are anonymous and stored locally for usability research. No personal or financial identifiers are recorded.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                submitted = st.form_submit_button("Submit Discovery Feedback", type="primary", use_container_width=True)
                if submitted:
                    record = {
                        "situation": st.session_state.selected_situation,
                        "platform": st.session_state.selected_platform,
                        "setup_type": st.session_state.selected_setup,
                        "time_remaining": st.session_state.selected_timing,
                        "clarity_response": clarity_response,
                        "useful_feedback": useful_text,
                        "understood_deadline": understood_deadline,
                        "identified_action": identified_action,
                        "reminder_opt_in": st.session_state.comeback_created is not None
                    }
                    save_feedback_record(record)
                    st.session_state.feedback_submitted = True
                    st.success("Thank you! Your feedback has been recorded in the usability research log.")
                    st.rerun()

        else:
            st.success("✅ Your feedback has been logged in the research dataset.")

        # ---------------------------------------------------------------------------
        # Section 9: Live Prototype Usability Metrics Panel
        # ---------------------------------------------------------------------------
        st.markdown("---")
        st.markdown("### 📊 Documented Usability Measurement Plan & Live Results")
        st.caption("Heuristic usability metrics computed from recorded discovery testing sessions. (Not fabricated churn reduction metrics).")

        metrics = get_discovery_metrics()

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        with mcol1:
            st.metric(
                label="Guidance Clarity Rate",
                value=f"{metrics['clarity_rate']}%",
                help=f"Numerator: {metrics['clarity_numerator']} 'Yes, I know what to do next' / Denominator: {metrics['clarity_denominator']} total responses"
            )
            st.caption(f"**{metrics['clarity_numerator']} / {metrics['clarity_denominator']}** sessions")

        with mcol2:
            st.metric(
                label="Deadline Comprehension",
                value=f"{metrics['deadline_understanding_rate']}%",
                help=f"Numerator: {metrics['deadline_numerator']} understood cutoff / Denominator: {metrics['deadline_denominator']} total responses"
            )
            st.caption(f"**{metrics['deadline_numerator']} / {metrics['deadline_denominator']}** sessions")

        with mcol3:
            st.metric(
                label="Action Identified",
                value=f"{metrics['action_identification_rate']}%",
                help=f"Numerator: {metrics['action_numerator']} identified practical action / Denominator: {metrics['action_denominator']} total responses"
            )
            st.caption(f"**{metrics['action_numerator']} / {metrics['action_denominator']}** sessions")

        with mcol4:
            st.metric(
                label="Comeback Opt-In Rate",
                value=f"{metrics['reminder_opt_in_rate']}%",
                help=f"Numerator: {metrics['reminder_numerator']} scheduled reminder / Denominator: {metrics['reminder_denominator']} total responses"
            )
            st.caption(f"**{metrics['reminder_numerator']} / {metrics['reminder_denominator']}** sessions")

        st.markdown("<br/>", unsafe_allow_html=True)

        with st.expander("📐 Measurement Plan: Metric Formulas, Numerators & Denominators", expanded=True):
            st.markdown(
                """
                | Metric | Formula (Numerator / Denominator) | Purpose in Testing | What It Proves vs Disproves |
                | :--- | :--- | :--- | :--- |
                | **Guidance Task-Completion Rate** | `Sessions reaching Screen 4 / Sessions starting Screen 1` | Measures usability and funnel drop-off | Validates whether the 3-question flow is lightweight enough for stressed users. |
                | **Timing Rule Comprehension** | `Sessions confirming deadline understood / Total completed sessions` | Tests whether cutoff warnings prevent false expectations | Validates if users understand that sub-2-day requests cannot stop an upcoming debit. |
                | **Action Identification Rate** | `Users selecting a clear next step / Total completed sessions` | Measures actionability over passive reading | Proves users found an applicable alternative (skip, pause, step-down, or retry). |
                | **User-Reported Clarity** | `Positive clarity responses ("Yes") / Total feedback respondents` | Direct qualitative signal of cognitive relief | Validates hypothesis that context-aware guidance reduces friction. |
                | **Clarification Needed Rate** | `Responses indicating "Partly" or "No" / Total feedback respondents` | Identifies gaps in guidance rules | Highlights platforms or edge cases needing clearer explanations. |
                | **Reminder Opt-In Rate** | `Users creating Comeback Plan / Total guidance viewers` | Measures appetite for non-presumptive check-in | Discovers whether investors value delayed self-reflection vs immediate exit. |
                """
            )
            st.warning(
                "⚠️ **Research Boundary Notice:** Real-world 90-day SIP resumption, missed-instalment recovery rates, "
                "and churn reduction cannot be validated using an isolated prototype. Real validation requires integrating "
                "with live broker telemetry, conducting controlled A/B experiments against a generic pause button, "
                "and tracking longitudinal debit outcomes over 3–6 months."
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        rcol1, rcol2 = st.columns([1, 1])
        with rcol1:
            if st.button("🔄 Start New Guidance Session", type="primary", use_container_width=True):
                reset_journey()
                st.rerun()
        with rcol2:
            st.page_link("pages/5_Problem_Statements.py", label="← Return to Problem Statements", icon="🎯", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
