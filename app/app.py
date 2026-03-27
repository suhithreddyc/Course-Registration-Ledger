import streamlit as st
import pandas as pd
from datetime import datetime
import contract_interface as ci
from config import ADMIN_ADDRESS
from utils import short_addr

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Course Registration Ledger",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

.stApp { background: #060612; }

.brand {
    font-size: 2.4rem; font-weight: 800; letter-spacing: -1.5px;
    background: linear-gradient(100deg, #818cf8, #38bdf8, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.brand-sub { color: #475569; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; }

.metric-card {
    background: #0d0d1f; border: 1px solid #1e1e3a; border-radius: 14px;
    padding: 1.2rem 1.4rem; text-align: center;
}
.metric-num { font-size: 2.2rem; font-weight: 800; color: #818cf8; }
.metric-lbl { font-size: 0.72rem; color: #475569; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 2px; }

.course-row {
    background: #0a0a1e; border: 1px solid #1a1a30; border-radius: 12px;
    padding: 1rem 1.3rem; margin-bottom: 0.6rem;
}
.cid { font-family: 'IBM Plex Mono', monospace; color: #818cf8; font-size: 0.82rem; font-weight: 600; }
.cname { color: #e2e8f0; font-weight: 700; font-size: 1rem; margin: 2px 0 6px 0; }
.bar-track { background: #1e1e3a; border-radius: 99px; height: 6px; width: 100%; }
.bar-fill-ok   { height: 6px; border-radius: 99px; background: linear-gradient(90deg,#34d399,#38bdf8); }
.bar-fill-warn { height: 6px; border-radius: 99px; background: linear-gradient(90deg,#fbbf24,#f59e0b); }
.bar-fill-full { height: 6px; border-radius: 99px; background: linear-gradient(90deg,#f87171,#ef4444); }
.seat-info { display:flex; justify-content:space-between; font-size:0.78rem; color:#475569; margin-top:4px; }

.tag {
    display: inline-block; padding: 2px 9px; border-radius: 99px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.5px; margin-left: 6px;
}
.tag-open   { background:#0d2a1e; color:#34d399; border:1px solid #34d39933; }
.tag-full   { background:#2a0d0d; color:#f87171; border:1px solid #f8717133; }
.tag-off    { background:#1a1a2e; color:#64748b; border:1px solid #33333366; }
.tag-you    { background:#1a1040; color:#818cf8; border:1px solid #818cf833; }
.tag-admin  { background:#2d1b00; color:#fbbf24; border:1px solid #fbbf2433; }

.msg-ok  { background:#0d2a1e; border:1px solid #34d39940; border-radius:10px; padding:.8rem 1rem; color:#34d399; margin:.5rem 0; }
.msg-err { background:#2a0d0d; border:1px solid #f8717140; border-radius:10px; padding:.8rem 1rem; color:#f87171; margin:.5rem 0; }
.msg-inf { background:#0d1a2e; border:1px solid #38bdf840; border-radius:10px; padding:.8rem 1rem; color:#38bdf8; margin:.5rem 0; }

.tx-hash { font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#475569; word-break:break-all; }

.section-title { font-size:1.3rem; font-weight:800; color:#e2e8f0; margin:1.2rem 0 0.8rem 0; }

/* Sidebar */
[data-testid="stSidebar"] { background: #08081a !important; border-right: 1px solid #1e1e3a !important; }

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #0d0d1f !important; border: 1px solid #2a2a4a !important;
    color: #e2e8f0 !important; border-radius: 8px !important; font-family: 'Syne',sans-serif !important;
}
.stSelectbox > div > div { background: #0d0d1f !important; border: 1px solid #2a2a4a !important; border-radius: 8px !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important; border: none !important; border-radius: 9px !important;
    font-weight: 700 !important; font-family: 'Syne',sans-serif !important;
    padding: 0.55rem 1.8rem !important; letter-spacing: 0.3px !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px); }

/* Tabs */
.stTabs [data-baseweb="tab"] { color: #475569 !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { color: #818cf8 !important; border-bottom-color: #818cf8 !important; }

/* Dataframe */
.stDataFrame { border: 1px solid #1e1e3a !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {"wallet":"","private_key":"","student_id":"",
              "is_admin":False,"course_count":0}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="brand">CRL</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Course Registration Ledger</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Connection status
    try:
        accounts   = ci.get_ganache_accounts()
        block_num  = ci.get_block_number()
        st.markdown(f'<div class="msg-ok">🟢 Ganache connected · Block #{block_num}</div>',
                    unsafe_allow_html=True)
    except Exception as e:
        accounts  = []
        st.markdown(f'<div class="msg-err">🔴 Ganache unreachable<br><small>{e}</small></div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Select Account")

    if accounts:
        sel_account = st.selectbox(
            "Ganache Account",
            options=accounts,
            format_func=lambda a: f"{'[ADMIN] ' if a.lower()==ADMIN_ADDRESS.lower() else ''}{a[:12]}...{a[-6:]}",
            label_visibility="collapsed",
        )
        pk_input = st.text_input("Private Key", type="password",
                                 placeholder="0x... (from Ganache key icon 🔑)",
                                 label_visibility="collapsed")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Connect", use_container_width=True):
                st.session_state.wallet      = sel_account
                st.session_state.private_key = pk_input
                st.session_state.is_admin    = (
                    sel_account.lower() == ADMIN_ADDRESS.lower()
                )
                try:
                    sid, registered, cnt = ci.get_student_info(sel_account)
                    st.session_state.student_id   = sid if registered else ""
                    st.session_state.course_count = cnt if registered else 0
                except Exception:
                    st.session_state.student_id = ""
                st.rerun()
        with col2:
            if st.button("Clear", use_container_width=True):
                for k in ["wallet","private_key","student_id","is_admin"]:
                    st.session_state[k] = "" if k != "is_admin" else False
                st.session_state.course_count = 0
                st.rerun()

    # Connected info
    if st.session_state.wallet:
        st.markdown("---")
        try:
            bal = ci.get_balance(st.session_state.wallet)
            st.markdown(f"**Balance:** `{bal:.4f} ETH`")
        except Exception:
            pass

        if st.session_state.is_admin:
            st.markdown('<span class="tag tag-admin">⚡ ADMIN</span>', unsafe_allow_html=True)
        elif st.session_state.student_id:
            st.markdown(f"**ID:** `{st.session_state.student_id}`")
            st.markdown(
                f'<span class="tag tag-open">REGISTERED</span>'
                f'<span class="tag tag-you">{st.session_state.course_count}/4 courses</span>',
                unsafe_allow_html=True
            )
        else:
            st.markdown('<span class="tag tag-full">NOT REGISTERED</span>', unsafe_allow_html=True)

    # Registration window status
    st.markdown("---")
    try:
        rw_start, rw_end, rw_open = ci.get_registration_window()
        if rw_open:
            st.markdown('<div class="msg-ok" style="font-size:0.8rem">📅 Registration: OPEN</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="msg-err" style="font-size:0.8rem">📅 Registration: CLOSED</div>',
                        unsafe_allow_html=True)
    except Exception:
        pass

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

tab_courses, tab_register, tab_enroll, tab_ledger, tab_admin = st.tabs([
    "📚  Courses",
    "🎓  Register",
    "✅  Enroll / Drop",
    "📒  Ledger",
    "🛡️  Admin",
])

# ════════════════════════════════════════════════════════
# TAB 1 – COURSES
# ════════════════════════════════════════════════════════
with tab_courses:
    st.markdown('<div class="section-title">All Courses</div>', unsafe_allow_html=True)

    try:
        courses = ci.get_all_courses()
    except Exception as e:
        st.markdown(f'<div class="msg-err">Failed to load courses: {e}</div>', unsafe_allow_html=True)
        courses = []

    if courses:
        c1,c2,c3,c4 = st.columns(4)
        stats = [
            (len(courses), "Courses"),
            (sum(c["total"] for c in courses), "Total Seats"),
            (sum(c["enrolled"] for c in courses), "Enrolled"),
            (sum(c["available"] for c in courses), "Available"),
        ]
        for col, (num, lbl) in zip([c1,c2,c3,c4], stats):
            col.markdown(
                f'<div class="metric-card"><div class="metric-num">{num}</div>'
                f'<div class="metric-lbl">{lbl}</div></div>',
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)

        for c in courses:
            pct = int((c["enrolled"] / c["total"]) * 100) if c["total"] else 0
            bar_cls = "bar-fill-full" if c["available"] == 0 else \
                      ("bar-fill-warn" if pct >= 70 else "bar-fill-ok")

            status_tag = '<span class="tag tag-full">FULL</span>'     if c["available"] == 0 else \
                         ('<span class="tag tag-off">INACTIVE</span>' if not c["active"] else \
                          '<span class="tag tag-open">OPEN</span>')

            enrolled_tag = ""
            if st.session_state.student_id:
                try:
                    if ci.is_enrolled(st.session_state.student_id, c["id"]):
                        enrolled_tag = '<span class="tag tag-you">✓ ENROLLED</span>'
                except Exception:
                    pass

            st.markdown(f"""
            <div class="course-row">
              <span class="cid">{c['id']}</span>{status_tag}{enrolled_tag}
              <div class="cname">{c['name']}</div>
              <div class="bar-track"><div class="{bar_cls}" style="width:{pct}%"></div></div>
              <div class="seat-info">
                <span>{c['available']} seats available</span>
                <span>{c['enrolled']} / {c['total']} enrolled ({pct}%)</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 2 – REGISTER STUDENT
# ════════════════════════════════════════════════════════
with tab_register:
    st.markdown('<div class="section-title">Student Registration</div>', unsafe_allow_html=True)

    if not st.session_state.wallet:
        st.markdown('<div class="msg-inf">Connect your Ganache wallet in the sidebar first.</div>',
                    unsafe_allow_html=True)
    elif st.session_state.is_admin:
        st.markdown('<div class="msg-inf">Admin accounts cannot register as students.</div>',
                    unsafe_allow_html=True)
    elif st.session_state.student_id:
        st.markdown(
            f'<div class="msg-ok">✅ Already registered as <b>{st.session_state.student_id}</b>'
            f' · Enrolled in {st.session_state.course_count}/4 courses</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div class="msg-inf">
        Each Ganache account = one student. Your Student ID is permanently recorded on-chain
        and linked to your wallet address. Choose it carefully — it cannot be changed.
        </div>
        """, unsafe_allow_html=True)

        sid_input = st.text_input("Student ID", placeholder="e.g. CS2024001",
                                  help="Unique identifier — letters & numbers only")
        if st.button("Register on Blockchain 🔗"):
            if not sid_input.strip():
                st.markdown('<div class="msg-err">Student ID cannot be empty.</div>',
                            unsafe_allow_html=True)
            elif not st.session_state.private_key:
                st.markdown('<div class="msg-err">Enter your private key in the sidebar.</div>',
                            unsafe_allow_html=True)
            else:
                try:
                    with st.spinner("Broadcasting transaction to Ganache..."):
                        receipt = ci.register_student(
                            sid_input.strip(),
                            st.session_state.wallet,
                            st.session_state.private_key,
                        )
                    st.session_state.student_id = sid_input.strip()
                    st.session_state.course_count = 0
                    tx = receipt.transactionHash.hex()
                    st.markdown(
                        f'<div class="msg-ok">✅ Registered! '
                        f'<span class="tx-hash">Tx: {tx}</span></div>',
                        unsafe_allow_html=True
                    )
                    st.rerun()
                except Exception as e:
                    err = str(e)
                    if "execution reverted" in err:
                        if "already registered" in err:
                            msg = "This wallet is already registered."
                        elif "already taken" in err:
                            msg = "That Student ID is already taken — choose another."
                        else:
                            msg = err
                    else:
                        msg = err
                    st.markdown(f'<div class="msg-err">❌ {msg}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 3 – ENROLL / DROP
# ════════════════════════════════════════════════════════
with tab_enroll:
    st.markdown('<div class="section-title">Enroll / Drop Courses</div>', unsafe_allow_html=True)

    if not st.session_state.student_id:
        st.markdown('<div class="msg-inf">Register as a student first (Register tab).</div>',
                    unsafe_allow_html=True)
    else:
        # Refresh course count
        try:
            _, _, cnt = ci.get_student_info(st.session_state.wallet)
            st.session_state.course_count = cnt
        except Exception:
            pass

        st.markdown(
            f'<div class="msg-inf">Student: <b>{st.session_state.student_id}</b> · '
            f'{st.session_state.course_count}/4 courses enrolled · '
            f'{"⚠️ Max limit reached — drop a course first" if st.session_state.course_count >= 4 else "Slots available"}'
            f'</div>',
            unsafe_allow_html=True
        )

        try:
            all_courses = ci.get_all_courses()
        except Exception as e:
            st.error(str(e))
            all_courses = []

        enroll_col, drop_col = st.columns(2)

        with enroll_col:
            st.markdown("#### ➕ Enroll in a Course")
            enrollable = [
                c for c in all_courses
                if c["active"]
                and c["available"] > 0
                and not ci.is_enrolled(st.session_state.student_id, c["id"])
            ]
            if st.session_state.course_count >= 4:
                st.markdown('<div class="msg-err">Max 4 courses reached. Drop one to enroll in another.</div>',
                            unsafe_allow_html=True)
            elif not enrollable:
                st.markdown('<div class="msg-inf">No courses available to enroll in.</div>',
                            unsafe_allow_html=True)
            else:
                opts = {f"{c['id']} – {c['name']}  [{c['available']} left]": c["id"]
                        for c in enrollable}
                choice = st.selectbox("Choose course", list(opts.keys()), key="enroll_sel")
                if st.button("Enroll Now ✅"):
                    try:
                        with st.spinner("Submitting..."):
                            receipt = ci.enroll_student(
                                opts[choice],
                                st.session_state.wallet,
                                st.session_state.private_key,
                            )
                        tx = receipt.transactionHash.hex()
                        st.markdown(
                            f'<div class="msg-ok">✅ Enrolled in <b>{opts[choice]}</b>!<br>'
                            f'<span class="tx-hash">{tx}</span></div>',
                            unsafe_allow_html=True
                        )
                        st.rerun()
                    except Exception as e:
                        err = str(e)
                        if "No seats available" in err:
                            msg = "No seats left in this course."
                        elif "Max course limit" in err:
                            msg = "You've reached the 4-course maximum."
                        elif "Registration not open" in err:
                            msg = "Registration window is not open."
                        elif "Registration closed" in err:
                            msg = "Registration period has ended."
                        else:
                            msg = err
                        st.markdown(f'<div class="msg-err">❌ {msg}</div>', unsafe_allow_html=True)

        with drop_col:
            st.markdown("#### ➖ Drop a Course")
            my_courses = [
                c for c in all_courses
                if ci.is_enrolled(st.session_state.student_id, c["id"])
            ]
            if not my_courses:
                st.markdown('<div class="msg-inf">You have no enrolled courses.</div>',
                            unsafe_allow_html=True)
            else:
                opts_drop = {f"{c['id']} – {c['name']}": c["id"] for c in my_courses}
                choice_d  = st.selectbox("Choose course to drop", list(opts_drop.keys()), key="drop_sel")
                st.markdown('<div class="msg-err" style="font-size:0.8rem">⚠️ Dropping is permanent and recorded on-chain.</div>',
                            unsafe_allow_html=True)
                if st.button("Drop Course ❌"):
                    try:
                        with st.spinner("Submitting..."):
                            receipt = ci.drop_course(
                                opts_drop[choice_d],
                                st.session_state.wallet,
                                st.session_state.private_key,
                            )
                        tx = receipt.transactionHash.hex()
                        st.markdown(
                            f'<div class="msg-ok">✅ Dropped <b>{opts_drop[choice_d]}</b>!<br>'
                            f'<span class="tx-hash">{tx}</span></div>',
                            unsafe_allow_html=True
                        )
                        st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="msg-err">❌ {e}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# TAB 4 – LEDGER
# ════════════════════════════════════════════════════════
with tab_ledger:
    st.markdown('<div class="section-title">Immutable Blockchain Ledger</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([2,2,1])
    with col_f1:
        f_action = st.selectbox("Filter Action", ["ALL","ENROLL","DROP"], key="f_action")
    with col_f2:
        f_student = st.text_input("Filter by Student ID", placeholder="leave blank for all", key="f_sid")
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔄 Refresh", key="ledger_refresh")

    try:
        ledger = ci.get_full_ledger()
    except Exception as e:
        st.markdown(f'<div class="msg-err">{e}</div>', unsafe_allow_html=True)
        ledger = []

    if f_action != "ALL":
        ledger = [e for e in ledger if e["action"] == f_action]
    if f_student.strip():
        ledger = [e for e in ledger if f_student.strip().lower() in e["student_id"].lower()]

    ledger_reversed = list(reversed(ledger))

    st.markdown(f"**{len(ledger_reversed)} transaction(s)** recorded on-chain")

    if not ledger_reversed:
        st.markdown('<div class="msg-inf">No transactions found.</div>', unsafe_allow_html=True)
    else:
        df = pd.DataFrame(ledger_reversed)[
            ["index","timestamp","student_id","course_id","action","success"]
        ]
        df.columns = ["Block #","Timestamp","Student ID","Course","Action","✓"]

        def style_action(val):
            if val == "ENROLL":
                return "color: #34d399; font-weight: 700"
            elif val == "DROP":
                return "color: #f87171; font-weight: 700"
            return ""

        styled = df.style.applymap(style_action, subset=["Action"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════
# TAB 5 – ADMIN
# ════════════════════════════════════════════════════════
with tab_admin:
    st.markdown('<div class="section-title">Admin Panel</div>', unsafe_allow_html=True)

    if not st.session_state.is_admin:
        st.markdown('<div class="msg-err">🔒 Access restricted to admin wallet only.</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="msg-inf">Connect with Account[0] from Ganache: '
            f'<code>{short_addr(ADMIN_ADDRESS)}</code></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="msg-ok">✅ Admin access granted.</div>', unsafe_allow_html=True)

        try:
            courses = ci.get_all_courses()
        except Exception as e:
            st.error(str(e))
            courses = []

        a1, a2, a3, a4 = st.tabs([
            "🔢 Update Seats",
            "🔘 Toggle Course",
            "➕ Add Course",
            "📅 Reg Window",
        ])

        with a1:
            st.markdown("#### Update Course Seat Count")
            opts = {f"{c['id']} – {c['name']}  (current: {c['total']}, enrolled: {c['enrolled']})": c
                    for c in courses}
            sel = st.selectbox("Select course", list(opts.keys()), key="a1_sel")
            selected = opts[sel]
            new_seats = st.number_input(
                "New total seats", min_value=selected["enrolled"],
                value=selected["total"], step=1
            )
            if st.button("Update Seats", key="a1_btn"):
                try:
                    with st.spinner("Updating..."):
                        ci.admin_update_seats(selected["id"], int(new_seats))
                    st.markdown('<div class="msg-ok">✅ Seats updated!</div>', unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="msg-err">❌ {e}</div>', unsafe_allow_html=True)

        with a2:
            st.markdown("#### Enable / Disable Course")
            opts2 = {f"{c['id']} – {c['name']}  ({'Active' if c['active'] else 'Inactive'})": c
                     for c in courses}
            sel2  = st.selectbox("Select course", list(opts2.keys()), key="a2_sel")
            cur   = opts2[sel2]
            state = st.radio("Set status", ["Active", "Inactive"],
                             index=0 if cur["active"] else 1, key="a2_radio")
            if st.button("Apply", key="a2_btn"):
                try:
                    with st.spinner("Updating..."):
                        ci.admin_toggle_course(cur["id"], state == "Active")
                    st.markdown('<div class="msg-ok">✅ Course status updated!</div>',
                                unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="msg-err">❌ {e}</div>', unsafe_allow_html=True)

        with a3:
            st.markdown("#### Add a New Course")
            new_id    = st.text_input("Course ID (e.g. ML)", key="a3_id")
            new_name  = st.text_input("Course Name", key="a3_name")
            new_seats = st.number_input("Total Seats", min_value=1, value=25, step=1, key="a3_seats")
            if st.button("Add Course", key="a3_btn"):
                if not new_id.strip() or not new_name.strip():
                    st.markdown('<div class="msg-err">Fill in all fields.</div>',
                                unsafe_allow_html=True)
                else:
                    try:
                        with st.spinner("Adding to blockchain..."):
                            ci.admin_add_course(new_id.strip(), new_name.strip(), int(new_seats))
                        st.markdown('<div class="msg-ok">✅ Course added!</div>',
                                    unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="msg-err">❌ {e}</div>', unsafe_allow_html=True)

        with a4:
            st.markdown("#### Set Registration Window")
            st.markdown('<div class="msg-inf">Set 0 / 0 for always-open registration.</div>',
                        unsafe_allow_html=True)
            col_s, col_e = st.columns(2)
            with col_s:
                start_dt = st.date_input("Start Date", key="a4_start")
                start_tm = st.time_input("Start Time", key="a4_stime")
            with col_e:
                end_dt   = st.date_input("End Date", key="a4_end")
                end_tm   = st.time_input("End Time", key="a4_etime")

            open_always = st.checkbox("Always open (no window restriction)", value=True)

            if st.button("Set Window", key="a4_btn"):
                try:
                    if open_always:
                        s_ts, e_ts = 0, 0
                    else:
                        s_ts = int(datetime.combine(start_dt, start_tm).timestamp())
                        e_ts = int(datetime.combine(end_dt, end_tm).timestamp())
                    with st.spinner("Updating..."):
                        ci.admin_set_window(s_ts, e_ts)
                    st.markdown('<div class="msg-ok">✅ Registration window updated!</div>',
                                unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f'<div class="msg-err">❌ {e}</div>', unsafe_allow_html=True)
