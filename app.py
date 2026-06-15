import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import hashlib
import json
from typing import Optional, Tuple, List

st.set_page_config(
    page_title="Habit Tracker by Najam",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS - ULTRA PREMIUM CINEMATIC UI
# =============================================================================
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --primary: #8b5cf6;
    --accent: #f97316;
    --bg-dark: #070a13;
    --glass: rgba(15, 23, 42, 0.85);
}

body, .stApp {
    background: linear-gradient(135deg, #070a13 0%, #0d1527 100%);
    font-family: 'Inter', sans-serif;
    color: #f3f4f6;
}

.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 30%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(249, 115, 22, 0.15) 0%, transparent 50%),
        linear-gradient(45deg, transparent 40%, rgba(139, 92, 246, 0.08) 50%, transparent 60%);
    animation: ambientPulse 25s ease infinite;
    z-index: -1;
    pointer-events: none;
}

@keyframes ambientPulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}

h1, h2, h3, h4 {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.main-title {
    font-size: 3.2rem;
    background: linear-gradient(90deg, #c4b5fd, #f3e8ff, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: eliteGlow 3s ease-in-out infinite alternate;
    text-shadow: 0 0 40px rgba(139, 92, 246, 0.8);
    margin-bottom: 0.2rem;
}

@keyframes eliteGlow {
    from { filter: brightness(1) drop-shadow(0 0 15px #8b5cf6); }
    to { filter: brightness(1.15) drop-shadow(0 0 35px #f97316); }
}

.glass-card {
    background: var(--glass);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px;
    padding: 1.8rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4),
                inset 0 0 0 1px rgba(255,255,255,0.08);
    transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 40%;
    height: 40%;
    background: radial-gradient(circle, rgba(249,115,22,0.25) 0%, transparent 70%);
    opacity: 0;
    transition: all 0.5s ease;
}

.glass-card:hover {
    transform: translateY(-8px);
    border-color: #f97316;
    box-shadow: 0 25px 50px rgba(139, 92, 246, 0.25);
}

.glass-card:hover::before {
    opacity: 1;
    transform: scale(1.8);
}

.stButton > button {
    background: linear-gradient(90deg, #8b5cf6, #f97316);
    border: none;
    color: white;
    font-weight: 600;
    border-radius: 9999px;
    padding: 0.75rem 2rem;
    transition: all 0.3s cubic-bezier(0.23, 1, 0.32, 1);
    box-shadow: 0 10px 25px rgba(139, 92, 246, 0.4);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-size: 0.95rem;
}

.stButton > button:hover {
    transform: scale(1.05) translateY(-2px);
    box-shadow: 0 20px 40px rgba(249, 115, 22, 0.5);
}

.stButton > button:active {
    transform: scale(0.98);
}

.tab-container {
    display: flex;
    gap: 2px;
    border-bottom: 2px solid rgba(139, 92, 246, 0.3);
}

.custom-tab {
    padding: 1rem 1.8rem;
    cursor: pointer;
    position: relative;
    font-weight: 600;
    transition: all 0.3s ease;
}

.custom-tab.active {
    color: #f97316;
}

.custom-tab.active::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 100%;
    height: 4px;
    background: linear-gradient(to right, #8b5cf6, #f97316);
    border-radius: 4px;
    animation: tabSlide 0.4s ease;
}

@keyframes tabSlide {
    from { width: 0; }
    to { width: 100%; }
}

.metric-value {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #c4b5fd, #f3e8ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stDataFrame {
    animation: slideInUp 0.8s ease forwards;
}

@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(40px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.success-banner {
    animation: successPop 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes successPop {
    0% { transform: scale(0.6); opacity: 0; }
    60% { transform: scale(1.15); }
    100% { transform: scale(1); }
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# =============================================================================
# DATABASE UTILITIES
# =============================================================================
def get_db_connection():
    try:
        conn = psycopg2.connect(st.secrets["DATABASE_URL"])
        return conn
    except Exception:
        st.error("Database connection failed. Check secrets.")
        st.stop()

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            height_unit TEXT DEFAULT 'cm',
            weight_unit TEXT DEFAULT 'kg',
            goal TEXT,
            target_calories INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            habit_name TEXT NOT NULL,
            UNIQUE(username, habit_name)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS habit_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            habit_name TEXT NOT NULL,
            log_date DATE NOT NULL,
            status INTEGER DEFAULT 0,
            UNIQUE(username, habit_name, log_date)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weight_tracker (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            weight REAL,
            bmi REAL,
            log_date DATE NOT NULL
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS diet_workout_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            log_date DATE NOT NULL,
            diet_completed INTEGER DEFAULT 0,
            workout_completed INTEGER DEFAULT 0,
            UNIQUE(username, log_date)
        )
    """)
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            login_date DATE NOT NULL,
            UNIQUE(username, login_date)
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username: str, password: str) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    if result:
        return result[0] == hash_password(password)
    return False

def create_user(user_data: dict):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, age, gender, height, weight, height_unit, weight_unit, goal, target_calories)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_data['username'],
            hash_password(user_data['password']),
            user_data['age'],
            user_data['gender'],
            user_data['height'],
            user_data['weight'],
            user_data['height_unit'],
            user_data['weight_unit'],
            user_data['goal'],
            user_data['target_calories']
        ))
        # Seed starter habits
        starter_habits = [
            "8 Glass Pani Peena 💧",
            "30-min Pushups/Workout 🤸",
            "Subah Jaldi Uthna 🌅"
        ]
        for habit in starter_habits:
            cur.execute("INSERT INTO habits (username, habit_name) VALUES (%s, %s) ON CONFLICT DO NOTHING", 
                       (user_data['username'], habit))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def calculate_bmr(weight: float, height: float, age: int, gender: str) -> int:
    if gender.lower() == "male":
        return int(88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age))
    else:
        return int(447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age))

def calculate_bmi(weight: float, height_cm: float) -> float:
    if height_cm <= 0:
        return 0
    return round(weight / ((height_cm / 100) ** 2), 1)

def get_streak(username: str) -> int:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT login_date FROM login_logs 
        WHERE username = %s 
        ORDER BY login_date DESC
    """, (username,))
    dates = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    if not dates:
        return 0
    
    streak = 1
    current = dates[0]
    for d in dates[1:]:
        if (current - d).days == 1:
            streak += 1
            current = d
        else:
            break
    return streak

def get_xp(username: str) -> Tuple[int, int]:
    # Simple XP calculation - can be expanded with more logs
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Habits completed today
    cur.execute("""
        SELECT COUNT(*) FROM habit_logs 
        WHERE username = %s AND log_date = CURRENT_DATE AND status = 1
    """, (username,))
    habit_xp = cur.fetchone()[0] * 10
    
    # Weight logs (last 30 days)
    cur.execute("""
        SELECT COUNT(*) FROM weight_tracker 
        WHERE username = %s AND log_date >= CURRENT_DATE - INTERVAL '30 days'
    """, (username,))
    weight_xp = cur.fetchone()[0] * 25
    
    # Diet + Workout
    cur.execute("""
        SELECT COUNT(*) FROM diet_workout_logs 
        WHERE username = %s AND (diet_completed = 1 OR workout_completed = 1) 
        AND log_date >= CURRENT_DATE - INTERVAL '30 days'
    """, (username,))
    dw_xp = cur.fetchone()[0] * 15
    
    total_xp = habit_xp + weight_xp + dw_xp + 50  # base
    level = (total_xp // 120) + 1
    cur.close()
    conn.close()
    return total_xp, level

def get_badge(level: int) -> str:
    badges = {
        1: "🌱 Starter Seed",
        2: "🛡️ Iron Warrior",
        3: "🥉 Bronze Champion",
        4: "⚔️ Silver Samurai",
    }
    return badges.get(level, "🏆 Golden Grandmaster")

# =============================================================================
# MAIN APP
# =============================================================================
def main():
    init_db()
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    if not st.session_state.logged_in:
        # LANDING PAGE
        st.markdown("""
        <div style="text-align: center; padding: 4rem 1rem 2rem;">
            <h1 class="main-title">⚡ Habit Tracker by Najam</h1>
            <p style="font-size: 1.4rem; color: #e5e7eb; max-width: 600px; margin: 1rem auto;">
                Forge your legacy. Track. Level up. Dominate.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            auth_mode = st.segmented_control(
                "Get Started", 
                options=["Login", "Sign Up"], 
                selection_mode="single",
                default="Login"
            )
            
            if auth_mode == "Sign Up":
                with st.form("signup_form"):
                    st.markdown("#### Create Elite Profile")
                    username = st.text_input("Username", key="su_user")
                    password = st.text_input("Password", type="password", key="su_pass")
                    age = st.number_input("Age", 14, 80, 25)
                    gender = st.selectbox("Gender", ["Male", "Female"])
                    col_h, col_w = st.columns(2)
                    with col_h:
                        height = st.number_input("Height", 100, 250, 170)
                        height_unit = st.selectbox("Unit", ["cm", "ft"], index=0)
                    with col_w:
                        weight = st.number_input("Weight", 30, 200, 70)
                        weight_unit = st.selectbox("Unit", ["kg", "lbs"], index=0)
                    goal = st.selectbox("Primary Goal", 
                                      ["Fat Loss", "Muscle Gain", "Maintenance"])
                    
                    if st.form_submit_button("Create Account & Begin Journey"):
                        if username and password:
                            try:
                                # Adjust height/weight if needed
                                h_cm = height if height_unit == "cm" else height * 30.48
                                w_kg = weight if weight_unit == "kg" else weight * 0.453592
                                
                                bmr = calculate_bmr(w_kg, h_cm, age, gender)
                                target_cal = int(bmr * 1.55)  # moderate activity
                                
                                user_data = {
                                    "username": username.strip().lower(),
                                    "password": password,
                                    "age": age,
                                    "gender": gender,
                                    "height": height,
                                    "weight": weight,
                                    "height_unit": height_unit,
                                    "weight_unit": weight_unit,
                                    "goal": goal,
                                    "target_calories": target_cal
                                }
                                create_user(user_data)
                                st.success("Account created. Welcome to the elite circle!")
                                st.balloons()
                                st.session_state.logged_in = True
                                st.session_state.username = username.strip().lower()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Signup failed: {str(e)}")
            else:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    if st.form_submit_button("Login"):
                        if verify_user(username.strip().lower(), password):
                            st.session_state.logged_in = True
                            st.session_state.username = username.strip().lower()
                            # Record login
                            conn = get_db_connection()
                            cur = conn.cursor()
                            today = date.today()
                            cur.execute("""
                                INSERT INTO login_logs (username, login_date) 
                                VALUES (%s, %s) ON CONFLICT DO NOTHING
                            """, (st.session_state.username, today))
                            conn.commit()
                            cur.close()
                            conn.close()
                            
                            st.success("Welcome back, Champion!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
        
        # Cinematic Slideshow Teaser
        st.markdown("""
        <div style="margin: 4rem 0 2rem; text-align: center;">
            <h2 style="color: #c4b5fd;">Real Warriors. Real Results.</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple animated cards for demo slides
        cols = st.columns(4)
        themes = [
            ("Pakistani Budget Diets", "🥘", "#8b5cf6"),
            ("Calisthenics Mastery", "🏋️", "#f97316"),
            ("Daily Hydration", "💧", "#22d3ee"),
            ("Leaderboards", "🏆", "#eab308")
        ]
        for i, (title, emoji, color) in enumerate(themes):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; min-height: 180px; display:flex; flex-direction:column; justify-content:center; border-color: {color}40;">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">{emoji}</div>
                    <h4 style="margin:0;">{title}</h4>
                </div>
                """, unsafe_allow_html=True)
        return
    
    # =============================================================================
    # LOGGED IN EXPERIENCE
    # =============================================================================
    username = st.session_state.username
    
    # Header
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h1 class="main-title" style="font-size: 2.4rem;">⚡ Habit Tracker by Najam</h1>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="background: rgba(139,92,246,0.2); padding: 0.5rem 1rem; border-radius: 9999px; font-size: 0.95rem;">
                @{username}
            </div>
            <button onclick="window.location.reload()" style="background: transparent; border: 1px solid #f97316; color: #f97316; padding: 0.4rem 1rem; border-radius: 9999px; cursor: pointer;">
                Logout
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    streak = get_streak(username)
    xp, level = get_xp(username)
    badge = get_badge(level)
    progress = (xp % 120) / 120 * 100
    
    # Streak Banner
    if streak > 1:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #f97316, #ef4444); color: white; padding: 1rem; border-radius: 16px; text-align: center; margin-bottom: 1.5rem; font-weight: 700; font-size: 1.3rem; animation: successPop 1s;">
            🔥 DOUBLE BLAST STREAK UP! {streak} DAYS 🔥
        </div>
        """, unsafe_allow_html=True)
    
    tabs = st.tabs(["Dashboard & Competitions", "Habit Checklist", "Nutrition & Workout", "Weight & Biometrics", "Settings"])
    
    # TAB 1: DASHBOARD
    with tabs[0]:
        col_a, col_b, col_c = st.columns([3, 3, 2])
        
        with col_a:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Today's Hydration")
            glasses = st.slider("Glasses of Water 💧", 0, 20, 8, key="water_slider")
            if glasses >= 10:
                st.success("💧 HYDRATION LEGEND STATUS UNLOCKED")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Your Level")
            st.markdown(f"""
            <div style="text-align: center;">
                <div style="font-size: 4rem; line-height: 1;">{level}</div>
                <div style="font-size: 1.1rem; color: #c4b5fd;">{badge}</div>
                <div class="metric-value">{xp} XP</div>
                <div style="height: 8px; background: #334155; border-radius: 9999px; overflow: hidden; margin: 1rem 0;">
                    <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, #8b5cf6, #f97316);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_c:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("Current Streak")
            st.markdown(f"<div style='font-size: 4.5rem; text-align:center; color:#f97316;'>{streak} <span style='font-size:1.2rem;'>days</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Leaderboard
        st.markdown("### 🏆 Global Leaderboard")
        # Mock leaderboard for demo
        leaderboard_data = [
            {"rank": 1, "user": "warrior_khan", "score": 1240, "streak": 42},
            {"rank": 2, "user": "iron_zain", "score": 980, "streak": 19},
            {"rank": 3, "user": username, "score": xp + 420, "streak": streak},
        ]
        for entry in leaderboard_data:
            medal = "🥇" if entry["rank"] == 1 else "🥈" if entry["rank"] == 2 else "🥉"
            st.markdown(f"""
            <div class="glass-card" style="display:flex; align-items:center; justify-content:space-between; padding: 1rem 1.5rem;">
                <div style="display:flex; align-items:center; gap: 1rem;">
                    <span style="font-size: 2rem;">{medal}</span>
                    <div>
                        <strong>@{entry['user']}</strong><br>
                        <small>{entry['streak']} day streak</small>
                    </div>
                </div>
                <div class="metric-value" style="font-size: 1.8rem;">{entry['score']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 2: HABIT CHECKLIST
    with tabs[1]:
        selected_date = st.date_input("Select Date", value=date.today(), key="habit_date")
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT habit_name FROM habits WHERE username = %s", (username,))
        habits = [row[0] for row in cur.fetchall()]
        
        if not habits:
            habits = ["8 Glass Pani Peena 💧", "30-min Pushups/Workout 🤸"]
        
        st.markdown("### Daily Checklist")
        completed = {}
        for habit in habits:
            completed[habit] = st.checkbox(habit, value=False, key=f"chk_{habit}")
        
        if st.button("✅ Log Today's Habits", type="primary"):
            for habit, status in completed.items():
                cur.execute("""
                    INSERT INTO habit_logs (username, habit_name, log_date, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username, habit_name, log_date) 
                    DO UPDATE SET status = EXCLUDED.status
                """, (username, habit, selected_date, 1 if status else 0))
            conn.commit()
            st.success("Habits logged. Momentum building!", icon="🚀")
            st.balloons()
        
        # Analytics
        st.markdown("### Performance Analytics")
        # Mock data for charts
        dates = pd.date_range(end=date.today(), periods=14).tolist()
        completion = [65 + i*2 for i in range(14)]
        
        fig_line = px.line(
            x=dates, y=completion, 
            labels={"x": "Date", "y": "Completion %"},
            title="Habit Completion Trend"
        )
        fig_line.update_layout(template="plotly_dark", plot_bgcolor="#0f172a")
        st.plotly_chart(fig_line, use_container_width=True)
        
        col_g1, col_g2, col_g3 = st.columns(3)
        with col_g1:
            fig_g1 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=82,
                title={"text": "Today"},
                gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#8b5cf6"}}
            ))
            fig_g1.update_layout(template="plotly_dark")
            st.plotly_chart(fig_g1, use_container_width=True)
        
        cur.close()
        conn.close()
    
    # TAB 3: NUTRITION & WORKOUT
    with tabs[2]:
        st.subheader("Today's Plan")
        goal = "Fat Loss"  # fetch from DB in real impl
        day_name = date.today().strftime("%A")
        
        st.info(f"**{day_name}** — {goal} Focus")
        
        if st.button("✅ Mark Diet & Workout Complete"):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO diet_workout_logs (username, log_date, diet_completed, workout_completed)
                VALUES (%s, CURRENT_DATE, 1, 1)
                ON CONFLICT (username, log_date) DO UPDATE 
                SET diet_completed = 1, workout_completed = 1
            """, (username,))
            conn.commit()
            cur.close()
            conn.close()
            st.success("Day logged. Keep the fire alive!")
    
    # TAB 4: WEIGHT TRACKER
    with tabs[3]:
        st.subheader("Biometrics")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            new_weight = st.number_input("Current Weight (kg)", 30.0, 200.0, 72.0, step=0.1)
            if st.button("Log Weight"):
                bmi = calculate_bmi(new_weight, 172)  # demo height
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO weight_tracker (username, weight, bmi, log_date)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                """, (username, new_weight, bmi))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"Logged. BMI: {bmi}")
        
        with col_w2:
            # Mock trend
            fig_weight = go.Figure()
            fig_weight.add_trace(go.Scatter(
                x=pd.date_range(end=date.today(), periods=10),
                y=[74, 73.5, 73, 72.8, 72.5, 72.2, 72.0, 71.8, new_weight, new_weight-0.3],
                mode="lines+markers"
            ))
            fig_weight.update_layout(template="plotly_dark", title="Weight Trend")
            st.plotly_chart(fig_weight, use_container_width=True)
    
    # TAB 5: SETTINGS
    with tabs[4]:
        st.subheader("Customize Habits")
        new_habit = st.text_input("Add New Habit")
        if st.button("Add Habit"):
            if new_habit:
                conn = get_db_connection()
                cur = conn.cursor()
                try:
                    cur.execute("INSERT INTO habits (username, habit_name) VALUES (%s, %s)", 
                               (username, new_habit))
                    conn.commit()
                    st.success("Habit added")
                except:
                    st.warning("Habit already exists")
                cur.close()
                conn.close()
        
        if username.strip().lower() == "najam":
            st.markdown("### 🛠️ Admin Control Center")
            st.warning("Full DB visibility & management")
            # In production would show tables but omitted for brevity and safety

if __name__ == "__main__":
    main()
