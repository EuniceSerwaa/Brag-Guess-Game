import streamlit as st
import random
import pandas as pd
import time
import os

st.set_page_config(page_title="Brag & Guess – Ultimate Edition", layout="centered")

# ---------------- CSS ----------------
st.markdown("""
<style>
.glow {
    font-size: 30px;
    font-weight: bold;
    color: white;
    text-align: center;
    animation: glow 1.5s ease-in-out infinite alternate;
}
@keyframes glow {
    from { text-shadow: 0 0 10px #00ffcc; }
    to { text-shadow: 0 0 35px #ff00ff; }
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

st.title("🎯 Brag & Guess – Ultimate Edition ✨")
st.write("Brag about your skills. Race the clock. Get humbled 😏")

# ---------------- LEADERBOARD ----------------
LEADERBOARD_FILE = "leaderboard.csv"

if not os.path.exists(LEADERBOARD_FILE):
    pd.DataFrame(
        columns=["Nickname", "Level", "Attempts", "Time(s)"]
    ).to_csv(LEADERBOARD_FILE, index=False)

# ---------------- SESSION STATE ----------------
if "started" not in st.session_state:
    st.session_state.started = False

# ---------------- PLAYER SETUP ----------------
st.subheader("👤 Player Setup")

nickname = st.text_input("Enter your nickname")

level = st.selectbox(
    "Choose Difficulty",
    ["🟢 Easy", "🟡 Medium", "🔴 Hard"]
)

brag = st.selectbox(
    "How many attempts will you win in? 😎",
    ["1 attempt", "2 attempts", "3 attempts"]
)

brag_map = {
    "1 attempt": 1,
    "2 attempts": 2,
    "3 attempts": 3
}

level_config = {
    "🟢 Easy": {"max": 20, "attempts": 3, "time": 15},
    "🟡 Medium": {"max": 50, "attempts": 2, "time": 10},
    "🔴 Hard": {"max": 100, "attempts": 1, "time": 5},
}

if st.button("Start Game 🚀"):
    if nickname.strip() == "":
        st.warning("Nickname is required.")
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
        st.session_state.level = level
        st.session_state.brag_attempts = brag_map[brag]

        st.success(
            f"{level} | Range: 1–{config['max']} | "
            f"Allowed attempts: {config['attempts']} | "
            f"You bragged: {st.session_state.brag_attempts} attempt(s)"
        )

# ---------------- GAME PLAY ----------------
if st.session_state.started and not st.session_state.game_over:

    remaining_time = int(
        st.session_state.time_limit - (time.time() - st.session_state.turn_start)
    )

    st.write(f"⏳ Time left: **{max(0, remaining_time)} seconds**")

    # ⏰ TIME UP = INSTANT LOSS
    if remaining_time <= 0:
        st.markdown(
            "<div class='shake'>⏰ TIME UP! GAME OVER 😢</div>",
            unsafe_allow_html=True
        )

        st.write(
            f"😂 You bragged about winning in "
            f"{st.session_state.brag_attempts} attempt(s)… and time beat you."
        )

        pd.DataFrame([{
            "Nickname": st.session_state.nickname,
            "Level": st.session_state.level,
            "Attempts": "Timed Out ⏰",
            "Time(s)": "-"
        }]).to_csv(
            LEADERBOARD_FILE, mode="a", header=False, index=False
        )

        st.session_state.game_over = True

    if not st.session_state.game_over:
        guess = st.number_input(
            "Enter your guess",
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
                total_time = round(time.time() - st.session_state.start_time, 2)

                st.markdown(
                    f"<div class='glow'>✨ {nickname} WON! ✨</div>",
                    unsafe_allow_html=True
                )
                st.balloons()

                # 🎭 BRAG CHECK
                if st.session_state.attempts <= st.session_state.brag_attempts:
                    st.write("😎 You backed up your brag!")
                else:
                    st.write(
                        f"😂 You bragged about "
                        f"{st.session_state.brag_attempts} attempt(s)… "
                        f"but needed {st.session_state.attempts}!"
                    )

                pd.DataFrame([{
                    "Nickname": nickname,
                    "Level": level,
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
                    f"😂 You bragged about winning in "
                    f"{st.session_state.brag_attempts} attempt(s)… bold move."
                )

                pd.DataFrame([{
                    "Nickname": nickname,
                    "Level": level,
                    "Attempts": "Failed",
                    "Time(s)": "-"
                }]).to_csv(
                    LEADERBOARD_FILE, mode="a", header=False, index=False
                )

                st.session_state.game_over = True

# ---------------- LEADERBOARD ----------------
st.subheader("🏆 Leaderboard")

df = pd.read_csv(LEADERBOARD_FILE)

df["RankScore"] = df["Attempts"].apply(
    lambda x: 99 if isinstance(x, str) else int(x)
)

df = df.sort_values(by=["Level", "RankScore", "Time(s)"], ascending=True)
df["Position"] = range(1, len(df) + 1)

st.dataframe(
    df[["Position", "Nickname", "Level", "Attempts", "Time(s)"]],
    use_container_width=True
)

# ---------------- RESTART ----------------
if st.session_state.started:
    if st.button("Restart Game 🔄"):
        st.session_state.started = False
