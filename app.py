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
    {"name": "Dr. Amorpho",
     "image": "images/dramorpho.png"},
    {"name": "Entropy",
     "image": "images/entropy.png"},
    {"name": "Dislocator",
     "image": "images/dislocator.png"},
    {"name": "MisInfomorph",
     "image": "images/misinfomorph.png"},
    {"name": "The Disorder",
     "image": "images/disorder.png"},
    {"name": "Vacancy Viper",
     "image": "images/viper.png"},
    {"name": "Glassy Ghoul",
     "image": "images/glassy_ghoul.png"},
    {"name": "Twinster",
     "image": "images/twinster.png"},
    {"name": "Phase Phantom",
     "image": "images/phase_phantom.png"}
    
    
]

ENEMY_SHOUTOUTS = {
    "Dr. Amorpho": [
        "Symmetry is so last century. Join the amorphous age!",
        "Crystals? Please! I prefer the freedom of the amorphous.",
        "Let’s smudge those pretty planes!",
        "You can’t orient what has no order!",
        "Who needs repeating units when you have imagination?",
        "I’ll melt your monoclinic dreams!",
        "Order is for cowards!",
        "They called me ‘non-crystalline’ in school. Look at me now!",
        "You can’t X-ray what won’t stay still"
    ],
    "Entropy": [
        "Heat me up, and I’ll tear your crystals apart!",
        "Order is an illusion... I am inevitable!",
        "Why build structure when you can watch it crumble?",
        "I don’t break rules, I dissolve them.",
        "Temperature up—structure down!",
        "Even your perfect lattice can't outrun me forever.",
        "The universe favors me, not your little grids."
    ],
    "Dislocator": [
        "Just one slip... and down it all goes!",
        "Perfect lattice? Not on my watch.",
        "I bend, twist, and tear from within!",
        "Think you’ve got structure? Let’s test it!”",
        "Oh no! Another slip plane? What a shame!",
        "Stress me, and I move!",
        "I’m the crack in your crystal’s smile",
        "Grain boundaries love me.",
        "I twist your lattice like a pretzel.",
        "You’ll never strain me out!"
        
    ],
    "MisInfomorph": [
        "Is it hexagonal or hexed?",
        "Oops! Did I mix up your axes again?",
        "I love a confused crystallographer.",
        "Every wrong answer feeds me!",
        "Your confusion is crystal clear.",
        "The more you guess, the stronger I get!"
    ],
    "The Disorder": [
        "Symmetry is just a suggestion.",
        "I whisper chaos into your unit cells.",
        "Perfect order is a myth.",
        "I turn patterns into noise.",
        "I don’t break rules. I undo them.",
        "Try centering this structure!",
    ],
    "Vacancy Viper": [
        "Guess what’s gone? That atom. You’re welcome.",
        "One gap, one glitch, one downfall.",
        "I leave holes where atoms once dreamed.",
        "You’ll never fill what I take!",
        "Don’t worry—it was just one atom…",
        "I slip in, pop one out, slither off.",
        "Perfect occupancy? Not anymore!",
        "Find me if you can—I’m just a... space.",
    ],
    "Glassy Ghoul": [
        "No symmetry, no structure, no mercy.",
        "I haunt your crystal dreams with curves!.",
        "Forget periodicity—I live in chaos!",
        "Try calculating my diffraction pattern!",
        "I ooze where atoms used to align.",
        "Crystalline? Not in this neighborhood.",
        "Your ordered world ends with a shatter.",
        "I’m glassy, ghastly, and glorious.",
    ],
    "Twinster": [
        "Mirror, mirror, everywhere!",
        "Am I the twin... or the original?",
        "You’re not seeing double. You’re seeing me!",
        "Planes reversed, minds confused.",
        "Crack that symmetry—I dare you!",
        "Two orientations? That’s my kind of mess!",
        "My domains are tangled, like your thoughts.",
        "Your structure just split in two... or did it",
        "Twinning is my winning!"
    ],
    "Phase Phantom": [
        "I switch states like socks!",
        "Solid today, something else tomorrow!",
        "Polymorph panic incoming!",
        "What phase am I? Depends on the weather!",
        "Stability is so overrated.",
        "This unit cell? It’s already obsolete.",
        "Metastable? Me? Always.",
        "Temperature up... guess what I become!",
    ]
    
}


