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
body {
    background-color: #0f172a;
    color: #e5e7eb;
}

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

# ---------------- LEADERBOARD FILE ----------------
LEADERBOARD_FILE = "leaderboard.csv"

if not os.path.exists(LEADERBOARD_FILE):
    pd.DataFrame(
        columns=["Player", "Level", "Attempts", "Time(s)"]
    ).to_csv(LEADERBOARD_FILE, index=False)

# ---------------- SESSION STATE ----------------
if "started" not in st.session_state:
    st.session_state.started = False

# ---------------- LANDING ----------------
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
    avatar = st.selectbox("Choose your avatar", ["😎", "🔥", "🎯", "👑", "🐉", "🧠"])

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

brag_map = {
    "1 attempt": 1,
    "2 attempts": 2,
    "3 attempts": 3,
}

# ---------------- START GAME ----------------
if st.button("Start Game 🚀"):
    if nickname.strip() == "":
        st.warning("Please enter a nickname.")
    else:
        config = level_config[level]
        st.session_state.max_num = config["max"]
        st.session_state.allowed_attempts = config["attempts"]
        st.session_state.time_limit = config["time"]
        st.session_state.number = random.randint(1, config["max"])
        st.session_state.attempts = 0
        st.session_state.start_time = time.time()
        st.session_state.turn_start = time.time()
        st.session_state.game_over = False
        st.session_state.started = True
        st.session_state.nickname = nickname
        st.session_state.avatar = avatar
        st.session_state.level = level
        st.session_state.brag_attempts = brag_map[brag]

        st.success(
            f"{level} | Range 1–{config['max']} | "
            f"{config['attempts']} attempts | "
            f"{config['time']}s per attempt"
        )

# ---------------- GAME PLAY ----------------
if st.session_state.started and not st.session_state.game_over:

    remaining_time = int(
        st.session_state.time_limit - (time.time() - st.session_state.turn_start)
    )

    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.subheader("🎮 Game On")
        st.write(f"⏳ Time left: **{max(0, remaining_time)} seconds**")
        st.write(
            f"Attempts used: {st.session_state.attempts} / "
            f"{st.session_state.allowed_attempts}"
        )

        if remaining_time <= 0:
            st.markdown(
                "<div class='shake'>⏰ TIME UP! GAME OVER 😢</div>",
                unsafe_allow_html=True
            )

            st.write(
                f"😂 You bragged about "
                f"{st.session_state.brag_attempts} attempt(s)… bold."
            )

            pd.DataFrame([{
                "Player": f"{st.session_state.avatar} {st.session_state.nickname}",
                "Level": st.session_state.level,
                "Attempts": "Timed Out ⏰",
                "Time(s)": "-"
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
                        f"<div class='glow'>✨ {nickname} WON! ✨</div>",
                        unsafe_allow_html=True
                    )
                    st.balloons()

                    if st.session_state.attempts <= st.session_state.brag_attempts:
                        st.success("😎 You backed up your brag!")
                    else:
                        st.warning(
                            f"😂 You said "
                            f"{st.session_state.brag_attempts} attempt(s)… "
                            f"but needed {st.session_state.attempts}."
                        )

                    pd.DataFrame([{
                        "Player": f"{st.session_state.avatar} {nickname}",
                        "Level": level,
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
                        "<div class='shake'>😢 No attempts left. GAME OVER!</div>",
                        unsafe_allow_html=True
                    )

                    st.write(
                        f"😂 You bragged about "
                        f"{st.session_state.brag_attempts} attempt(s)… interesting."
                    )

                    pd.DataFrame([{
                        "Player": f"{st.session_state.avatar} {nickname}",
                        "Level": level,
                        "Attempts": "Failed",
                        "Time(s)": "-"
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

    # --- Rank Logic ---
    def rank_score(row):
        if row["Result"].startswith("Won"):
            return 0
        elif row["Result"].startswith("Timed"):
            return 1
        else:
            return 2

    df["ResultRank"] = df.apply(rank_score, axis=1)

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

