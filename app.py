import streamlit as st
import random
import time
from pathlib import Path

st.set_page_config(layout="wide", initial_sidebar_state="expanded", )


def render_game_log():
    st.subheader("Last Round")
    log_container = st.container(height=350)
    if st.session_state.game_log:
        for msg in st.session_state.game_log:
            log_container.markdown(f'<div style="color: inherit; margin: 0.25rem 0; padding: 0.25rem; border-left: 3px solid #4CAF50; padding-left: 0.75rem; background-color: rgba(76, 175, 80, 0.05);">{msg}</div>', unsafe_allow_html=True)
    else:
        log_container.markdown('<div style="color: inherit; font-style: italic;">Battle begins...</div>', unsafe_allow_html=True)



PLAYER_INITIAL_STATS = {
    "level": 1,
    "hp": 100,
    "max_hp": 100,
    "xp": 0,
    "xp_to_next_level": 50,
    "attack": 5,
    "accuracy": 60,
    "speed": 5,
    "intelligence": 5,
    "stat_points": 0
}

ENEMY_BASE_STATS = {
    "name": "Goblin",
    "hp": 30,
    "max_hp": 30,
    "attack": 8,
    "accuracy": 50,
    "speed": 3,
    "xp_reward": 25
}

ENEMIES_LIST = [
    {"name": "Goblin Grunt",
     "image": "images/goblin.png"},
    {"name": "Orc Bruiser",
     "image": "images/orc.png"},
    {"name": "Stone Golem",
     "image": "images/golem.png"},
    {"name": "Shadow Stalker",
     "image": "images/shadow.png"},
    {"name": "Dungeon Troll",
     "image": "images/troll.png"},
    {"name": "Arcane Horror",
     "image": "images/horror.png"}
]

RPS_OPTIONS = ["Rock", "Paper", "Scissors"]
RPS_EMOJIS = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}


RPS_STAT_BONUSES = [
    {"type": "attack", "amount": 1, "message": "⚔️ Your victory sharpens your blade! +2 Attack"},
    {"type": "accuracy", "amount": 1, "message": "🎯 Your focus improves! +5% Accuracy"},
    {"type": "speed", "amount": 1, "message": "💨 You feel more agile! +1 Speed"},
    {"type": "intelligence", "amount": 1, "message": "🧠 Your tactical thinking improves! +1 Intelligence"},
    {"type": "max_hp", "amount": 2, "message": "❤️ Your confidence boosts your vitality! +10 Max HP"}
]
GRADE_THRESHOLDS = {
    "F": {"min_level": 1, "max_level": 1, "color": "#ff4444", "description": "Novice Explorer"},
    "E": {"min_level": 2, "max_level": 3, "color": "#ff6666", "description": "Dungeon Newcomer"},
    "D": {"min_level": 4, "max_level": 5, "color": "#ff8800", "description": "Dungeon Crawler"},
    "C": {"min_level": 6, "max_level": 7, "color": "#ffcc00", "description": "Skilled Adventurer"},
    "B": {"min_level": 8, "max_level": 9, "color": "#88cc00", "description": "Veteran Warrior"},
    "A": {"min_level": 10, "max_level": float('inf'), "color": "#44aa44", "description": "Elite Champion"}
}


def get_current_grade(dungeon_level):
    for grade, threshold in GRADE_THRESHOLDS.items():
        if threshold["min_level"] <= dungeon_level <= threshold["max_level"]:
            return grade, threshold
    return "F", GRADE_THRESHOLDS["F"]


def get_next_grade_info(current_grade):
    grade_order = ["F", "E", "D", "C", "B", "A"]
    current_index = grade_order.index(current_grade)

    if current_index < len(grade_order) - 1:
        next_grade = grade_order[current_index + 1]
        return next_grade, GRADE_THRESHOLDS[next_grade]
    return None, None