def get_enemy_shoutout(enemy_name):
    import random
    base_name = enemy_name.split(" (Lvl")[0]

    if base_name in ENEMY_SHOUTOUTS:
        return random.choice(ENEMY_SHOUTOUTS[base_name])
    else:
        default_shouts = [
            "Prepare to face your doom! ⚔️",
            "You cannot defeat me! 💪",
            "Your knowledge is worthless here! 🧠",
            "I will crush your spirit! 💀",
            "This dungeon will be your tomb! 🏰"
        ]
        return random.choice(default_shouts)



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
    "F": {"min_level": 1, "max_level": 1, "color": "#ff4444", "description": "Novice"},
    "E": {"min_level": 2, "max_level": 2, "color": "#ff5555", "description": "Newcomer"},
    "D": {"min_level": 3, "max_level": 3, "color": "#ff6666", "description": "Beginner"},
    "C-": {"min_level": 4, "max_level": 4, "color": "#ff8800", "description": "Learner"},
    "C": {"min_level": 5, "max_level": 5, "color": "#ffaa00", "description": "Crawler"},
    "C+": {"min_level": 6, "max_level": 6, "color": "#ffcc00", "description": "Explorer"},
    "B-": {"min_level": 7, "max_level": 7, "color": "#cccc00", "description": "Seeker"},
    "B": {"min_level": 8, "max_level": 8, "color": "#aacc00", "description": "Warrior"},
    "B+": {"min_level": 9, "max_level": 9, "color": "#88cc00", "description": "Fighter"},
    "A-": {"min_level": 10, "max_level": 11, "color": "#66aa44", "description": "Veteran"},
    "A": {"min_level": 12, "max_level": 13, "color": "#44aa44", "description": "Elite"},
    "A+": {"min_level": 14, "max_level": 15, "color": "#22aa22", "description": "Master"},
    "S-": {"min_level": 16, "max_level": 18, "color": "#4488ff", "description": "Legend"},
    "S": {"min_level": 19, "max_level": 22, "color": "#2266ff", "description": "Champion"},
    "S+": {"min_level": 23, "max_level": float('inf'), "color": "#0044ff", "description": "Godlike"}
}


def get_current_grade(dungeon_level):
    for grade, threshold in GRADE_THRESHOLDS.items():
        if threshold["min_level"] <= dungeon_level <= threshold["max_level"]:
            return grade, threshold
    return "F", GRADE_THRESHOLDS["F"]


