import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, date
import time
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION & CSS (Animations & Styling)
# ==========================================
st.set_page_config(page_title="Habit Tracker by Najam", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
    .stApp { background: #070a13; color: #f3f4f6; }
    .animated-title { font-family: 'Poppins', sans-serif; font-weight: 900; background: linear-gradient(135deg, #c084fc 0%, #f97316 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; text-align: center; margin-bottom: 20px;}
    .metric-card { background: rgba(17, 24, 39, 0.7); border-radius: 16px; padding: 20px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    div.stButton > button { width: 100%; border-radius: 12px; background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important; color: white !important; font-weight: bold; border: none; padding: 10px; transition: 0.3s;}
    div.stButton > button:hover { transform: scale(1.02); opacity: 0.9; }
    .header-style { color: #c084fc; border-bottom: 2px solid #374151; padding-bottom: 10px; }
</style>""", unsafe_allow_html=True)

# ==========================================
# 2. GOOGLE SHEETS CONNECTION & HELPER FUNCTIONS
# ==========================================
# ttl=0 lagaya hai taake data hamesha fresh aaye, purana save na dikhaye
conn = st.connection("gsheets", type=GSheetsConnection)

def get_sheet(sheet_name):
    """Google Sheet se fresh data parhna"""
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df.empty or len(df.columns) == 0:
            return pd.DataFrame()
        return df.dropna(how='all')
    except Exception as e:
        st.error(f"Error reading {sheet_name}: {e}")
        return pd.DataFrame()

def update_sheet(sheet_name, df):
    """Google Sheet mein data save karna"""
    conn.update(worksheet=sheet_name, data=df)

# Session State Initialization
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""

# ==========================================
# 3. AUTHENTICATION (LOG IN / SIGN UP)
# ==========================================
if not st.session_state["logged_in"]:
    st.markdown("<h1 class='animated-title'>⚡ Habit Tracker by Najam</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Apni aadaat ko behtar banayein aur fitness goals hasil karein.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auth_mode = st.tabs(["Log In 🔑", "Sign Up 🚀"])
        
        # --- LOGIN ---
        with auth_mode[0]:
            login_user = st.text_input("Username", key="login_u")
            login_pass = st.text_input("Password", type="password", key="login_p")
            
            if st.button("Log In"):
                if login_user and login_pass:
                    users_df = get_sheet("users")
                    if not users_df.empty:
                        user_match = users_df[(users_df["username"] == login_user) & (users_df["password"] == login_pass)]
                        if not user_match.empty:
                            st.session_state["logged_in"] = True
                            st.session_state["username"] = login_user
                            st.session_state["user_data"] = user_match.iloc[0].to_dict()
                            st.rerun()
                        else:
                            st.error("Username ya Password ghalat hai.")
                    else:
                        st.error("Database khali hai. Pehle Sign Up karein.")
                else:
                    st.warning("Please username aur password likhein.")

        # --- SIGN UP ---
        with auth_mode[1]:
            new_user = st.text_input("New Username", key="reg_u")
            new_pass = st.text_input("New Password", type="password", key="reg_p")
            col_a, col_b = st.columns(2)
            age = col_a.number_input("Age", 10, 100, 20)
            gender = col_b.selectbox("Gender", ["Male", "Female", "Other"])
            height = col_a.number_input("Height (cm)", 50.0, 250.0, 170.0)
            weight = col_b.number_input("Weight (kg)", 20.0, 300.0, 70.0)
            goal = st.selectbox("Fitness Goal", ["Fat Loss", "Muscle Gain", "Fitness Maintenance"])
            
            if st.button("Create Account"):
                users_df = get_sheet("users")
                if users_df.empty:
                    users_df = pd.DataFrame(columns=["username", "password", "age", "gender", "height", "weight", "goal"])
                
                if new_user in users_df["username"].values:
                    st.error("Ye username pehle se majood hai!")
                elif new_user and new_pass:
                    new_row = pd.DataFrame([{"username": new_user, "password": new_pass, "age": age, "gender": gender, "height": height, "weight": weight, "goal": goal}])
                    update_sheet("users", pd.concat([users_df, new_row], ignore_index=True))
                    st.success("🎉 Account ban gaya! Ab Log In karein.")
                else:
                    st.warning("Details mukammal karein.")

# ==========================================
# 4. MAIN APPLICATION (LOGGED IN)
# ==========================================
else:
    username = st.session_state["username"]
    user_info = st.session_state.get("user_data", {})
    today_str = str(date.today())

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"Hi, {username} 👋")
        st.info(f"**Goal:** {user_info.get('goal', 'N/A')}")
        st.markdown("---")
        if st.button("Log Out 🛑"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

    # --- TABS (Sab features yahan hain) ---
    tab_dash, tab_habits, tab_diet, tab_weight, tab_settings = st.tabs([
        "🌌 Dashboard", "📝 Checklist & Water", "🥗 Diet & Workout", "⚖️ Biometrics", "⚙️ Settings"
    ])

    # ================= 1. DASHBOARD =================
    with tab_dash:
        st.markdown(f"<h2 class='header-style'>Welcome to your Dashboard!</h2>", unsafe_allow_html=True)
        
        # Metrics Cards
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><h3>Current Weight</h3><h2>{user_info.get('weight', 0)} kg</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><h3>Height</h3><h2>{user_info.get('height', 0)} cm</h2></div>", unsafe_allow_html=True)
        # BMI Calculation
        h_m = float(user_info.get('height', 170)) / 100
        w_kg = float(user_info.get('weight', 70))
        bmi = round(w_kg / (h_m ** 2), 1) if h_m > 0 else 0
        c3.markdown(f"<div class='metric-card'><h3>BMI</h3><h2>{bmi}</h2></div>", unsafe_allow_html=True)

    # ================= 2. HABITS & WATER =================
    with tab_habits:
        st.markdown(f"<h2 class='header-style'>Daily Habits & Water Tracker</h2>", unsafe_allow_html=True)
        
        col_habits, col_water = st.columns([2, 1])
        
        with col_habits:
            st.subheader("📝 Habits Checklist")
            new_habit = st.text_input("Nayi Habit shamil karein:")
            if st.button("Add Habit ➕"):
                if new_habit:
                    habits_df = get_sheet("habits")
                    if habits_df.empty: habits_df = pd.DataFrame(columns=["username", "habit_name"])
                    new_h_row = pd.DataFrame([{"username": username, "habit_name": new_habit}])
                    update_sheet("habits", pd.concat([habits_df, new_h_row], ignore_index=True))
                    st.success(f"'{new_habit}' shamil ho gayi!")
                    st.rerun()

            st.markdown("---")
            habits_df = get_sheet("habits")
            logs_df = get_sheet("habit_logs")
            if logs_df.empty: logs_df = pd.DataFrame(columns=["username", "habit_name", "date", "status"])

            if not habits_df.empty:
                user_habits = habits_df[habits_df["username"] == username]["habit_name"].tolist()
                for h in user_habits:
                    is_done = False
                    if not logs_df.empty:
                        done_check = logs_df[(logs_df["username"] == username) & (logs_df["habit_name"] == h) & (logs_df["date"] == today_str) & (logs_df["status"] == "Done")]
                        is_done = not done_check.empty
                    
                    checked = st.checkbox(h, value=is_done, key=f"habit_{h}")
                    if checked != is_done:
                        new_status = "Done" if checked else "Pending"
                        logs_df = logs_df[~((logs_df["username"] == username) & (logs_df["habit_name"] == h) & (logs_df["date"] == today_str))]
                        new_log = pd.DataFrame([{"username": username, "habit_name": h, "date": today_str, "status": new_status}])
                        update_sheet("habit_logs", pd.concat([logs_df, new_log], ignore_index=True))
                        st.rerun()
            else:
                st.info("Koi habit add nahi ki.")

        with col_water:
            st.subheader("💧 Water Tracker")
            # Using habit_logs to save water glasses
            water_habit_name = "Water_Glasses_Count"
            water_count = 0
            if not logs_df.empty:
                w_logs = logs_df[(logs_df["username"] == username) & (logs_df["habit_name"] == water_habit_name) & (logs_df["date"] == today_str)]
                if not w_logs.empty:
                    try: water_count = int(w_logs.iloc[0]["status"]) 
                    except: water_count = 0
            
            st.markdown(f"<h1 style='text-align: center; color: #3b82f6;'>{water_count} / 8+</h1>", unsafe_allow_html=True)
            st.write("Glasses drank today")
            
            c_add, c_sub = st.columns(2)
            if c_add.button("➕ Add Glass"):
                new_w = water_count + 1
                logs_df = logs_df[~((logs_df["username"] == username) & (logs_df["habit_name"] == water_habit_name) & (logs_df["date"] == today_str))]
                new_log = pd.DataFrame([{"username": username, "habit_name": water_habit_name, "date": today_str, "status": str(new_w)}])
                update_sheet("habit_logs", pd.concat([logs_df, new_log], ignore_index=True))
                st.rerun()
            if c_sub.button("➖ Remove Glass") and water_count > 0:
                new_w = water_count - 1
                logs_df = logs_df[~((logs_df["username"] == username) & (logs_df["habit_name"] == water_habit_name) & (logs_df["date"] == today_str))]
                new_log = pd.DataFrame([{"username": username, "habit_name": water_habit_name, "date": today_str, "status": str(new_w)}])
                update_sheet("habit_logs", pd.concat([logs_df, new_log], ignore_index=True))
                st.rerun()

    # ================= 3. DIET & WORKOUT =================
    with tab_diet:
        st.markdown(f"<h2 class='header-style'>Diet & Workout Logger</h2>", unsafe_allow_html=True)
        dw_df = get_sheet("diet_workout_logs")
        if dw_df.empty: dw_df = pd.DataFrame(columns=["username", "date", "calories", "workout_type", "duration_min"])
        
        c_diet, c_work = st.columns(2)
        with c_diet:
            st.subheader("🥗 Diet Log")
            calories = st.number_input("Calories Consumed", min_value=0, max_value=10000, value=0)
        with c_work:
            st.subheader("🏋️ Workout Log")
            workout_type = st.text_input("Workout Type (e.g., Running, Gym)")
            duration = st.number_input("Duration (minutes)", min_value=0, max_value=300, value=0)
            
        if st.button("Save Daily Log 💾"):
            new_dw = pd.DataFrame([{"username": username, "date": today_str, "calories": calories, "workout_type": workout_type, "duration_min": duration}])
            update_sheet("diet_workout_logs", pd.concat([dw_df, new_dw], ignore_index=True))
            st.success("Log save ho gaya!")

        # Display history
        st.markdown("### Recent Logs")
        user_dw = dw_df[dw_df["username"] == username]
        if not user_dw.empty:
            st.dataframe(user_dw.tail(5), use_container_width=True)

    # ================= 4. BIOMETRICS & WEIGHT =================
    with tab_weight:
        st.markdown(f"<h2 class='header-style'>Weight Tracking</h2>", unsafe_allow_html=True)
        log_date = st.date_input("Date", value=date.today())
        daily_weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(user_info.get("weight", 70.0)))
        
        if st.button("Log Weight ⚖️"):
            wt_df = get_sheet("weight_tracker")
            if wt_df.empty: wt_df = pd.DataFrame(columns=["username", "date", "weight"])
            new_wt = pd.DataFrame([{"username": username, "date": str(log_date), "weight": daily_weight}])
            update_sheet("weight_tracker", pd.concat([wt_df, new_wt], ignore_index=True))
            
            # Also update current profile weight
            users_df = get_sheet("users")
            idx = users_df.index[users_df['username'] == username].tolist()[0]
            users_df.at[idx, 'weight'] = daily_weight
            update_sheet("users", users_df)
            st.session_state["user_data"]["weight"] = daily_weight
            
            st.success("Weight save ho gaya!")
            st.rerun()
            
        # Graph
        wt_df = get_sheet("weight_tracker")
        if not wt_df.empty:
            user_wt = wt_df[wt_df["username"] == username]
            if not user_wt.empty:
                fig = px.line(user_wt, x="date", y="weight", title="Weight Progress Chart", markers=True)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                st.plotly_chart(fig, use_container_width=True)

    # ================= 5. SETTINGS / EDIT PROFILE =================
    with tab_settings:
        st.markdown(f"<h2 class='header-style'>Account Settings</h2>", unsafe_allow_html=True)
        with st.expander("⚙️ Edit Profile / Update Information", expanded=True):
            st.write("Apni profile details ya password update karein:")
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                upd_age = st.number_input("Update Age:", min_value=10, value=int(user_info.get("age", 20)))
                upd_goal = st.selectbox("Update Goal:", ["Fat Loss", "Muscle Gain", "Fitness Maintenance"], 
                                        index=["Fat Loss", "Muscle Gain", "Fitness Maintenance"].index(user_info.get("goal", "Fat Loss")))
            with c_p2:
                upd_weight = st.number_input("Update Starting Weight:", value=float(user_info.get("weight", 70.0)))
                upd_pass = st.text_input("Naya Password (Khali chorein agar nahi badalna):", type="password")
                upd_pass_conf = st.text_input("Password Confirm karein:", type="password")

            if st.button("Save Profile Changes 💾", key="save_profile"):
                if upd_pass and upd_pass != upd_pass_conf:
                    st.error("Passwords match nahi kar rahe!")
                else:
                    users_df = get_sheet("users")
                    idx = users_df.index[users_df['username'] == username].tolist()[0]
                    
                    users_df.at[idx, 'age'] = upd_age
                    users_df.at[idx, 'goal'] = upd_goal
                    users_df.at[idx, 'weight'] = upd_weight
                    if upd_pass: users_df.at[idx, 'password'] = upd_pass
                        
                    update_sheet("users", users_df)
                    st.session_state["user_data"] = users_df.iloc[idx].to_dict()
                    st.success("🎉 Profile update ho gayi!")
                    time.sleep(1)
                    st.rerun()