def render_grade_ladder():
    current_level = st.session_state.dungeon_level
    current_grade, current_info = get_current_grade(current_level)
    next_grade, next_info = get_next_grade_info(current_grade)

    st.subheader("🏆 Achievement Ladder")

    ladder_container = st.container()

    with ladder_container:
        grade_order = ["A", "B", "C", "D", "E", "F"]

        for grade in grade_order:
            grade_info = GRADE_THRESHOLDS[grade]
            is_current = (grade == current_grade)
            is_achieved = current_level >= grade_info["min_level"]


            if is_current:
                grade_html = f"""
                <div style="
                    background: linear-gradient(90deg, {grade_info['color']}, {grade_info['color']}88);
                    border: 3px solid {grade_info['color']};
                    border-radius: 12px;
                    padding: 12px;
                    margin: 8px 0;
                    color: white;
                    font-weight: bold;
                    font-size: 1.2rem;
                    text-align: center;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    animation: pulse 2s infinite;
                ">
                    🎖️ Grade {grade} - {grade_info['description']}<br>
                    <small style="font-size: 0.9rem;">Level {grade_info['min_level']}-{grade_info['max_level'] if grade_info['max_level'] != float('inf') else '∞'} | Current: Level {current_level}</small>
                </div>
                """
            elif is_achieved:
                grade_html = f"""
                <div style="
                    background: linear-gradient(90deg, #666, #888);
                    border: 2px solid #555;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px 0;
                    color: #ccc;
                    font-size: 1rem;
                    text-align: center;
                    opacity: 0.7;
                ">
                    ✅ Grade {grade} - {grade_info['description']}<br>
                    <small>Level {grade_info['min_level']}-{grade_info['max_level'] if grade_info['max_level'] != float('inf') else '∞'} - COMPLETED</small>
                </div>
                """
            else:
                grade_html = f"""
                <div style="
                    background: #333;
                    border: 2px dashed #666;
                    border-radius: 8px;
                    padding: 8px;
                    margin: 4px 0;
                    color: #888;
                    font-size: 1rem;
                    text-align: center;
                    opacity: 0.5;
                ">
                    🔒 Grade {grade} - {grade_info['description']}<br>
                    <small>Requires Level {grade_info['min_level']}</small>
                </div>
                """

            st.markdown(grade_html, unsafe_allow_html=True)

        if next_grade and next_info:
            levels_needed = next_info["min_level"] - current_level
        else:
            st.success("🌟 **Congratulations!** You've achieved the highest grade possible!")


def generate_rps_problem():
    enemy_choice = random.choice(RPS_OPTIONS)

    st.session_state.question_start_time = time.time()
    st.session_state.time_out_attack_done = False

    return {
        "type": "rps",
        "enemy_choice": enemy_choice,
        "question": "Choose your move in this battle of wits!"
    }


def handle_rps_turn(player_choice):
    if st.session_state.get('question_start_time'):
        time_taken = time.time() - st.session_state.question_start_time
        time_limit = get_answer_time_limit()

        if time_taken > time_limit:
            log_message("⏰ Too slow! The enemy takes advantage of your hesitation!")
            enemy_attack()
            commit_round_log()
            if st.session_state.current_enemy:
                st.session_state.current_problem = generate_problem()
            st.rerun()
            return

    problem = st.session_state.current_problem
    enemy_choice = problem["enemy_choice"]

    log_message(f"You chose: {RPS_EMOJIS[player_choice]} **{player_choice}**")
    log_message(f"Enemy chose: {RPS_EMOJIS[enemy_choice]} **{enemy_choice}**")

    result = determine_rps_winner(player_choice, enemy_choice)

    if result == "win":
        log_message("🎉 **You WIN the battle of wits!**")

        player = st.session_state.player
        enemy = st.session_state.current_enemy

        if random.randint(1, 100) <= player['accuracy']:
            base_damage = player['attack'] + random.randint(player['level'], player['level'] * 3)
            enemy['hp'] = max(0, enemy['hp'] - base_damage)
            log_message(f"✅⚔️ Your strategic victory leads to a devastating attack for **{base_damage} damage**!")
        else:
            log_message("Your attack missed despite your tactical advantage!")

        bonus = random.choice(RPS_STAT_BONUSES)
        apply_rps_bonus(bonus)
        log_message(bonus["message"])
        st.session_state.battle_summary["bonuses"].append(bonus["message"])

        if enemy['hp'] <= 0:
            handle_victory()

    elif result == "lose":
        log_message("😤 **The enemy outsmarts you!**")

        enemy_attack()

    else:
        log_message("🤝 **It's a tie!** Both fighters circle each other warily...")
        log_message("No one gains an advantage this round.")

    commit_round_log()

    if st.session_state.current_enemy:
        st.session_state.current_problem = generate_problem()
    st.rerun()


def determine_rps_winner(player_choice, enemy_choice):
    if player_choice == enemy_choice:
        return "tie"

    winning_combinations = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper"
    }

    if winning_combinations[player_choice] == enemy_choice:
        return "win"
    else:
        return "lose"