def get_next_grade_info(current_grade):
    grade_order = ["F", "E", "D", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S-", "S", "S+"]
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


    col1, col2 = st.columns(2)

    with col1:
        # Current grade
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, {current_info['color']}, {current_info['color']}aa);
            border: 2px solid {current_info['color']};
            border-radius: 8px;
            padding: 6px;
            color: white;
            font-weight: bold;
            font-size: 0.9rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">
            🎖️ Current<br>
            <span style="font-size: 1.1rem;">{current_grade}</span><br>
            <small style="font-size: 0.7rem;">{current_info['description']}<br>Level {current_level}</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Next grade or max achievement
        if next_grade and next_info:
            levels_needed = next_info["min_level"] - current_level
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, {next_info['color']}, {next_info['color']}66);
                border: 2px dashed {next_info['color']};
                border-radius: 8px;
                padding: 6px;
                color: white;
                font-weight: bold;
                font-size: 0.9rem;
                text-align: center;
                opacity: 0.8;
            ">
                🎯 Next<br>
                <span style="font-size: 1.1rem;">{next_grade}</span><br>
                <small style="font-size: 0.7rem;">{next_info['description']}<br>+{levels_needed} level(s)</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="
                background: linear-gradient(90deg, #ffd700, #ffed4e);
                border: 2px solid #ffd700;
                border-radius: 8px;
                padding: 6px;
                color: #333;
                font-weight: bold;
                font-size: 0.9rem;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            ">
                🌟 Max<br>
                <span style="font-size: 1.1rem;">DONE!</span><br>
                <small style="font-size: 0.7rem;">Ultimate<br>Champion</small>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


    st.markdown("**Progress Overview:**")


    grade_order = ["F", "E", "D", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S-", "S", "S+"]
    progress_html = '<div style="display: flex; gap: 2px; margin: 10px 0;">'

    for grade in grade_order:
        grade_info = GRADE_THRESHOLDS[grade]
        is_current = (grade == current_grade)
        is_achieved = current_level >= grade_info["min_level"]

        if is_current:
            progress_html += f'''
            <div style="
                flex: 1;
                height: 25px;
                background: {grade_info['color']};
                border: 2px solid white;
                border-radius: 4px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 0.8rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            " title="Current: {grade} - {grade_info['description']} (Level {current_level})">
                {grade}
            </div>'''
        elif is_achieved:
            progress_html += f'''
            <div style="
                flex: 1;
                height: 20px;
                background: {grade_info['color']};
                border-radius: 3px;
                opacity: 0.6;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.7rem;
            " title="Completed: {grade} - {grade_info['description']}">
                ✓
            </div>'''
        else:
            # Future grades
            progress_html += f'''
            <div style="
                flex: 1;
                height: 15px;
                background: #555;
                border-radius: 3px;
                opacity: 0.4;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaa;
                font-size: 0.6rem;
            " title="Locked: {grade} - {grade_info['description']} (Need Level {grade_info['min_level']})">
                {grade}
            </div>'''

    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)


    st.markdown("**Nearby Grades:**")
    current_index = grade_order.index(current_grade)
    start_index = max(0, current_index - 1)
    end_index = min(len(grade_order), current_index + 3)
    visible_grades = grade_order[start_index:end_index]

    for grade in visible_grades:
        grade_info = GRADE_THRESHOLDS[grade]
        is_current = (grade == current_grade)
        is_achieved = current_level >= grade_info["min_level"]

        if is_current:
            continue
        elif is_achieved:
            st.markdown(f'''
            <div style="
                background: linear-gradient(90deg, #555, #777);
                border-radius: 6px;
                padding: 4px 8px;
                margin: 2px 0;
                color: #ccc;
                font-size: 0.85rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span>✅ <strong>{grade}</strong> - {grade_info['description']}</span>
                <small>Lvl {grade_info['min_level']}-{grade_info['max_level'] if grade_info['max_level'] != float('inf') else '∞'}</small>
            </div>
            ''', unsafe_allow_html=True)
        else:
            levels_to_unlock = grade_info['min_level'] - current_level
            st.markdown(f'''
            <div style="
                background: #333;
                border: 1px dashed #666;
                border-radius: 6px;
                padding: 4px 8px;
                margin: 2px 0;
                color: #888;
                font-size: 0.85rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <span>🔒 <strong>{grade}</strong> - {grade_info['description']}</span>
                <small>+{levels_to_unlock} levels</small>
            </div>
            ''', unsafe_allow_html=True)


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

            st.session_state.battle_summary["total_questions"] += 1
            st.session_state.battle_summary["questions_wrong"] += 1
            enemy_attack()
            commit_round_log()
            if st.session_state.current_enemy:
                st.session_state.current_problem = generate_problem()
            st.rerun()
            return

    problem = st.session_state.current_problem
    enemy_choice = problem["enemy_choice"]

    st.session_state.battle_summary["total_questions"] += 1

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
        st.session_state.battle_summary["questions_wrong"] += 1
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


BASE_ANSWER_TIME_LIMIT = 30.0


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
    st.session_state.battle_summary = {"damage_taken": 0, "bonuses": [], "total_questions": 0, "questions_wrong": 0}
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


    st.session_state.battle_summary["total_questions"] += 1
    if not is_correct:
        st.session_state.battle_summary["questions_wrong"] += 1

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
        shoutout = get_enemy_shoutout(enemy['name'])

        st.markdown(f"""
                    <div style="
                        position: relative;
                        background: white;
                        border: 3px solid #333;
                        border-radius: 20px;
                        padding: 15px 20px;
                        margin: 0 auto 20px auto;
                        max-width: 300px;
                        font-size: 1.1rem;
                        font-weight: bold;
                        text-align: center;
                        color: #333;
                        box-shadow: 3px 3px 0px #666;
                        transform: rotate(-2deg);
                    ">
                        "{shoutout}"
                        <div style="
                            position: absolute;
                            bottom: -15px;
                            left: 50px;
                            width: 0;
                            height: 0;
                            border-left: 15px solid transparent;
                            border-right: 15px solid transparent;
                            border-top: 15px solid white;
                        "></div>
                        <div style="
                            position: absolute;
                            bottom: -18px;
                            left: 47px;
                            width: 0;
                            height: 0;
                            border-left: 18px solid transparent;
                            border-right: 18px solid transparent;
                            border-top: 18px solid #333;
                        "></div>
                    </div>
                """, unsafe_allow_html=True)
        st.image(enemy["image_path"])

    with stats_col:
        st.header(enemy['name'])
        st.write(f"**HP:**")
        st.progress(enemy['hp'] / enemy['max_hp'], text=f"{enemy['hp']}/{enemy['max_hp']}")
        st.info(f"⚔️ Attack: {enemy['attack']} | 🎯 Accuracy: {enemy['accuracy']}% | 💨 Speed: {enemy['speed']}")


def render_victory_screen():
    summary = st.session_state.battle_summary
    current_grade, current_info = get_current_grade(st.session_state.dungeon_level)

    st.header("Victory!")
    st.balloons()

    # Two column layout for victory details
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader(f"You defeated the {summary.get('enemy_name', 'enemy')}!")
        st.success(f"**XP Gained:** {summary.get('xp_gain', 0)}")
        st.error(f"**Damage Taken:** {round(summary.get('damage_taken', 0), 1)}")

        total_questions = summary.get('total_questions', 0)
        questions_wrong = summary.get('questions_wrong', 0)
        questions_right = total_questions - questions_wrong

        if total_questions > 0:
            accuracy_percentage = (questions_right / total_questions) * 100
            st.info(f"**Battle Accuracy:** {questions_right}/{total_questions} correct ({accuracy_percentage:.1f}%)")
        else:
            st.info("**Battle Accuracy:** No questions answered")

    with col2:
        st.subheader("Current Status")
        st.metric("Current Level", st.session_state.dungeon_level)
        st.metric("Current Grade", f"{current_grade} - {current_info['description']}")

        next_grade, next_info = get_next_grade_info(current_grade)
        if next_grade and next_info:
            levels_needed = next_info["min_level"] - st.session_state.dungeon_level
            st.metric("Next Grade", f"{next_grade} (Need {levels_needed} more levels)")
        else:
            st.success("🌟 **Maximum Grade Achieved!**")

    bonuses = summary.get('bonuses', [])
    if bonuses:
        st.info("Battle Bonuses Earned:")
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


    st.session_state.battle_summary["total_questions"] += 1
    if not is_correct:  # or if result == "lose" for RPS
        st.session_state.battle_summary["questions_wrong"] += 1

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


    st.session_state.battle_summary["total_questions"] += 1
    if not is_correct:
        st.session_state.battle_summary["questions_wrong"] += 1

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


        st.session_state.battle_summary["total_questions"] += 1
        st.session_state.battle_summary["questions_wrong"] += 1

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

            current_grade, current_info = get_current_grade(st.session_state.dungeon_level)
            st.metric("Final Grade Achieved", f"{current_grade} - {current_info['description']}")

        with col2:
            st.subheader("Final Stats")
            player = st.session_state.player
            st.write(f"**Level:** {player['level']}")
            st.info(
                f"⚔️ Attack: {player['attack']} | 🎯 Accuracy: {player['accuracy']}% | 💨 Speed: {player['speed']} | 🧠 Intelligence: {player['intelligence']}")

        st.divider()

        st.subheader("🏆 Your Achievement Progress")

        grade_order = ["F", "E", "D", "C-", "C", "C+", "B-", "B", "B+", "A-", "A", "A+", "S-", "S", "S+"]
        current_level = st.session_state.dungeon_level
        current_grade, current_info = get_current_grade(current_level)

        progress_html = '<div style="display: flex; gap: 2px; margin: 10px 0;">'

        for grade in grade_order:
            grade_info = GRADE_THRESHOLDS[grade]
            is_current = (grade == current_grade)
            is_achieved = current_level >= grade_info["min_level"]

            if is_current:
                progress_html += f'''
                <div style="
                    flex: 1;
                    height: 30px;
                    background: {grade_info['color']};
                    border: 2px solid white;
                    border-radius: 4px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 0.9rem;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                " title="Final Grade: {grade} - {grade_info['description']} (Level {current_level})">
                    {grade}
                </div>'''
            elif is_achieved:
                progress_html += f'''
                <div style="
                    flex: 1;
                    height: 25px;
                    background: {grade_info['color']};
                    border-radius: 3px;
                    opacity: 0.7;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 0.8rem;
                    font-weight: bold;
                " title="Completed: {grade} - {grade_info['description']}">
                    ✓
                </div>'''
            else:
                progress_html += f'''
                <div style="
                    flex: 1;
                    height: 20px;
                    background: #333;
                    border-radius: 3px;
                    opacity: 0.3;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #666;
                    font-size: 0.7rem;
                " title="Not Reached: {grade} - {grade_info['description']} (Need Level {grade_info['min_level']})">
                    {grade}
                </div>'''

        progress_html += '</div>'
        st.markdown(progress_html, unsafe_allow_html=True)


        achieved_grades = [grade for grade in grade_order if current_level >= GRADE_THRESHOLDS[grade]["min_level"]]
        st.info(f"**Grades Achieved:** {len(achieved_grades)}/15 - You unlocked {', '.join(achieved_grades)}")

        next_grade, next_info = get_next_grade_info(current_grade)
        if next_grade and next_info:
            levels_short = next_info["min_level"] - current_level
            st.warning(
                f"**So Close!** You were {levels_short} level(s) away from {next_grade} - {next_info['description']}")

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
                        format_func=lambda x: problem['options'][x],
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
            render_enemy_display()


        log_col, grade_col = st.columns([2, 1])

        with log_col:
            render_game_log()

        with grade_col:
            render_grade_ladder()


if __name__ == "__main__":
    main()
