import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import time

# ==========================================
# 1. DATABASE MANAGEMENT (GOOGLE SHEETS Integration)
# ==========================================
st.set_page_config(
    page_title="Habit Tracker by Najam",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_sheet_data(sheet_name, expected_cols):
    """Google Sheet se data parhna aur khali hone par columns tayar karna"""
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df.empty or len(df.columns) == 0:
            return pd.DataFrame(columns=expected_cols)
        return df.dropna(how='all')
    except Exception:
        return pd.DataFrame(columns=expected_cols)

def update_sheet_data(sheet_name, df):
    """Google Sheet mein naya data push karna"""
    conn.update(worksheet=sheet_name, data=df)

# ==========================================
# 2. MOBILE-FRIENDLY CONFIGURATION & PREMIUM STYLING
# ==========================================
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 10%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 90% 80%, rgba(249, 115, 22, 0.08) 0%, transparent 40%),
                    #070a13;
        color: #f3f4f6;
    }
    
    @keyframes pulseGlow {
        0%, 100% { 
            text-shadow: 0 0 10px rgba(192, 132, 252, 0.4), 0 0 20px rgba(249, 115, 22, 0.2); 
            transform: scale(1);
        }
        50% { 
            text-shadow: 0 0 25px rgba(192, 132, 252, 0.8), 0 0 40px rgba(249, 115, 22, 0.6);
            transform: scale(1.02);
        }
    }
    
    .animated-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #c084fc 0%, #f97316 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        text-align: center;
        animation: pulseGlow 4s infinite ease-in-out;
        transition: all 0.3s ease;
        margin-bottom: 5px;
    }
    
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(6px);
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(139, 92, 246, 0.3);
        transform: translateY(-2px);
    }
    
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #8b5cf6 0%, #f97316 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: bold !important;
        width: 100% !important; 
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
        font-size: 16px !important;
    }
    
    div.stButton > button:first-child:hover {
        box-shadow: 0 6px 20px rgba(249, 115, 22, 0.5);
    }

    .leaderboard-row {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
        border-left: 4px solid #8b5cf6;
    }

    .slideshow-box {
        position: relative;
        width: 100%;
        height: 300px;
        overflow: hidden;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .slide-item {
        position: absolute;
        width: 100%;
        height: 100%;
        opacity: 0;
        animation: autoSlide 35s infinite;
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        padding: 20px;
        box-sizing: border-box;
    }
    
    .slide-item:nth-child(1) { animation-delay: 0s; }
    .slide-item:nth-child(2) { animation-delay: 5s; }
    .slide-item:nth-child(3) { animation-delay: 10s; }
    .slide-item:nth-child(4) { animation-delay: 15s; }
    .slide-item:nth-child(5) { animation-delay: 20s; }
    .slide-item:nth-child(6) { animation-delay: 25s; }
    .slide-item:nth-child(7) { animation-delay: 30s; }
    
    @keyframes autoSlide {
        0% { opacity: 0; transform: scale(1.05); }
        2% { opacity: 1; transform: scale(1); }
        12% { opacity: 1; }
        14% { opacity: 0; }
        100% { opacity: 0; }
    }
    
    .slide-overlay {
        background: linear-gradient(0deg, rgba(7, 10, 19, 0.95) 0%, rgba(7, 10, 19, 0.4) 100%);
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 24px;
        box-sizing: border-box;
    }
    
    @media (max-width: 768px) {
        .animated-title { font-size: 1.8rem !important; }
        .metric-card { padding: 10px; }
        .slideshow-box { height: 250px; }
    }
    
    .celebration-banner {
        text-align: center;
        background: rgba(17, 24, 39, 0.9);
        border: 2px solid;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        animation: popUp 0.5s ease-out forwards;
    }
    
    @keyframes popUp {
        0% { transform: scale(0.5); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Session Setup
if "logged_in" not in st.session_state: st.session_state["logged_in"] = False
if "username" not in st.session_state: st.session_state["username"] = ""
if "streak_notified" not in st.session_state: st.session_state["streak_notified"] = False

# ==========================================
# 3. MATHEMATICAL COMPUTATIONS HELPERS
# ==========================================
def calculate_bmi(weight, height, w_unit, h_unit):
    try:
        w_kg = float(weight) if w_unit == "Kilograms (kg)" else float(weight) * 0.453592
        if h_unit == "Centimeters (cm)":
            h_m = float(height) / 100
        else:
            h_m = float(height) * 0.3048
        if h_m > 0:
            return round(w_kg / (h_m ** 2), 2)
    except: pass
    return 0.0

def estimate_calories(age, weight, height, w_unit, h_unit, goal):
    try:
        w_kg = float(weight) if w_unit == "Kilograms (kg)" else float(weight) * 0.453592
        h_cm = float(height) if h_unit == "Centimeters (cm)" else float(height) * 30.48
        bmr = 10 * w_kg + 6.25 * h_cm - 5 * int(age) + 5
        if goal == "Fat Loss": return int(bmr * 1.2 - 350)
        elif goal == "Muscle Gain": return int(bmr * 1.35 + 300)
        else: return int(bmr * 1.3)
    except: return 2000

def update_and_get_streak(username):
    today_str = date.today().strftime("%Y-%m-%d")
    df_logs = get_sheet_data("login_logs", ["username", "login_date"])
    
    # Check if already logged today
    already_logged = not df_logs[(df_logs["username"] == username) & (df_logs["login_date"] == today_str)].empty
    
    if not already_logged:
        new_log = pd.DataFrame([{"username": username, "login_date": today_str}])
        df_logs = pd.concat([df_logs, new_log], ignore_index=True)
        update_sheet_data("login_logs", df_logs)
        
    user_logs = df_logs[df_logs["username"] == username]["login_date"].dropna().tolist()
    if not user_logs:
        return 0, False
        
    login_dates = sorted([datetime.strptime(str(d), "%Y-%m-%d").date() for d in user_logs], reverse=True)
    
    streak = 0
    current_check = date.today()
    for l_date in login_dates:
        if l_date == current_check:
            streak += 1
            current_check -= timedelta(days=1)
        elif l_date > current_check:
            continue
        else: break
            
    streak_increased = not already_logged and streak > 1
    return streak, streak_increased

def get_user_badges_and_xp(username):
    h_logs = get_sheet_data("habit_logs", ["username", "habit_name", "log_date", "status"])
    w_logs = get_sheet_data("weight_tracker", ["username", "weight", "bmi", "log_date"])
    habits = get_sheet_data("habits", ["username", "habit_name"])
    dw_logs = get_sheet_data("diet_workout_logs", ["username", "log_date", "diet_completed", "workout_completed"])
    
    completed_count = 0
    if not h_logs.empty:
        h_logs['status'] = pd.to_numeric(h_logs['status'], errors='coerce')
        completed_count = len(h_logs[(h_logs["username"] == username) & (h_logs["status"] == 1)])
        
    weight_count = len(w_logs[w_logs["username"] == username]) if not w_logs.empty else 0
    custom_count = len(habits[habits["username"] == username]) if not habits.empty else 0
    
    diet_count, workout_count = 0, 0
    if not dw_logs.empty:
        dw_logs['diet_completed'] = pd.to_numeric(dw_logs['diet_completed'], errors='coerce')
        dw_logs['workout_completed'] = pd.to_numeric(dw_logs['workout_completed'], errors='coerce')
        diet_count = len(dw_logs[(dw_logs["username"] == username) & (dw_logs["diet_completed"] == 1)])
        workout_count = len(dw_logs[(dw_logs["username"] == username) & (dw_logs["workout_completed"] == 1)])
        
    total_xp = (completed_count * 10) + (weight_count * 25) + (custom_count * 5) + (diet_count * 15) + (workout_count * 15)
    
    level = int(1 + (total_xp // 120))
    xp_for_next_level = int(120 - (total_xp % 120))
    progress_percentage = float((total_xp % 120) / 120.0)
    
    if level == 1: current_badge = {"name": "Starter Seed 🌱", "desc": "Safar ki shuruaat! Habits poori karein aur XP barhayen.", "color": "#10b981"}
    elif level == 2: current_badge = {"name": "Iron Warrior 🛡️", "desc": "Level 2! Aapki aadat pukhta ho rahi hai.", "color": "#94a3b8"}
    elif level == 3: current_badge = {"name": "Bronze Champion 🥉", "desc": "Level 3! Behtareen! Aapne ek solid routine bana li hai.", "color": "#d97706"}
    elif level == 4: current_badge = {"name": "Silver Samurai ⚔️", "desc": "Level 4! Zabardast consistency! Aap unstoppable hain.", "color": "#cbd5e1"}
    else: current_badge = {"name": "Golden Grandmaster 🏆", "desc": f"Level {level}! Kamaal kar diya! Ab aap ek misaal ban chuke hain.", "color": "#eab308"}
        
    return level, total_xp, xp_for_next_level, progress_percentage, current_badge

# ==========================================
# 4. GUEST / AUTHENTICATION INTERFACE
# ==========================================
if not st.session_state["logged_in"]:
    st.markdown("<h1 class='animated-title'>⚡ Habit Tracker by Najam</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="slideshow-box">
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1552674605-db6fea11e0d5?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Rukna nahi hai, thakna nahi hai!” 🌅</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Consistency hi kamyabi ka raaz hai. Apna daily progress yahan track karein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1512621776951-a57141f2eefd?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Sasta aur Healthy Pakistani Rashan!” 🥗</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Budget mein rehte huwe behtareen auto-generated diet plan hasil karein aur fit rahein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1517649763962-0c623066013b?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Doston ko Leaderboard par piche chorrein!” 🏆</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Healthy competition mein hissa lein, apna level up karein aur top rank hasil karein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1548839140-29a749e1ab14?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Pani zindgi hai! Hydration track karein.” 💧</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Din mein 8 glass pani poora karein, dehydration se bachein aur apni energy ko boost karein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1599058917212-d750089bc07e?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Bina Gym ke Calisthenics Routine!” 🤸</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Ghar bethe expert level home workouts follow karein aur strong fitness banayein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1474418397713-722a45d0dd31?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Zehni Sakoon aur Mood Tracking” 🧘</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Apni mental health ka khayal rakhein, habits track karein aur stress ko door bhagayein.</p>
            </div>
        </div>
        <div class="slide-item" style="background-image: url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1000');">
            <div class="slide-overlay">
                <h3 style="color:#ffffff; margin:0; font-family:'Poppins';">“Daily Streaks aur Badges Unlock Karein!” 🔥</h3>
                <p style="color:#a5b4fc; margin:0; font-size:14px;">Lagatar tracking se nayi achievements, XP points aur exclusive badges hasil karein.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
        
    auth_action = st.radio("Aap kya karna chahte hain?", ["Login (Pehle se Account hai)", "Sign Up (Naya Account Banayein)"])
    
    col_auth_left, col_auth_right = st.columns([1, 1])
    
    if auth_action == "Sign Up (Naya Account Banayein)":
        with col_auth_left:
            st.markdown("### 📝 Naya Account Banayein")
            su_user = st.text_input("Apna Pyara Sa Username Chunein:", key="su_u").strip()
            su_pass = st.text_input("Koi Password Likhein:", type="password", key="su_p")
            su_age = st.number_input("Aapki Umar (Age):", min_value=10, max_value=100, value=20)
            su_gender = st.selectbox("Apna Gender Chunein:", ["Male", "Female", "Other"])
            
        with col_auth_right:
            su_h_unit = st.selectbox("Height System Chunein:", ["Feet/Inches", "Centimeters (cm)"])
            if su_h_unit == "Feet/Inches":
                su_h_val = st.number_input("Height (e.g., 5.7 for 5ft 7in):", min_value=3.0, max_value=8.0, value=5.6, step=0.1)
            else:
                su_h_val = st.number_input("Height in cm:", min_value=100.0, max_value=250.0, value=168.0, step=1.0)
                
            su_w_unit = st.selectbox("Weight System Chunein:", ["Kilograms (kg)", "Pounds (lbs)"])
            su_w_val = st.number_input(f"Current Weight ({su_w_unit.split()[-1]}):", min_value=20.0, max_value=250.0, value=60.0)
            
            su_goal = st.selectbox("Aapka Fitness Goal Kya Hai?", ["Fat Loss", "Muscle Gain", "Fitness Maintenance"])
            
        if st.button("Naya Account Register Karein ✨"):
            if not su_user or not su_pass:
                st.error("Kuch blank mat chorein, username aur password lazmi hain!")
            else:
                users_cols = ["username", "password", "age", "gender", "height", "weight", "height_unit", "weight_unit", "goal", "target_calories"]
                users_df = get_sheet_data("users", users_cols)
                
                if su_user in users_df["username"].values:
                    st.error("Oops! Yeh username pehle se kisi ke pas hai. Koi aur naam chunein.")
                else:
                    cal = estimate_calories(su_age, su_w_val, su_h_val, su_w_unit, su_h_unit, su_goal)
                    new_user_row = pd.DataFrame([{
                        "username": su_user, "password": su_pass, "age": su_age, "gender": su_gender, 
                        "height": su_h_val, "weight": su_w_val, "height_unit": su_h_unit, 
                        "weight_unit": su_w_unit, "goal": su_goal, "target_calories": cal
                    }])
                    update_sheet_data("users", pd.concat([users_df, new_user_row], ignore_index=True))
                    
                    # Starter Habits
                    habits_df = get_sheet_data("habits", ["username", "habit_name"])
                    starter_habits = ["8 Glass Pani Peena 💧", "30-min Pushups/Workout 🤸", "Subah Jaldi Uthna 🌅"]
                    new_habits = pd.DataFrame([{"username": su_user, "habit_name": h} for h in starter_habits])
                    update_sheet_data("habits", pd.concat([habits_df, new_habits], ignore_index=True))
                    
                    st.success("🎉 Account successfully ban gaya! Ab upar 'Login' option select kar ke login karein.")
                    
    else:
        st.markdown("### 🔑 Apne Account Mein Login Karein")
        lin_u = st.text_input("Username:", key="lin_u").strip()
        lin_p = st.text_input("Password:", type="password", key="lin_p")
        
        if st.button("Magic Dashboard Par Chalein 🚀"):
            users_df = get_sheet_data("users", ["username", "password"])
            if not users_df.empty:
                user_match = users_df[(users_df["username"] == str(lin_u)) & (users_df["password"] == str(lin_p))]
                if not user_match.empty:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = lin_u
                    st.session_state["user_details"] = user_match.iloc[0].to_dict()
                    st.session_state["streak_notified"] = False
                    st.balloons()
                    st.rerun()
                else: st.error("Galat username ya password! Dobara check karein.")
            else: st.error("Database khali hai, pehle account banayein!")

# ==========================================
# 5. AUTHENTICATED EXPERIENCE
# ==========================================
else:
    user_info = st.session_state["user_details"]
    username = st.session_state["username"]
    
    current_streak, is_streak_inc = update_and_get_streak(username)
    level, xp, xp_needed, xp_progress, current_badge = get_user_badges_and_xp(username)
    
    st.markdown("<h1 class='animated-title'>⚡ Habit Tracker by Najam</h1>", unsafe_allow_html=True)
    
    if is_streak_inc and not st.session_state["streak_notified"]:
        st.balloons()
        st.session_state["streak_notified"] = True
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, rgba(249, 115, 22, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%); border: 2px solid #f97316; text-align: center;">
            <h2 style="margin: 0; color: #f97316; font-family: 'Poppins';">🔥 DOUBLE BLAST STREAK UP!</h2>
            <p style="font-size: 18px; color: #fff; margin: 10px 0 0 0;">Mubarak ho Najam! Aapki login streak barh kar <b>{current_streak} Days</b> ho gayi hai! Consistent rahein!</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="metric-card" style="border-left:5px solid #a855f7; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h4 style="margin:0; color:#fff;">🥋 Level {level} Hero</h4>
            <small style="color:#a5b4fc;">XP Points: {xp} | Next Level in {xp_needed} XP</small>
        </div>
        <div style="text-align: right;">
            <span style="background: linear-gradient(135deg, #f97316 0%, #8b5cf6 100%); padding: 6px 14px; border-radius: 50px; font-weight: bold; font-size: 14px; color: #fff;">
                🔥 {current_streak}-Day Streak
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.progress(xp_progress)
    
    tab_dashboard, tab_tracker, tab_diet, tab_biometrics, tab_settings = st.tabs([
        "🌌 Dashboard & Competitions",
        "📝 Habit Checklist",
        "🥗 Nutrition & Workout",
        "⚖️ Weight Progress",
        "🛠️ Settings"
    ])
    
    # ----------------------------------------
    # TAB 1: DASHBOARD & LEADERBOARD
    # ----------------------------------------
    with tab_dashboard:
        with st.expander("ℹ️ Welcome Guide (Click to Open)"):
            st.markdown("""
            ### Welcome to Habit Tracker by Najam! ⚡
            1. **Habit Checklist:** Apni daily habits ko complete karein.
            2. **Nutrition & Workout Guide:** Apni date chunein aur daily budget diet complete karein.
            3. **Daily Streak:** Rozana app open karne par aapki fire streak baregi.
            4. **Leaderboard:** Apne doston ke sath active rate competition karein.
            """)
            
        col_db1, col_db2 = st.columns([2, 1])
        with col_db1:
            st.subheader("🔥 Your Current Rank")
            
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; border: 2px solid {current_badge['color']}; background: linear-gradient(180deg, rgba(17,24,39,0.8) 0%, {current_badge['color']}15 100%); padding: 30px;">
                <h2 style="color:{current_badge['color']}; margin:0; font-size: 32px; font-family:'Poppins';">{current_badge['name']}</h2>
                <p style="color:#e5e7eb; font-size:16px; margin-top:10px;">{current_badge['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.write("💧 **Quick Glass Tracker (Water intake):**")
            water_today = st.slider("Aaj kitne glass paani peeya?", 0, 20, 8, key="quick_water")
            if water_today >= 10:
                st.success("Bohot behtareen! Dehydration cycle complete! 🧊")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_db2:
            st.subheader("🏆 Leaderboard")
            h_logs = get_sheet_data("habit_logs", ["username", "status"])
            
            if h_logs.empty:
                st.info("No logs present. Register other accounts to view competition!")
            else:
                h_logs['status'] = pd.to_numeric(h_logs['status'], errors='coerce')
                leaderboard_df = h_logs.groupby("username")["status"].agg(completed="sum", total="count").reset_index()
                leaderboard_df["Score (%)"] = ((leaderboard_df["completed"] / leaderboard_df["total"]) * 100).round(1)
                leaderboard_df = leaderboard_df.sort_values(by="Score (%)", ascending=False).reset_index(drop=True)
                medals = ["🥇", "🥈", "🥉"]
                
                for index, row in leaderboard_df.iterrows():
                    medal_icon = medals[index] if index < 3 else "⚡"
                    st.markdown(f"""
                    <div class="leaderboard-row">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <strong>{medal_icon} {row['username']}</strong>
                            <strong style="color:#f97316;">{row['Score (%)']}% Completion</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
        st.markdown("---")
        
        with st.expander("⚙️ Edit Profile / Update Information"):
            st.write("Apni profile details ya password update karein:")
            
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                upd_age = st.number_input("Update Age:", min_value=10, max_value=100, value=int(user_info["age"]))
                gender_opts = ["Male", "Female", "Other"]
                upd_gender = st.selectbox("Update Gender:", gender_opts, index=gender_opts.index(user_info["gender"]) if user_info["gender"] in gender_opts else 0)
                upd_goal = st.selectbox("Update Goal:", ["Fat Loss", "Muscle Gain", "Fitness Maintenance"], index=["Fat Loss", "Muscle Gain", "Fitness Maintenance"].index(user_info["goal"]))
            
            with c_p2:
                upd_h_val = st.number_input("Update Height:", min_value=3.0, max_value=250.0, value=float(user_info["height"]))
                upd_w_val = st.number_input("Update Weight:", min_value=20.0, max_value=300.0, value=float(user_info["weight"]))
                upd_pass = st.text_input("Naya Password (Khali chorein agar nahi badalna):", type="password")
                upd_pass_conf = st.text_input("Password Confirm karein:", type="password")

            if st.button("Save Profile Changes 💾"):
                if upd_pass and upd_pass != upd_pass_conf:
                    st.error("Passwords match nahi kar rahe!")
                else:
                    users_df = get_sheet_data("users", ["username", "password", "age", "gender", "height", "weight", "height_unit", "weight_unit", "goal", "target_calories"])
                    idx = users_df.index[users_df['username'] == username].tolist()[0]
                    
                    new_cal = estimate_calories(upd_age, upd_w_val, upd_h_val, user_info["height_unit"], user_info["weight_unit"], upd_goal)
                    
                    users_df.at[idx, 'age'] = upd_age
                    users_df.at[idx, 'gender'] = upd_gender
                    users_df.at[idx, 'height'] = upd_h_val
                    users_df.at[idx, 'weight'] = upd_w_val
                    users_df.at[idx, 'goal'] = upd_goal
                    users_df.at[idx, 'target_calories'] = new_cal
                    if upd_pass: users_df.at[idx, 'password'] = upd_pass
                        
                    update_sheet_data("users", users_df)
                    st.session_state["user_details"] = users_df.iloc[idx].to_dict()
                    st.success("🎉 Profile aur Password successfully update ho gaye!")
                    time.sleep(1)
                    st.rerun()

    # ----------------------------------------
    # TAB 2: INTERACTIVE CALENDAR TRACKER
    # ----------------------------------------
    with tab_tracker:
        st.subheader("📅 Date Wise Checklist Tracker")
        target_date = st.date_input("Khaas Tareeq (Select Date):", date.today(), max_value=date.today())
        target_date_str = target_date.strftime("%Y-%m-%d")
        
        habits_df = get_sheet_data("habits", ["username", "habit_name"])
        user_habits = habits_df[habits_df["username"] == username]["habit_name"].tolist()
        
        if not user_habits:
            st.info("Aapki list bilkul khali hai! 'Settings' tab par ja kar habits add karein.")
        else:
            logs_df = get_sheet_data("habit_logs", ["username", "habit_name", "log_date", "status"])
            user_logs = logs_df[(logs_df["username"] == username) & (logs_df["log_date"] == target_date_str)]
            logs_dict = dict(zip(user_logs["habit_name"], pd.to_numeric(user_logs["status"])))
            
            st.markdown(f"**Check off completed habits for date:** `{target_date_str}`")
            
            updated_statuses = {}
            for i, habit in enumerate(user_habits):
                current_checked = True if logs_dict.get(habit, 0) == 1 else False
                updated_statuses[habit] = st.checkbox(f"✔️ {habit}", value=current_checked, key=f"habit_chk_{i}_{target_date_str}")
                
            if st.button("Daily Score Update Karein 🎉", key="save_habits_mobile"):
                logs_df = get_sheet_data("habit_logs", ["username", "habit_name", "log_date", "status"])
                # Remove old logs for this date
                logs_df = logs_df[~((logs_df["username"] == username) & (logs_df["log_date"] == target_date_str))]
                
                new_logs = []
                for habit, is_checked in updated_statuses.items():
                    val = 1 if is_checked else 0
                    new_logs.append({"username": username, "habit_name": habit, "log_date": target_date_str, "status": val})
                    
                if new_logs:
                    logs_df = pd.concat([logs_df, pd.DataFrame(new_logs)], ignore_index=True)
                update_sheet_data("habit_logs", logs_df)
                
                st.balloons()
                st.markdown("""
                    <div class='celebration-banner' style='border-color: #a855f7;'>
                        <h1 style='color: #a855f7; font-size: 35px;'>🎉 KAMAAL KAR DIYA! 🎉</h1>
                        <h3 style='color: white;'>Aapki Habits Successfully Save Ho Gayin!</h3>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(2.5)
                st.rerun()
                
            st.markdown("---")
            st.subheader("📊 Habit Success Trends Over Time")
            all_logs_df = get_sheet_data("habit_logs", ["username", "habit_name", "log_date", "status"])
            all_logs_df = all_logs_df[all_logs_df["username"] == username].copy()
            
            if not all_logs_df.empty:
                all_logs_df["status"] = pd.to_numeric(all_logs_df["status"])
                all_logs_df["log_date"] = pd.to_datetime(all_logs_df["log_date"])
                daily_stats = all_logs_df.groupby("log_date").apply(lambda x: (x["status"].sum() / x["status"].count()) * 100).reset_index()
                daily_stats.columns = ["Date", "Completion Rate (%)"]
                daily_stats = daily_stats.sort_values("Date")
                
                fig = px.line(daily_stats, x="Date", y="Completion Rate (%)", markers=True)
                fig.update_traces(line_color="#a855f7", marker=dict(size=8, color="#f97316"))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.3)', font={'color': "#f3f4f6"}, yaxis_range=[0, 105], height=280)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📊 Habit Analytics (Daily, Weekly, Yearly)")
                
                today_dt_habit = pd.to_datetime(target_date_str)
                today_h_df = all_logs_df[all_logs_df["log_date"] == today_dt_habit]
                today_h_pct = int((today_h_df["status"].sum() / len(today_h_df)) * 100) if len(today_h_df) > 0 else 0

                week_ago_h = today_dt_habit - timedelta(days=7)
                week_h_df = all_logs_df[(all_logs_df["log_date"] > week_ago_h) & (all_logs_df["log_date"] <= today_dt_habit)]
                week_h_pct = int((week_h_df["status"].sum() / len(week_h_df)) * 100) if len(week_h_df) > 0 else 0

                year_h_df = all_logs_df[all_logs_df["log_date"].dt.year == today_dt_habit.year]
                year_h_pct = int((year_h_df["status"].sum() / len(year_h_df)) * 100) if len(year_h_df) > 0 else 0

                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    fig_h_today = go.Figure(go.Indicator(mode="gauge+number", value=today_h_pct, title={'text': "Daily Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#4ade80"}}))
                    fig_h_today.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                    st.plotly_chart(fig_h_today, use_container_width=True, key="habit_gauge_today")
                with col_h2:
                    fig_h_week = go.Figure(go.Indicator(mode="gauge+number", value=week_h_pct, title={'text': "Weekly Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#a855f7"}}))
                    fig_h_week.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                    st.plotly_chart(fig_h_week, use_container_width=True, key="habit_gauge_week")
                with col_h3:
                    fig_h_year = go.Figure(go.Indicator(mode="gauge+number", value=year_h_pct, title={'text': "Yearly Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#f97316"}}))
                    fig_h_year.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                    st.plotly_chart(fig_h_year, use_container_width=True, key="habit_gauge_year")
                
                st.markdown("#### 📅 Maheenay Ki Habits Ka Record (Monthly Summary)")
                month_h_df = all_logs_df[(all_logs_df["log_date"].dt.month == today_dt_habit.month) & (all_logs_df["log_date"].dt.year == today_dt_habit.year)].copy()
                if not month_h_df.empty:
                    month_h_df["log_date"] = month_h_df["log_date"].dt.strftime("%Y-%m-%d")
                    pivot_h = month_h_df.pivot_table(index="log_date", columns="habit_name", values="status", fill_value=0)
                    pivot_h = pivot_h.map(lambda x: "✅ Done" if x >= 1 else "❌ Missed")
                    st.dataframe(pivot_h, use_container_width=True)
                else:
                    st.info("Is maheenay ka koi record save nahi hua.")
            else:
                st.info("Trend graphs load karne ke liye checklists complete karein!")

    # ----------------------------------------
    # TAB 3: NUTRITION & WORKOUT GUIDE
    # ----------------------------------------
    with tab_diet:
        st.subheader("🥗 Pakistani Budget-Friendly Nutrition & Workout Engine")
        
        diet_date = st.date_input("Rozana Ke Plans Chunein (Select Plan Date):", date.today(), key="diet_workout_date")
        diet_date_str = diet_date.strftime("%Y-%m-%d")
        
        day_index = diet_date.weekday()
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        current_day_name = day_names[day_index]
        
        st.markdown(f"### 📅 Dynamic Plan For: **{current_day_name}** ({diet_date_str})")
        
        dw_logs_df = get_sheet_data("diet_workout_logs", ["username", "log_date", "diet_completed", "workout_completed"])
        dw_log = dw_logs_df[(dw_logs_df["username"] == username) & (dw_logs_df["log_date"] == diet_date_str)]
        
        logged_diet_status = True if (not dw_log.empty and int(dw_log.iloc[0]["diet_completed"]) == 1) else False
        logged_workout_status = True if (not dw_log.empty and int(dw_log.iloc[0]["workout_completed"]) == 1) else False
        goal_val = user_info["goal"]
        
        diets_database = {
            "Fat Loss": [
                {"nashta": "2 Boiled eggs + 1 Cup plain Tea + 1 small Roti", "dopehar": "1 Plate Boiled Kaalay Channay + salad", "dinner": "150g baked chicken breast + salad", "nutrition": "🔥 Calories: ~1350 kcal | 💪 Protein: ~75g"},
                {"nashta": "1 Boiled egg + 1 Glass Lassi (No sugar) + Apple", "dopehar": "1 Plate Boiled red beans (Lobia) + salad", "dinner": "1 Plate clean Moong Daal + half roti", "nutrition": "🔥 Calories: ~1280 kcal | 💪 Protein: ~55g"},
                {"nashta": "3 Egg white scramble + green tea", "dopehar": "Mix Vegetable Soup + half Roti", "dinner": "150g fish fillet or baked Lobia", "nutrition": "🔥 Calories: ~1200 kcal | 💪 Protein: ~68g"},
                {"nashta": "2 Boiled eggs + 1 Peach/Apple + Black Tea", "dopehar": "Chickpea salad with lemon", "dinner": "150g minced chicken + green salad", "nutrition": "🔥 Calories: ~1380 kcal | 💪 Protein: ~70g"},
                {"nashta": "1 Boiled egg + 1 Cup plain yogurt", "dopehar": "1 Plate boiled Dal Chana + salad", "dinner": "Palak curry + half Roti", "nutrition": "🔥 Calories: ~1150 kcal | 💪 Protein: ~45g"},
                {"nashta": "Omelette with onion + plain green tea", "dopehar": "1 plate boiled Keema + cucumber salad", "dinner": "150g steamed fish or chicken tikka", "nutrition": "🔥 Calories: ~1400 kcal | 💪 Protein: ~80g"},
                {"nashta": "2 Boiled eggs + plain water with lemon", "dopehar": "Split peas boiled salad", "dinner": "Cabbage soup + grilled chicken", "nutrition": "🔥 Calories: ~1100 kcal | 💪 Protein: ~65g"}
            ],
            "Muscle Gain": [
                {"nashta": "3 Whole Eggs scramble + 1 Paratha + milk + Bananas", "dopehar": "1 big Plate Daal Chawal + dahi", "dinner": "200g beef mince + 2 Rotis", "nutrition": "🔥 Calories: ~2600 kcal | 💪 Protein: ~120g"},
                {"nashta": "3 Scrambled Eggs + brown bread + dates shake", "dopehar": "1 Plate chicken pulao + raita", "dinner": "Palak Paneer + 2 flatbreads", "nutrition": "🔥 Calories: ~2450 kcal | 💪 Protein: ~105g"},
                {"nashta": "Oatmeal in whole milk + 2 boiled eggs", "dopehar": "1 plate white Lobia + rice + dahi", "dinner": "200g grilled chicken + 2 Rotis", "nutrition": "🔥 Calories: ~2550 kcal | 💪 Protein: ~115g"},
                {"nashta": "3 Boiled eggs + banana shake + 1 Roti", "dopehar": "Chicken karahi + 2 Rotis + salad", "dinner": "Daal Mash with butter + 2 Rotis", "nutrition": "🔥 Calories: ~2700 kcal | 💪 Protein: ~125g"},
                {"nashta": "3 Egg cheese scramble + milk + Dates", "dopehar": "Beef stew (Nihari) + 1 nan", "dinner": "200g baked chicken breast + 2 Rotis + dahi", "nutrition": "🔥 Calories: ~2650 kcal | 💪 Protein: ~130g"},
                {"nashta": "Banana pancake + honey", "dopehar": "1 Plate Biryani + dahi raita", "dinner": "Egg bhurji (4 eggs) + 2 Parathas", "nutrition": "🔥 Calories: ~2800 kcal | 💪 Protein: ~110g"},
                {"nashta": "4 Egg whites + 2 whole eggs + dates milk shake + 1 Roti", "dopehar": "Boiled red beans with mutton mince + rice", "dinner": "Palak paneer with cheese + 2 Rotis", "nutrition": "🔥 Calories: ~2750 kcal | 💪 Protein: ~135g"}
            ],
            "Fitness Maintenance": [
                {"nashta": "2 Boiled eggs + 1 Roti + Tea", "dopehar": "Mix vegetable curry + 1 roti + dahi", "dinner": "Oatmeal in milk + 1 ubla egg", "nutrition": "🔥 Calories: ~1800 kcal | 💪 Protein: ~65g"},
                {"nashta": "Omelette (2 eggs) + 2 slices bread + green tea", "dopehar": "1 Plate Dal Chawal + cucumber salad", "dinner": "Light chicken curry + 1 Roti", "nutrition": "🔥 Calories: ~1900 kcal | 💪 Protein: ~75g"},
                {"nashta": "2 Boiled eggs + 1 apple + tea", "dopehar": "Lobia curry + 1 flatbread + green salad", "dinner": "Mix seasonal vegetable + 1 Roti + yogurt", "nutrition": "🔥 Calories: ~1750 kcal | 💪 Protein: ~60g"},
                {"nashta": "Scrambled eggs + 1 Roti + green tea", "dopehar": "Chicken soup with vegetables + half Roti", "dinner": "Daal Mong + 1 flat Roti", "nutrition": "🔥 Calories: ~1850 kcal | 💪 Protein: ~70g"},
                {"nashta": "1 glass milk with 2 dates + 2 boiled eggs", "dopehar": "Chickpea salad + 1 Roti", "dinner": "Pan-cooked fish fillet + 1 cup dahi", "nutrition": "🔥 Calories: ~1950 kcal | 💪 Protein: ~85g"},
                {"nashta": "2 slices brown bread toast + 2 uble anday + lassi", "dopehar": "1 Plate simple chicken pulao + salad", "dinner": "Oatmeal dalya with seasonal fruits", "nutrition": "🔥 Calories: ~1700 kcal | 💪 Protein: ~58g"},
                {"nashta": "2 Boiled eggs + 1 banana + green tea", "dopehar": "Mix daal with steamed white rice", "dinner": "Chicken tikka pieces + 1 Roti + salad", "nutrition": "🔥 Calories: ~1800 kcal | 💪 Protein: ~80g"}
            ]
        }
        
        workouts_database = [
            {"focus": "Chest & Triceps Blast", "exercises": "Standard Pushups (3 sets x 12 reps) + Bench Dips (3 sets x 15 reps) + Diamond Pushups (2 sets x 8 reps)"},
            {"focus": "Active Back & Pulls", "exercises": "Doorframe Pulls or Inverted Table Rows (3 sets x 10 reps) + Towel curls + Superman stretches (3 sets x 15 reps)"},
            {"focus": "Power Legs & Glutes", "exercises": "Deep bodyweight Squats (4 sets x 15 reps) + Walking Lunges (3 sets x 12 reps each leg) + Calf raises (3 sets x 20 reps)"},
            {"focus": "Shoulders & Arms Fit", "exercises": "Pike Pushups (3 sets x 8 reps) + Crab walks (3 sets x 1 minute) + Arm circles with water bottles"},
            {"focus": "Active Core & Abs", "exercises": "Standard Plank Hold (3 rounds x 45 seconds each) + Crunches (3 sets x 15 reps) + Leg raises (3 sets x 12 reps)"},
            {"focus": "Full Body Cardio/HIIT", "exercises": "Jumping Jacks (3 sets x 40 seconds) + Burpees (3 sets x 8 reps) + Mountain Climbers (3 sets x 20 reps)"},
            {"focus": "Active Stretching & Recovery", "exercises": "Full body dynamic stretching + 5-minute deep breathing + Hydration"}
        ]
        
        selected_diet = diets_database[goal_val][day_index]
        selected_workout = workouts_database[day_index]
        
        st.markdown(f"#### 🥗 Budget Diet Menu ({goal_val})")
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #4ade80;">
            <p style="color:#4ade80; font-weight:bold; font-size:17px; margin-bottom:10px;">{selected_diet['nutrition']}</p>
            <ul>
                <li><strong>Nashta (Breakfast):</strong> {selected_diet['nashta']}</li>
                <li><strong>Dopehar (Lunch):</strong> {selected_diet['dopehar']}</li>
                <li><strong>Dinner:</strong> {selected_diet['dinner']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"#### 🤸 Calisthenics Routine ({selected_workout['focus']})")
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #a855f7;">
            <p><strong>Target Routine:</strong></p>
            <p style="font-size: 16px; color: #f3f4f6;">{selected_workout['exercises']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📝 Plan Completion Checklists")
        col_chk1, col_chk2 = st.columns(2)
        with col_chk1:
            diet_checked = st.checkbox("Main ne Aaj ki Diet poori ki! 🥗", value=logged_diet_status, key="diet_completed_check")
        with col_chk2:
            workout_checked = st.checkbox("Main ne Aaj ka Workout poora kiya! 🤸", value=logged_workout_status, key="workout_completed_check")
            
        if st.button("Save Diet & Workout Status 💾"):
            diet_val = 1 if diet_checked else 0
            workout_val = 1 if workout_checked else 0
            
            dw_logs_df = get_sheet_data("diet_workout_logs", ["username", "log_date", "diet_completed", "workout_completed"])
            dw_logs_df = dw_logs_df[~((dw_logs_df["username"] == username) & (dw_logs_df["log_date"] == diet_date_str))]
            new_dw = pd.DataFrame([{"username": username, "log_date": diet_date_str, "diet_completed": diet_val, "workout_completed": workout_val}])
            dw_logs_df = pd.concat([dw_logs_df, new_dw], ignore_index=True)
            update_sheet_data("diet_workout_logs", dw_logs_df)
            
            st.balloons()
            st.markdown("""
                <div class='celebration-banner' style='border-color: #f97316;'>
                    <h1 style='color: #f97316; font-size: 35px;'>🔥 BEHTAREEN! 🔥</h1>
                    <h3 style='color: white;'>Diet Aur Workout Target Achieved!</h3>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(2.5)
            st.rerun()
            
        st.markdown("---")
        st.subheader("📊 Diet & Workout Analytics (Daily, Weekly, Yearly)")
        dw_logs_df = get_sheet_data("diet_workout_logs", ["username", "log_date", "diet_completed", "workout_completed"])
        user_dw = dw_logs_df[dw_logs_df["username"] == username].copy()
        
        if not user_dw.empty:
            user_dw["diet_completed"] = pd.to_numeric(user_dw["diet_completed"], errors='coerce')
            user_dw["workout_completed"] = pd.to_numeric(user_dw["workout_completed"], errors='coerce')
            user_dw["log_date"] = pd.to_datetime(user_dw["log_date"])
            today_dt = pd.to_datetime(diet_date_str)
            
            today_df = user_dw[user_dw["log_date"] == today_dt]
            if not today_df.empty:
                t_diet = today_df.iloc[0]["diet_completed"]
                t_work = today_df.iloc[0]["workout_completed"]
                today_pct = int(((t_diet + t_work) / 2.0) * 100)
            else:
                today_pct = 0
                
            week_ago = today_dt - timedelta(days=7)
            week_df = user_dw[(user_dw["log_date"] > week_ago) & (user_dw["log_date"] <= today_dt)]
            week_pct = int(((week_df["diet_completed"].sum() + week_df["workout_completed"].sum()) / (len(week_df) * 2)) * 100) if len(week_df) > 0 else 0
            
            year_df = user_dw[user_dw["log_date"].dt.year == today_dt.year]
            year_pct = int(((year_df["diet_completed"].sum() + year_df["workout_completed"].sum()) / (len(year_df) * 2)) * 100) if len(year_df) > 0 else 0
            
            col_dw1, col_dw2, col_dw3 = st.columns(3)
            with col_dw1:
                fig_d_today = go.Figure(go.Indicator(mode="gauge+number", value=today_pct, title={'text': "Daily Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#4ade80"}}))
                fig_d_today.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                st.plotly_chart(fig_d_today, use_container_width=True, key="diet_gauge_today")
            with col_dw2:
                fig_d_week = go.Figure(go.Indicator(mode="gauge+number", value=week_pct, title={'text': "Weekly Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#a855f7"}}))
                fig_d_week.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                st.plotly_chart(fig_d_week, use_container_width=True, key="diet_gauge_week")
            with col_dw3:
                fig_d_year = go.Figure(go.Indicator(mode="gauge+number", value=year_pct, title={'text': "Yearly Score"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#f97316"}}))
                fig_d_year.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', font={'color': "#f3f4f6"})
                st.plotly_chart(fig_d_year, use_container_width=True, key="diet_gauge_year")
                
            st.markdown("#### 📅 Maheenay Ka Diet & Workout Record (Monthly Summary)")
            month_dw_df = user_dw[(user_dw["log_date"].dt.month == today_dt.month) & (user_dw["log_date"].dt.year == today_dt.year)].copy()
            if not month_dw_df.empty:
                month_dw_df["log_date"] = month_dw_df["log_date"].dt.strftime("%Y-%m-%d")
                month_dw_df["Diet Status"] = month_dw_df["diet_completed"].map(lambda x: "🥗 Done" if x == 1 else "❌ Missed")
                month_dw_df["Workout Status"] = month_dw_df["workout_completed"].map(lambda x: "🤸 Done" if x == 1 else "❌ Missed")
                st.dataframe(month_dw_df[["log_date", "Diet Status", "Workout Status"]].set_index("log_date"), use_container_width=True)
            else:
                st.info("Is maheenay ka koi record save nahi hua.")

    # ----------------------------------------
    # TAB 4: WEIGHT PROGRESS
    # ----------------------------------------
    with tab_biometrics:
        st.subheader("⚖️ Biometric updates & Trend Card")
        col_wl1, col_wl2 = st.columns(2)
        with col_wl1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("#### Update Weight")
            wt_val = st.number_input("Apna aaj ka weight enter karein:", min_value=10.0, max_value=300.0, value=float(user_info["weight"]), step=0.1)
            wt_date = st.date_input("Logging Date:", date.today(), max_value=date.today(), key="wt_date_mobile")
            wt_date_str = wt_date.strftime("%Y-%m-%d")
            
            calculated_bmi_val = calculate_bmi(wt_val, user_info["height"], user_info["weight_unit"], user_info["height_unit"])
            
            if calculated_bmi_val < 18.5:
                live_bmi_status, live_bmi_color = "Underweight (Kamzor) 🥣", "#38bdf8"
            elif 18.5 <= calculated_bmi_val < 24.9:
                live_bmi_status, live_bmi_color = "Normal Fit (Munasib) 🟢", "#4ade80"
            elif 25.0 <= calculated_bmi_val < 29.9:
                live_bmi_status, live_bmi_color = "Overweight (Motaapa Shuru) 🟡", "#facc15"
            else:
                live_bmi_status, live_bmi_color = "Obese (Bohot Ziada Weight) 🔴", "#f87171"
                
            st.markdown(f"**Live Calculated BMI Preview:** <span style='font-size:20px; color:{live_bmi_color}; font-weight:bold;'>{calculated_bmi_val} ({live_bmi_status})</span>", unsafe_allow_html=True)
            
            if st.button("New Weight Metric Save Karein 💾"):
                w_df = get_sheet_data("weight_tracker", ["username", "weight", "bmi", "log_date"])
                w_df = w_df[~((w_df["username"] == username) & (w_df["log_date"] == wt_date_str))]
                new_w = pd.DataFrame([{"username": username, "weight": wt_val, "bmi": calculated_bmi_val, "log_date": wt_date_str}])
                w_df = pd.concat([w_df, new_w], ignore_index=True)
                update_sheet_data("weight_tracker", w_df)
                
                st.balloons()
                st.markdown("""
                    <div class='celebration-banner' style='border-color: #38bdf8;'>
                        <h1 style='color: #38bdf8; font-size: 35px;'>⚖️ PERFECT! ⚖️</h1>
                        <h3 style='color: white;'>Aapka Naya Weight Update Ho Gaya!</h3>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(2.5)
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_wl2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("#### Formula used:")
            st.latex(r"BMI = \frac{Weight (kg)}{Height (m)^2}")
            st.write(f"🧑 **Age:** {user_info['age']} years")
            st.write(f"📏 **Height Value:** {user_info['height']} {user_info['height_unit']}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        weight_df = get_sheet_data("weight_tracker", ["username", "weight", "bmi", "log_date"])
        user_w_df = weight_df[weight_df["username"] == username].copy()
        
        if not user_w_df.empty:
            user_w_df = user_w_df.sort_values(by="log_date")
            st.markdown("---")
            st.subheader("📉 Weight Trend Curve")
            fig_w = px.line(user_w_df, x="log_date", y="weight", markers=True)
            fig_w.update_traces(line_color="#f97316", marker=dict(size=8, color="#8b5cf6"))
            fig_w.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(17,24,39,0.3)', font={'color': "#f3f4f6"}, height=280)
            st.plotly_chart(fig_w, use_container_width=True)
            st.markdown("#### 📊 Past Biometrics & BMI History Log")
            st.dataframe(user_w_df, use_container_width=True)

    # ----------------------------------------
    # TAB 5: SETTINGS & ADMIN PANEL
    # ----------------------------------------
    with tab_settings:
        st.subheader("🛠️ Settings & Admin Panel")
        
        # --- ADMIN PANEL (Sirf Aapke liye) ---
        if username == "Najam": # Yahan apna username likhein
            st.markdown("---")
            st.markdown("### 👑 Admin Control Panel")
            all_users = get_sheet_data("users", ["username", "password",