def apply_rps_bonus(bonus):
    player = st.session_state.player

    if bonus["type"] == "attack":
        player["attack"] += bonus["amount"]
    elif bonus["type"] == "accuracy":
        player["accuracy"] += bonus["amount"]
    elif bonus["type"] == "speed":
        player["speed"] += bonus["amount"]
    elif bonus["type"] == "intelligence":
        player["intelligence"] += bonus["amount"]
    elif bonus["type"] == "max_hp":
        player["max_hp"] += bonus["amount"]
        player["hp"] += bonus["amount"]






from questions import *
from numerical_questions import *


BASE_ANSWER_TIME_LIMIT = 15.0


def get_answer_time_limit():
    intelligence = st.session_state.player.get('intelligence', 5)
    return BASE_ANSWER_TIME_LIMIT + (intelligence - 5)

def apply_custom_styling():
    st.markdown("""
        <style>
            .stApp {
                font-size: 1.1rem;
            }
            h1 {
                font-size: 2.75rem !important;
            }
            h2, h3 {
                font-size: 2rem !important;
            }
            .stButton>button {
                font-size: 1.1rem;
                padding: 0.75em 1em;
            }
            .stProgress > div > div > div > div {
                height: 1.5rem;
            }
            .stRadio [role="radiogroup"] {
                align-items: center;
                justify-content: center;
            }
            .math-question {
                font-size: 1.75rem !important;
                font-weight: bold;
                text-align: center;
                padding: 1rem;
            }
            .math-question code {
                font-size: 2rem !important;
                color: #ff4b4b;
            }
            .mcq-question {
                font-size: 1.5rem !important;
                font-weight: bold;
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #1f4e79, #2e86ab);
                color: white;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            .mcq-option {
                font-size: 1.3rem !important;
                font-weight: 500;
                padding: 0.8rem;
                margin: 0.3rem;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .mcq-option:hover {
                border-color: #007bff;
                background-color: #e3f2fd;
            }
            .stRadio > div {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 0.5rem !important;
            }
            .stRadio [role="radiogroup"] {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 0.5rem !important;
            }

            /* Fixed styling for dark mode compatibility */
            .stRadio [role="radiogroup"] > label {
                margin: 0 !important;
                display: flex !important;
                align-items: center !important;
                font-size: 1.3rem !important;
                font-weight: 500 !important;
                padding: 0.8rem !important;
                border: 2px solid var(--border-color, #ddd) !important;
                border-radius: 8px !important;
                background-color: var(--bg-color, rgba(255, 255, 255, 0.05)) !important;
                color: var(--text-color, inherit) !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
            }

            /* Light mode specific */
            [data-theme="light"] .stRadio [role="radiogroup"] > label {
                --border-color: #ddd;
                --bg-color: #f8f9fa;
                --text-color: #333;
            }

            /* Dark mode specific */  
            [data-theme="dark"] .stRadio [role="radiogroup"] > label,
            .stApp[data-theme="dark"] .stRadio [role="radiogroup"] > label {
                --border-color: #555;
                --bg-color: rgba(255, 255, 255, 0.1);
                --text-color: #fff;
            }

            /* Fallback for dark mode detection */
            @media (prefers-color-scheme: dark) {
                .stRadio [role="radiogroup"] > label {
                    border-color: #555 !important;
                    background-color: rgba(255, 255, 255, 0.1) !important;
                    color: #fff !important;
                }
            }

            .stRadio [role="radiogroup"] > label:hover {
                border-color: #007bff !important;
                background-color: rgba(0, 123, 255, 0.2) !important;
            }

            .stRadio [role="radiogroup"] > label > div {
                font-size: 1.3rem !important;
                margin-left: 0.5rem !important;
                color: inherit !important;
            }

            /* Ensure radio button itself is visible */
            .stRadio [role="radiogroup"] > label input[type="radio"] {
                accent-color: #007bff !important;
            }

            .time-warning {
                color: #ff4444 !important;
                font-weight: bold;
                animation: pulse 1s infinite;
            }
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            .rps-question {
                font-size: 1.5rem !important;
                font-weight: bold;
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #8e44ad, #e74c3c);
                color: white;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            .rps-option {
                font-size: 3rem !important;
                text-align: center;
                padding: 1rem;
                margin: 0.5rem;
                border: 3px solid #ddd;
                border-radius: 15px;
                background-color: #f8f9fa;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .rps-option:hover {
                border-color: #e74c3c;
                background-color: #ffeaa7;
                transform: scale(1.05);
            }

            /* Grade ladder animation */
            @keyframes pulse {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.8; transform: scale(1.02); }
                100% { opacity: 1; transform: scale(1); }
            }

        </style>
    """, unsafe_allow_html=True)


