import streamlit as st
import random
import time
from pathlib import Path


PLAYER_INITIAL_STATS = {
    "level": 1,
    "hp": 100,
    "max_hp": 100,
    "xp": 0,
    "xp_to_next_level": 50,
    "intelligence": 5,  # Affects damage
    "accuracy": 80,  # % chance to hit
    "speed": 5,  # Determines who attacks first
    "stat_points": 0
}

ENEMY_BASE_STATS = {
    "name": "Goblin",
    "hp": 30,
    "max_hp": 30,
    "attack": 8,
    "accuracy": 70,
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

ANSWER_TIME_LIMIT = 15.0  # seconds



def apply_custom_styling():

    st.set_page_config(layout="wide", initial_sidebar_state="expanded",)
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
        </style>
    """, unsafe_allow_html=True)



def init_game():
    if "player" not in st.session_state:
        st.session_state.player = PLAYER_INITIAL_STATS.copy()
        st.session_state.current_enemy = None
        st.session_state.game_log = []
        st.session_state.dungeon_level = 1
        st.session_state.question_start_time = None
        st.session_state.battle_summary = {}
        st.session_state.game_over = False

    if st.session_state.current_enemy is None and not st.session_state.battle_summary and not st.session_state.game_over:
        generate_enemy()


def reset_game_state():
    st.session_state.player = PLAYER_INITIAL_STATS.copy()
    st.session_state.current_enemy = None
    st.session_state.game_log = []
    st.session_state.dungeon_level = 1
    st.session_state.question_start_time = None
    st.session_state.battle_summary = {}
    st.session_state.game_over = False
    generate_enemy()


def generate_enemy():
    enemy_multiplier=0.65
    level = st.session_state.dungeon_level

    selected_enemy_data = random.choice(ENEMIES_LIST)

    st.session_state.current_enemy = {
        "name": f"{selected_enemy_data['name']} (Lvl {level})",
        "image_path": selected_enemy_data['image'],
        "hp": round(ENEMY_BASE_STATS["hp"] * level*enemy_multiplier,1),
        "max_hp": round(ENEMY_BASE_STATS["hp"] * level*enemy_multiplier,1),
        "attack": round(ENEMY_BASE_STATS["attack"] * level*enemy_multiplier,1),
        "accuracy": round(ENEMY_BASE_STATS["accuracy"] + level*enemy_multiplier,1),
        "speed": round(ENEMY_BASE_STATS["speed"] + (level // 2)*enemy_multiplier,1),
        "xp_reward": ENEMY_BASE_STATS["xp_reward"] * level
    }
    # Reset summary for the new battle
    st.session_state.battle_summary = {"damage_taken": 0, "bonuses": []}
    st.session_state.math_problem = generate_math_problem()
    log_message(f"A wild {st.session_state.current_enemy['name']} appears!")


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
        else:  # '*'
            a = random.randint(2, 5 + level_scale)
            b = random.randint(2, 5 + level_scale)
            answer = a * b
            question_str = f"{a} * {b}"

    elif dungeon_level < 10:
        level_scale = dungeon_level - 4  # scale from 1
        a = random.randint(1 * level_scale, 5 * level_scale)
        b = random.randint(2 * level_scale, 6 * level_scale)
        c = random.randint(2, 5)

        question_str = f"{a} + {b} * {c}"
        answer = a + (b * c)

    else:
        level_scale = dungeon_level - 9  # scale from 1
        a = random.randint(3 * level_scale, 7 * level_scale)
        b = random.randint(1 * level_scale, 5 * level_scale)
        c = random.randint(2, 7)
        op = random.choice(['+', '-'])

        if op == '+':
            question_str = f"({a} + {b}) * {c}"
            answer = (a + b) * c
        else:  # op == '-'
            question_str = f"({a} - {b}) * {c}"
            answer = (a - b) * c

    st.session_state.question_start_time = time.time()
    st.session_state.time_out_attack_done = False

    return {"question": question_str, "answer": answer}


def log_message(message):
    """Adds a message to the game log."""
    st.session_state.game_log.insert(0, message)
    if len(st.session_state.game_log) > 10:
        st.session_state.game_log.pop()



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
        st.progress(player['hp'] / player['max_hp'], text=f"{player['hp']}/{player['max_hp']}")
        st.write(f"**XP:**")
        st.progress(player['xp'] / player['xp_to_next_level'], text=f"{player['xp']}/{player['xp_to_next_level']}")
        st.info(
            f"🧠 Intelligence: {player['intelligence']}\n\n🎯 Accuracy: {player['accuracy']}%\n\n💨 Speed: {player['speed']}")


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

    st.divider()


def render_game_log():

    st.subheader("Battle Log")
    log_container = st.container(height=350)  #
    for msg in st.session_state.game_log:
        log_container.text(f"> {msg}")


def render_victory_screen():
    """Renders the screen after a battle is won, showing a summary."""
    summary = st.session_state.battle_summary
    st.header("Victory!")
    st.balloons()

    st.subheader(f"You defeated the {summary.get('enemy_name', 'enemy')}!")

    st.success(f"**XP Gained:** {summary.get('xp_gain', 0)}")
    st.error(f"**Damage Taken:** {summary.get('damage_taken', 0)}")

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
    if time_taken > ANSWER_TIME_LIMIT:
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


def player_attack(answer_correct, bonus):
    """Handles the player's attack turn, including bonuses."""
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    if bonus["time_out"] or not answer_correct:
        log_message(
            bonus["message"] if bonus["time_out"] else "Your calculation was wrong! Your attack misses completely.")
        return

    if bonus["message"]:
        log_message(bonus["message"])
        st.session_state.battle_summary["bonuses"].append(bonus["message"])

    if bonus["heal_amount"] > 0:
        player['hp'] = min(player['max_hp'], player['hp'] + bonus["heal_amount"])

    if random.randint(1, 100) <= player['accuracy']:
        base_damage = player['intelligence'] + random.randint(player['level'], player['level'] * 3)
        total_damage = base_damage + bonus["bonus_damage"]
        enemy['hp'] = max(0, enemy['hp'] - total_damage)
        log_message(f"✅ Correct! You strike for **{total_damage} damage**!")
    else:
        log_message("Your attack missed!")

    if enemy['hp'] <= 0:
        handle_victory()


def enemy_attack():
    """Handles the enemy's attack turn."""
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    if random.randint(1, 100) <= enemy['accuracy']:
        damage = enemy['attack'] + random.randint(0, 3 * st.session_state.dungeon_level)
        player['hp'] = max(0, player['hp'] - damage)
        log_message(f"The {enemy['name']} hits you for {damage} damage!")
        st.session_state.battle_summary["damage_taken"] += damage
    else:
        log_message(f"The {enemy['name']}'s attack missed!")

    if player['hp'] <= 0:
        st.session_state.game_over = True
        log_message("You have been defeated... Game Over.")


def handle_victory():
    """Handles logic for when the player defeats an enemy."""
    player = st.session_state.player
    enemy = st.session_state.current_enemy

    log_message(f"You have defeated the {enemy['name']}!")

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
        log_message(f"🎉 LEVEL UP! You are now level {player['level']}!")
        log_message("You feel stronger and fully healed. You gained 3 stat points!")

    st.session_state.current_enemy = None


def handle_turn(player_answer):
    """Processes a full turn of combat."""
    problem = st.session_state.math_problem
    time_taken = time.time() - st.session_state.question_start_time
    is_correct = (player_answer == problem['answer'])

    bonus = calculate_time_bonus(time_taken)

    player_speed = st.session_state.player['speed']
    enemy_speed = st.session_state.current_enemy['speed']

    if player_speed >= enemy_speed:
        player_attack(is_correct, bonus)
        if st.session_state.current_enemy and st.session_state.current_enemy['hp'] > 0:
            enemy_attack()
    else:
        enemy_attack()
        if st.session_state.player['hp'] > 0:
            player_attack(is_correct, bonus)

    if st.session_state.current_enemy:
        st.session_state.math_problem = generate_math_problem()
    st.rerun()


def render_level_up_screen():
    """Renders the screen for spending stat points."""
    st.header("Level Up! Spend Your Stat Points")
    player = st.session_state.player
    st.write(f"You have **{player['stat_points']}** points to spend.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🧠 Increase Intelligence (+1)", use_container_width=True, disabled=(player['stat_points'] == 0)):
            player['intelligence'] += 1
            player['stat_points'] -= 1
            st.rerun()
    with col2:
        if st.button("🎯 Increase Accuracy (+2%)", use_container_width=True, disabled=(player['stat_points'] == 0)):
            player['accuracy'] += 2
            player['stat_points'] -= 1
            st.rerun()
    with col3:
        if st.button("💨 Increase Speed (+1)", use_container_width=True, disabled=(player['stat_points'] == 0)):
            player['speed'] += 1
            player['stat_points'] -= 1
            st.rerun()

    if player['stat_points'] == 0:
        st.success("All points spent! You are ready for the next battle.")
        if st.session_state.current_enemy is None:
            generate_enemy()
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
                f"🧠 Intelligence: {player['intelligence']} | 🎯 Accuracy: {player['accuracy']}% | 💨 Speed: {player['speed']}")

        st.divider()
        st.subheader("A new adventure awaits...")
        if st.button("Restart Your Quest", use_container_width=True, type="primary"):
            reset_game_state()
            st.rerun()
        return


    #st.title("Numeria: The Math Dungeon")
    render_sidebar_stats()

    if st.session_state.player['stat_points'] > 0:
        render_level_up_screen()
    elif st.session_state.current_enemy is None:
        render_victory_screen()
    else:
        st.subheader(f"Dungeon Level: {st.session_state.dungeon_level}")

        action_col, log_col = st.columns([2, 1])

        with action_col:
            render_enemy_display()


            problem = st.session_state.math_problem
            time_elapsed = time.time() - st.session_state.question_start_time
            time_left = max(0, ANSWER_TIME_LIMIT - time_elapsed)

            if time_left <= 0 and not st.session_state.get('time_out_attack_done', False):
                st.session_state.time_out_attack_done = True
                log_message("⏰ Time's up! The enemy takes advantage of your hesitation!")
                enemy_attack()
                if not st.session_state.get("game_over"):
                    st.session_state.math_problem = generate_math_problem()
                st.rerun()

            #st.progress(time_left / ANSWER_TIME_LIMIT, text=f"Time Left: {time_left:.1f}s")
            st.progress(time_left / ANSWER_TIME_LIMIT, text=f"⌛ Time is ticking...")
            st.markdown(f'<p class="math-question">Solve this:<br><code>{problem["question"]}</code></p>',
                        unsafe_allow_html=True)

            with st.form("attack_form", clear_on_submit=True):
                user_answer = st.number_input("Your answer:", value=None, step=1, format="%d", key="math_answer_input",
                                              label_visibility="collapsed", placeholder="Type your answer...")
                submitted = st.form_submit_button("Attack!", use_container_width=True, type="primary")
                if submitted:
                    handle_turn(user_answer)

        with log_col:
            render_game_log()


if __name__ == "__main__":
    main()
