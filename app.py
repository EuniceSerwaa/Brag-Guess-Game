import streamlit as st
import random
import pandas as pd
import time
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Brag & Guess",
    page_icon="🎯",
    layout="centered"
)

# ---------------- STYLES ----------------
st.markdown("""
<style>
body { background-color: #0f172a; color: #e5e7eb; }

.card {
    background: #020617;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 0 30px rgba(56,189,248,0.15);
    margin-bottom: 25px;
}

.title {
    font-size: 42px;
    font-weight: 800;
    text-align: center;
    color: #38bdf8;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

.glow {
    font-size: 34px;
    font-weight: bold;
    color: #22d3ee;
    text-align: center;
    animation: glow 1.5s ease-in-out infinite alternate;
}

@keyframes glow {
    from { text-shadow: 0 0 10px #22d3ee; }
    to { text-shadow: 0 0 35px #9333ea; }
}

.shake {
    font-size: 22px;
    animation: shake 0.5s infinite;
}

@keyframes shake {
    0% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    50% { transform: translateX(5px); }
    75% { transform: translateX(-5px); }
    100% { transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)

# ---------------- LEADERBOARD ----------------
LEADERBOARD_FILE = "leaderboard.csv"
LEADERBOARD_COLUMNS = ["Player", "Level", "Result", "Attempts", "Time(s)"]

if not os.path.exists(LEADERBOARD_FILE):
    pd.DataFrame(columns=LEADERBOARD_COLUMNS).to_csv(
        LEADERBOARD_FILE, index=False
    )

# ---------------- SESSION STATE ----------------
if "started" not in st.session_state:
    st.session_state.started = False

# ---------------- TITLE ----------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='title'>🎯 Brag & Guess</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Brag big. Guess smart. Get humbled 😏</div>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- PLAYER SETUP ----------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.subheader("👤 Player Setup")

    nickname = st.text_input("Nickname")
    avatar = st.selectbox("Avatar", ["😎", "🔥", "🎯", "👑", "🐉", "🧠"])

    level = st.selectbox(
        "Difficulty",
        ["🟢 Easy", "🟡 Medium", "🔴 Hard"]
    )

    brag = st.selectbox(
        "How many attempts will you win in? 😏",
        ["1 attempt", "2 attempts", "3 attempts"]
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- GAME CONFIG ----------------
level_config = {
    "🟢 Easy": {"max": 20, "attempts": 6, "time": 20},
    "🟡 Medium": {"max": 50, "attempts": 4, "time": 15},
    "🔴 Hard": {"max": 100, "attempts": 3, "time": 10},
}

brag_map = {"1 attempt": 1, "2 attempts": 2, "3 attempts": 3}

# ---------------- START GAME ----------------
if st.button("Start Game 🚀"):
    if nickname.strip() == "":
        st.warning("Please enter a nickname.")
    else:
        cfg = level_config[level]
        st.session_state.number = random.randint(1, cfg["max"])
        st.session_state.allowed_attempts = cfg["attempts"]
        st.session_state.time_limit = cfg["time"]
        st.session_state.attempts = 0
        st.session_state.start_time = time.time()
        st.session_state.turn_start = time.time()
        st.session_state.started = True
        st.session_state.game_over = False
        st.session_state.player = f"{avatar} {nickname}"
        st.session_state.level = level
        st.session_state.brag = brag_map[brag]
        st.session_state.max_num = cfg["max"]

        st.success(
            f"{level} | Range 1–{cfg['max']} | "
            f"{cfg['attempts']} attempts | "
            f"{cfg['time']}s per attempt"
        )

# ---------------- GAME PLAY ----------------
if st.session_state.started and not st.session_state.game_over:

    remaining_time = int(
        st.session_state.time_limit - (time.time() - st.session_state.turn_start)
    )

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.subheader("🎮 Game On")
        st.write(f"⏳ Time left: **{max(0, remaining_time)}s**")
        st.write(
            f"Attempts: {st.session_state.attempts} / "
            f"{st.session_state.allowed_attempts}"
        )

        if remaining_time <= 0:
            st.markdown(
                "<div class='shake'>⏰ TIME UP! GAME OVER 😢</div>",
                unsafe_allow_html=True
            )

            pd.DataFrame([{
                "Player": st.session_state.player,
                "Level": st.session_state.level,
                "Result": "Timed Out ⏰",
                "Attempts": st.session_state.attempts,
                "Time(s)": None
            }]).to_csv(
                LEADERBOARD_FILE, mode="a", header=False, index=False
            )

            st.session_state.game_over = True

        if not st.session_state.game_over:
            guess = st.number_input(
                "Your guess",
                min_value=1,
                max_value=st.session_state.max_num,
                step=1
            )

            if st.button("Submit Guess 🎯"):
                st.session_state.attempts += 1
                st.session_state.turn_start = time.time()

                if guess < st.session_state.number:
                    st.warning("Too low 👇")
                elif guess > st.session_state.number:
                    st.warning("Too high 👆")
                else:
                    total_time = round(
                        time.time() - st.session_state.start_time, 2
                    )

                    st.markdown(
                        "<div class='glow'>✨ YOU WON! ✨</div>",
                        unsafe_allow_html=True
                    )
                    st.balloons()

                    if st.session_state.attempts > st.session_state.brag:
                        st.warning(
                            f"😂 You bragged {st.session_state.brag} attempt(s)… "
                            f"but needed {st.session_state.attempts}."
                        )

                    pd.DataFrame([{
                        "Player": st.session_state.player,
                        "Level": st.session_state.level,
                        "Result": "Won 🏆",
                        "Attempts": st.session_state.attempts,
                        "Time(s)": total_time
                    }]).to_csv(
                        LEADERBOARD_FILE, mode="a", header=False, index=False
                    )

                    st.session_state.game_over = True

                if (
                    st.session_state.attempts >= st.session_state.allowed_attempts
                    and not st.session_state.game_over
                ):
                    st.markdown(
                        "<div class='shake'>😢 No attempts left!</div>",
                        unsafe_allow_html=True
                    )

                    pd.DataFrame([{
                        "Player": st.session_state.player,
                        "Level": st.session_state.level,
                        "Result": "Failed ❌",
                        "Attempts": st.session_state.attempts,
                        "Time(s)": None
                    }]).to_csv(
                        LEADERBOARD_FILE, mode="a", header=False, index=False
                    )

                    st.session_state.game_over = True

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- LEADERBOARD ----------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏆 Leaderboard")

    df = pd.read_csv(LEADERBOARD_FILE)

    # Ensure correct types
    df["Result"] = df["Result"].astype(str)
    df["Attempts"] = pd.to_numeric(df["Attempts"], errors="coerce")
    df["Time(s)"] = pd.to_numeric(df["Time(s)"], errors="coerce")

    # Ranking logic (NO apply)
    df["ResultRank"] = 2
    df.loc[df["Result"].str.startswith("Won"), "ResultRank"] = 0
    df.loc[df["Result"].str.startswith("Timed"), "ResultRank"] = 1

    df["TimeRank"] = df["Time(s)"].fillna(9999)
    df["AttemptRank"] = df["Attempts"].fillna(99)

    df = df.sort_values(
        by=["ResultRank", "TimeRank", "AttemptRank"],
        ascending=True
    ).reset_index(drop=True)

    df["Position"] = df.index + 1

    st.dataframe(
        df[["Position", "Player", "Level", "Result", "Attempts", "Time(s)"]],
        use_container_width=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RESTART ----------------
if st.session_state.started:
    if st.button("Restart Game 🔄"):
        st.session_state.started = False