def init_game():
    if "player" not in st.session_state:
        st.session_state.player = PLAYER_INITIAL_STATS.copy()
        st.session_state.current_enemy = None
        st.session_state.game_log = []
        st.session_state.current_round_log = []
        st.session_state.dungeon_level = 1
        st.session_state.question_start_time = None
        st.session_state.battle_summary = {}
        st.session_state.game_over = False
        st.session_state.auto_refresh_placeholder = None

    if st.session_state.current_enemy is None and not st.session_state.battle_summary and not st.session_state.game_over:
        generate_enemy()


def reset_game_state():
    st.session_state.player = PLAYER_INITIAL_STATS.copy()
    st.session_state.current_enemy = None
    st.session_state.game_log = []
    st.session_state.current_round_log = []
    st.session_state.dungeon_level = 1
    st.session_state.question_start_time = None
    st.session_state.battle_summary = {}
    st.session_state.game_over = False
    st.session_state.auto_refresh_placeholder = None
    generate_enemy()


def generate_enemy():
    enemy_multiplier = 0.65
    level = st.session_state.dungeon_level

    selected_enemy_data = random.choice(ENEMIES_LIST)

    st.session_state.current_enemy = {
        "name": f"{selected_enemy_data['name']} (Lvl {level})",
        "image_path": selected_enemy_data['image'],
        "hp": round(ENEMY_BASE_STATS["hp"] * level * enemy_multiplier, 1),
        "max_hp": round(ENEMY_BASE_STATS["hp"] * level * enemy_multiplier, 1),
        "attack": round(ENEMY_BASE_STATS["attack"] * level * enemy_multiplier, 1),
        "accuracy": round(ENEMY_BASE_STATS["accuracy"] + level * enemy_multiplier, 1),
        "speed": round(ENEMY_BASE_STATS["speed"] + (level // 2) * enemy_multiplier, 1),
        "xp_reward": ENEMY_BASE_STATS["xp_reward"] * level
    }
    st.session_state.battle_summary = {"damage_taken": 0, "bonuses": []}
    st.session_state.current_problem = generate_problem()
    st.session_state.current_round_log = []
    log_message(f"A wild **{st.session_state.current_enemy['name']}** appears!")





def generate_problem():
    rand = random.random()
    if rand < 0.25:  # 25% math problems
        return generate_math_problem()
    elif rand < 0.50:  # 15% numerical questions
        return generate_numerical_question()
    elif rand < 0.75:  # 20% rock paper scissors
        return generate_rps_problem()
    else:  # 40% multiple choice questions
        return generate_multiple_choice_question()


def generate_numerical_question():
    topic = random.choice(list(NUMERICAL_QUESTIONS.keys()))
    question_data = random.choice(NUMERICAL_QUESTIONS[topic])

    st.session_state.question_start_time = time.time()
    st.session_state.time_out_attack_done = False

    return {
        "type": "numerical",
        "topic": topic,
        "question": question_data["question"],
        "answer": question_data["answer"]
    }


def handle_numerical_turn(player_answer):
    problem = st.session_state.current_problem
    time_taken = time.time() - st.session_state.question_start_time
    is_correct = (player_answer == problem['answer'])

    bonus = calculate_time_bonus(time_taken)

    player_speed = st.session_state.player['speed']
    enemy_speed = st.session_state.current_enemy['speed']

    if is_correct:
        log_message("✅🛡️ **Perfect knowledge!** Your precise answer leaves the enemy stunned and unable to counterattack!")
        player_attack(is_correct, bonus, time_taken)
    else:
        log_message(f"❌ Wrong answer! The correct answer was **{problem['answer']}**.")
        if player_speed >= enemy_speed:
            player_attack(is_correct, bonus, time_taken)
            if st.session_state.current_enemy and st.session_state.current_enemy['hp'] > 0:
                enemy_attack()
        else:
            enemy_attack()
            if st.session_state.player['hp'] > 0:
                player_attack(is_correct, bonus, time_taken)

    commit_round_log()

    if st.session_state.current_enemy:
        st.session_state.current_problem = generate_problem()
    st.rerun()




def generate_math_problem():
    dungeon_level = st.session_state.dungeon_level

    question_str = ""
    answer = 0

    if dungeon_level < 5:
        operator = random.choice(['+', '-', '*'])
        level_scale = dungeon_level
        if operator == '+':
            a = random.randint(5 * level_scale, 20 * level_scale)
            b = random.randint(5 * level_scale, 20 * level_scale)
            answer = a + b
            question_str = f"{a} + {b}"
        elif operator == '-':
            a = random.randint(10 * level_scale, 30 * level_scale)
            b = random.randint(1 * level_scale, 10 * level_scale)
            answer = a - b
            question_str = f"{a} - {b}"
        else:
            a = random.randint(2, 5 + level_scale)
            b = random.randint(2, 5 + level_scale)
            answer = a * b
            question_str = f"{a} * {b}"

    elif dungeon_level < 10:
        level_scale = dungeon_level - 4
        a = random.randint(1 * level_scale, 5 * level_scale)
        b = random.randint(2 * level_scale, 6 * level_scale)
        c = random.randint(2, 5)

        question_str = f"{a} + {b} * {c}"
        answer = a + (b * c)

    else:
        level_scale = dungeon_level - 9
        a = random.randint(3 * level_scale, 7 * level_scale)
        b = random.randint(1 * level_scale, 5 * level_scale)
        c = random.randint(2, 7)
        op = random.choice(['+', '-'])

        if op == '+':
            question_str = f"({a} + {b}) * {c}"
            answer = (a + b) * c
        else:
            question_str = f"({a} - {b}) * {c}"
            answer = (a - b) * c

    st.session_state.question_start_time = time.time()
    st.session_state.time_out_attack_done = False

    return {
        "type": "math",
        "question": question_str,
        "answer": answer
    }


def generate_multiple_choice_question():
    topic = random.choice(list(QUESTION_TOPICS.keys()))
    question_data = random.choice(QUESTION_TOPICS[topic])

    st.session_state.question_start_time = time.time()
    st.session_state.time_out_attack_done = False

    return {
        "type": "multiple_choice",
        "topic": topic,
        "question": question_data["question"],
        "options": question_data["options"],
        "correct": question_data["correct"]
    }


def log_message(message):
    st.session_state.current_round_log.append(message)


def commit_round_log():
    if st.session_state.current_round_log:
        st.session_state.game_log = st.session_state.current_round_log.copy()
        st.session_state.current_round_log = []


def render_sidebar_stats():
    if "player" not in st.session_state: return
    player = st.session_state.player
    with st.sidebar:
        st.header("Your Hero")

        player_image_path = Path("images/player2.png")
        if player_image_path.is_file():
            st.image(str(player_image_path), caption=f"Level {player['level']} Adventurer")
        else:
            st.info(f"Image not found at {player_image_path}")
            st.caption("(Create 'images/player.png' to see your character)")

        st.write(f"**Level:** {player['level']}")
        st.write(f"**HP:**")
        st.progress(round(player['hp'], 1) / player['max_hp'], text=f"{round(player['hp'], 1)}/{player['max_hp']}")
        st.write(f"**XP:**")
        st.progress(player['xp'] / player['xp_to_next_level'], text=f"{player['xp']}/{player['xp_to_next_level']}")

        current_time_limit = get_answer_time_limit()

        st.info(
            f"⚔️ Attack: {player['attack']}\n\n🎯 Accuracy: {player['accuracy']}%\n\n💨 Speed: {player['speed']}\n\n🧠 Intelligence: {player['intelligence']} ({current_time_limit:.0f}s)")

        st.markdown("---")
        st.markdown("""
                **⚔️ Attack:** Increases your base attack damage

                **🎯 Accuracy:** Chance to hit enemies with your attacks

                **💨 Speed:** Determines who attacks first in combat

                **🧠 Intelligence:** Increases time available for answering questions
                """)


def render_enemy_display():
    enemy = st.session_state.current_enemy
    if not enemy:
        return

    img_col, stats_col = st.columns([1, 2])

    with img_col:
        st.image(enemy["image_path"])

    with stats_col:
        st.header(enemy['name'])
        st.write(f"**HP:**")
        st.progress(enemy['hp'] / enemy['max_hp'], text=f"{enemy['hp']}/{enemy['max_hp']}")
        st.info(f"⚔️ Attack: {enemy['attack']} | 🎯 Accuracy: {enemy['accuracy']}% | 💨 Speed: {enemy['speed']}")






def render_victory_screen():
    summary = st.session_state.battle_summary
    st.header("Victory!")
    st.balloons()

    st.subheader(f"You defeated the {summary.get('enemy_name', 'enemy')}!")

    st.success(f"**XP Gained:** {summary.get('xp_gain', 0)}")
    st.error(f"**Damage Taken:** {round(summary.get('damage_taken', 0), 1)}")

    bonuses = summary.get('bonuses', [])
    if bonuses:
        st.info("Time Bonuses Earned:")
        for b in bonuses:
            st.write(f"- {b}")

    st.divider()
    if st.button("Descend to the next level", use_container_width=True, type="primary"):
        st.session_state.dungeon_level += 1
        st.toast(f"Entering Dungeon Level {st.session_state.dungeon_level}...", icon="⚔️")
        generate_enemy()
        st.rerun()


def calculate_time_bonus(time_taken):
    time_limit = get_answer_time_limit()

    if time_taken > time_limit:
        return {"bonus_damage": 0, "heal_amount": 0, "message": "Too slow! Your hesitation makes you miss.",
                "time_out": True}

    if time_taken < 5.0:
        bonus_dmg = st.session_state.player['level'] * 2
        return {"bonus_damage": bonus_dmg, "heal_amount": 0,
                "message": f"⚡ Quick thinking! You deal **+{bonus_dmg} bonus damage**!", "time_out": False}

    if time_taken < 10.0:
        heal_amt = st.session_state.player['level'] * 3
        return {"bonus_damage": 0, "heal_amount": heal_amt,
                "message": f"🩹 Precise calculation! You **heal** for **{heal_amt} HP**.", "time_out": False}

    return {"bonus_damage": 0, "heal_amount": 0, "message": "", "time_out": False}


def player_attack(answer_correct, bonus, time_taken):
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    log_message(f"⏱️ Answer time: **{time_taken:.2f}s**")

    if bonus["time_out"] or not answer_correct:
        log_message(
            bonus["message"] if bonus["time_out"] else "❌ Your answer was wrong! ⚔️ Your attack misses completely.")
        return

    if bonus["message"]:
        log_message(bonus["message"])
        st.session_state.battle_summary["bonuses"].append(bonus["message"])

    if bonus["heal_amount"] > 0:
        player['hp'] = min(player['max_hp'], player['hp'] + bonus["heal_amount"])

    if random.randint(1, 100) <= player['accuracy']:
        base_damage = player['attack'] + random.randint(player['level'], player['level'] * 3)
        total_damage = base_damage + bonus["bonus_damage"]
        enemy['hp'] = max(0, enemy['hp'] - total_damage)
        log_message(f"✅ Correct! You strike for **{total_damage} damage**!")
    else:
        log_message("Your attack missed!")

    if enemy['hp'] <= 0:
        handle_victory()


def enemy_attack():
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    if random.randint(1, 100) <= enemy['accuracy']:
        damage = enemy['attack'] + random.randint(0, 3 * st.session_state.dungeon_level)
        player['hp'] = max(0, player['hp'] - damage)
        log_message(f"The {enemy['name']} **hits you** for **{damage}** damage!")
        st.session_state.battle_summary["damage_taken"] += damage
    else:
        log_message(f"The {enemy['name']}'s attack missed!")

    if player['hp'] <= 0:
        st.session_state.game_over = True
        log_message("You have been defeated... Game Over.")


def handle_victory():
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    log_message(f"You have defeated the **{enemy['name']}**!")

    xp_gain = enemy['xp_reward']
    player['xp'] += xp_gain
    log_message(f"You gained **{xp_gain} XP**!")

    st.session_state.battle_summary['enemy_name'] = enemy['name']
    st.session_state.battle_summary['xp_gain'] = xp_gain

    if player['xp'] >= player['xp_to_next_level']:
        player['level'] += 1
        player['xp'] -= player['xp_to_next_level']
        player['xp_to_next_level'] = int(player['xp_to_next_level'] * 1.5)
        player['stat_points'] += 3
        player['max_hp'] += 15
        player['hp'] = player['max_hp']
        log_message(f"🎉 LEVEL UP! You are now level **{player['level']}**!")
        log_message(f"You feel stronger and fully healed. You gained **3 stat points**!")

    st.session_state.current_enemy = None


def handle_math_turn(player_answer):
    problem = st.session_state.current_problem
    time_taken = time.time() - st.session_state.question_start_time
    is_correct = (player_answer == problem['answer'])

    bonus = calculate_time_bonus(time_taken)

    player_speed = st.session_state.player['speed']
    enemy_speed = st.session_state.current_enemy['speed']
    if not is_correct:
        log_message(f"❌ Wrong answer! The correct answer to **{problem['question']}** was **{problem['answer']}**.")

    if player_speed >= enemy_speed:
        player_attack(is_correct, bonus, time_taken)
        if st.session_state.current_enemy and st.session_state.current_enemy['hp'] > 0:
            enemy_attack()
    else:
        enemy_attack()
        if st.session_state.player['hp'] > 0:
            player_attack(is_correct, bonus, time_taken)

    commit_round_log()

    if st.session_state.current_enemy:
        st.session_state.current_problem = generate_problem()
    st.rerun()


def handle_mcq_turn(selected_option):
    problem = st.session_state.current_problem
    time_taken = time.time() - st.session_state.question_start_time
    is_correct = (selected_option == problem['correct'])

    bonus = calculate_time_bonus(time_taken)

    player_speed = st.session_state.player['speed']
    enemy_speed = st.session_state.current_enemy['speed']

    if not is_correct:
        correct_option_text = problem['options'][problem['correct']]
        correct_letter = chr(65 + problem['correct'])
        log_message(f"❌ Wrong answer! The correct answer was **{correct_letter}. {correct_option_text}**.")

    if player_speed >= enemy_speed:
        player_attack(is_correct, bonus, time_taken)
        if st.session_state.current_enemy and st.session_state.current_enemy['hp'] > 0:
            enemy_attack()
    else:
        enemy_attack()
        if st.session_state.player['hp'] > 0:
            player_attack(is_correct, bonus, time_taken)

    commit_round_log()

    if st.session_state.current_enemy:
        st.session_state.current_problem = generate_problem()
    st.rerun()


def render_level_up_screen():
    st.header("Level Up! Spend Your Stat Points")
    player = st.session_state.player
    st.write(f"You have **{player['stat_points']}** points to spend.")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("⚔️ Increase Attack (+1)", use_container_width=True, disabled=(player['stat_points'] == 0),
                     type='primary'):
            player['attack'] += 1
            player['stat_points'] -= 1
            st.rerun()
    with col2:
        if st.button("🎯 Increase Accuracy (+2%)", use_container_width=True, disabled=(player['stat_points'] == 0),
                     type='primary'):
            player['accuracy'] += 2
            player['stat_points'] -= 1
            st.rerun()
    with col3:
        if st.button("💨 Increase Speed (+1)", use_container_width=True, disabled=(player['stat_points'] == 0),
                     type='primary'):
            player['speed'] += 1
            player['stat_points'] -= 1
            st.rerun()
    with col4:
        if st.button("🧠 Increase Intelligence (+1)", use_container_width=True, disabled=(player['stat_points'] == 0),
                     type='primary'):
            player['intelligence'] += 1
            player['stat_points'] -= 1
            st.rerun()
    with col5:
        if st.button("❤️ Increase Max Health (+20)", use_container_width=True, disabled=(player['stat_points'] == 0),
                     type='primary'):
            player['max_hp'] += 20
            player['hp'] += 20
            player['stat_points'] -= 1
            st.rerun()

    if player['stat_points'] == 0:
        st.success("All points spent! You are ready for the next battle.")
        if st.session_state.current_enemy is None:
            generate_enemy()
        st.rerun()


def auto_refresh_timer():
    if st.session_state.question_start_time is None:
        return

    time_elapsed = time.time() - st.session_state.question_start_time
    time_limit = get_answer_time_limit()
    time_left = max(0, time_limit - time_elapsed)

    if time_left <= 0 and not st.session_state.get('time_out_attack_done', False):
        st.session_state.time_out_attack_done = True

        problem = st.session_state.current_problem

        log_message("⏰ Time's up! The enemy takes advantage of your hesitation!")

        if problem["type"] == "math":
            log_message(f"❌ The correct answer to **{problem['question']}** was **{problem['answer']}**.")
        elif problem["type"] == "multiple_choice":
            correct_option_text = problem['options'][problem['correct']]
            correct_letter = chr(65 + problem['correct'])
            log_message(f"❌ The correct answer was **{correct_letter}. {correct_option_text}**.")
        elif problem["type"] == "numerical":
            log_message(f"❌ The correct answer was **{problem['answer']}**.")
        elif problem["type"] == "rps":
            log_message(f"The enemy chose: {RPS_EMOJIS[problem['enemy_choice']]} **{problem['enemy_choice']}**")

        enemy_attack()
        commit_round_log()
        if not st.session_state.get("game_over"):
            st.session_state.current_problem = generate_problem()
        st.rerun()


def main():
    apply_custom_styling()
    init_game()

    if st.session_state.get("game_over"):
        st.title("⚔️ You Have Fallen ⚔️")
        st.error("## GAME OVER")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Your journey ends here.")
            st.write("The depths of Numeria have claimed another brave soul. But your legend will be remembered.")
            st.metric("Dungeon Level Reached", st.session_state.dungeon_level)

        with col2:
            st.subheader("Final Stats")
            player = st.session_state.player
            st.write(f"**Level:** {player['level']}")
            st.info(
                f"⚔️ Attack: {player['attack']} | 🎯 Accuracy: {player['accuracy']}% | 💨 Speed: {player['speed']} | 🧠 Intelligence: {player['intelligence']}")

        st.divider()
        st.subheader("A new adventure awaits...")
        if st.button("Restart Your Quest", use_container_width=True, type="primary"):
            reset_game_state()
            st.rerun()
        return

    render_sidebar_stats()

    if st.session_state.player['stat_points'] > 0:
        render_level_up_screen()
    elif st.session_state.current_enemy is None:
        render_victory_screen()
    else:
        question_col, enemy_col = st.columns([2, 1.5])

        with question_col:
            st.subheader(f"🏰 Dungeon Level: {st.session_state.dungeon_level}")
            st.divider()
            problem = st.session_state.current_problem
            if not hasattr(st.session_state, 'question_start_time') or st.session_state.question_start_time is None:
                return

            time_elapsed = time.time() - st.session_state.question_start_time
            time_limit = get_answer_time_limit()
            time_left = max(0, time_limit - time_elapsed)

            auto_refresh_timer()

            if time_left <= 5.0:
                st.markdown(f'<p class="time-warning">⏰ HURRY! {time_left:.1f}s remaining!</p>',
                            unsafe_allow_html=True)

            st.progress(time_left / time_limit, text=f"⌛ Time is ticking...")

            if problem["type"] == "math":
                st.markdown(f'<p class="math-question">Solve this:<br><code>{problem["question"]}</code></p>',
                            unsafe_allow_html=True)

                with st.form("attack_form", clear_on_submit=True):
                    user_answer = st.number_input("Your answer:", value=None, step=1, format="%d",
                                                  key="math_answer_input", label_visibility="collapsed",
                                                  placeholder="Type your answer...")
                    submitted = st.form_submit_button("Attack!", use_container_width=True, type="primary")
                    if submitted and user_answer is not None:
                        handle_math_turn(user_answer)

            elif problem["type"] == "multiple_choice":
                st.markdown(f'<div class="mcq-question">📚 {problem["question"]}</div>',
                            unsafe_allow_html=True)
                with st.form("mcq_form", clear_on_submit=True):
                    selected_option = st.radio(
                        "Choose your answer:",
                        options=range(len(problem["options"])),
                        format_func=lambda x: f"{chr(65 + x)}. {problem['options'][x]}",
                        key="mcq_answer_input",
                        label_visibility="collapsed"
                    )
                    submitted = st.form_submit_button("Attack!", use_container_width=True, type="primary")
                    if submitted:
                        handle_mcq_turn(selected_option)

            elif problem["type"] == "numerical":
                st.markdown(f'<div class="mcq-question">🔢 {problem["topic"]}<br>{problem["question"]}</div>',
                            unsafe_allow_html=True)

                with st.form("numerical_form", clear_on_submit=True):
                    user_answer = st.number_input("Your answer:", value=None, step=1, format="%d",
                                                  key="numerical_answer_input", label_visibility="collapsed",
                                                  placeholder="Enter the exact number...")
                    submitted = st.form_submit_button("Attack!", use_container_width=True, type="primary")
                    if submitted and user_answer is not None:
                        handle_numerical_turn(int(user_answer))

            elif problem["type"] == "rps":
                st.markdown(f'<div class="rps-question">🎯 Battle of Wits<br>{problem["question"]}</div>',
                            unsafe_allow_html=True)

                with st.form("rps_form", clear_on_submit=True):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        rock_button = st.form_submit_button(
                            f"{RPS_EMOJIS['Rock']}\nRock",
                            use_container_width=True,
                            type="secondary"
                        )
                    with col2:
                        paper_button = st.form_submit_button(
                            f"{RPS_EMOJIS['Paper']}\nPaper",
                            use_container_width=True,
                            type="secondary"
                        )
                    with col3:
                        scissors_button = st.form_submit_button(
                            f"{RPS_EMOJIS['Scissors']}\nScissors",
                            use_container_width=True,
                            type="secondary"
                        )

                    if rock_button:
                        handle_rps_turn("Rock")
                    elif paper_button:
                        handle_rps_turn("Paper")
                    elif scissors_button:
                        handle_rps_turn("Scissors")

        with enemy_col:
            st.divider()
            st.divider()
            render_enemy_display()


        log_col, grade_col = st.columns([2, 1])

        with log_col:
            render_game_log()

        with grade_col:
            render_grade_ladder()


if __name__ == "__main__":
    main()
