import streamlit as st
import streamlit.components.v1 as components
import math
import random
from itertools import combinations

# --- HK Mark Six Setup ---
TOTAL_COMBINATIONS = math.comb(49, 6) # 13,983,816

PRIZE_ODDS = {
  "1st Prize (6 Main)": 1 / TOTAL_COMBINATIONS,
  "2nd Prize (5 Main + Special)": 6 / TOTAL_COMBINATIONS,
  "3rd Prize (5 Main)": 252 / TOTAL_COMBINATIONS,
  "4th Prize (4 Main + Special)": 630 / TOTAL_COMBINATIONS,
  "5th Prize (4 Main)": 12915 / TOTAL_COMBINATIONS,
  "6th Prize (3 Main + Special)": 17220 / TOTAL_COMBINATIONS,
  "7th Prize (3 Main)": 229600 / TOTAL_COMBINATIONS,
}

ANY_PRIZE_SINGLE_PROB = sum(PRIZE_ODDS.values())

st.set_page_config(page_title="HK Mark Six", layout="centered")

# Initialize Session States for persistently holding selections and audio state across reruns
if "selected_single_multiple" not in st.session_state:
  st.session_state.selected_single_multiple = []
if "selected_bankers" not in st.session_state:
  st.session_state.selected_bankers = []
if "selected_legs" not in st.session_state:
  st.session_state.selected_legs = []
if "play_bg_music" not in st.session_state:
  st.session_state.play_bg_music = False

# =========================================================================
# BACKGROUND MUSIC (Using Visible Compact YouTube Embed)
# =========================================================================
st.subheader("🎵 Background Music Player")

if st.button("▶️ Turn On Background Music Player"):
    st.session_state.play_bg_music = True

if st.button("🔇 Turn Off Background Music Player"):
    st.session_state.play_bg_music = False

if st.session_state.play_bg_music:
    background_youtube_id = "ZRtdQ81jPUQ"
    # Using visible dimensions so browsers don't block hidden audio
    bg_music_html = f"""
    <iframe width="300" height="80" src="https://www.youtube.com/embed/{background_youtube_id}?autoplay=1&loop=1&playlist={background_youtube_id}" frameborder="0" allow="autoplay; encrypted-media"></iframe>
    """
    components.html(bg_music_html, height=90)
    st.caption("🎶 Background music player loaded above.")
else:
    st.caption("🔇 Background music is currently off.")
# =========================================================================

st.title("HK Mark Six")
st.write("Select your betting method, pick your numbers manually or use Quick Pick")

# --- 1. Choose Betting Method ---
method = st.radio(
  "Choose your Betting Method:",
  ("Single (單式)", "Multiple (複式)", "Banker / Legs (膽拖)")
)

# --- Helper Functions for Quick Picks ---
def generate_balanced_numbers(n_count):
    """Generates numbers trying to balance odd/even and high/low split."""
    all_nums = list(range(1, 50))
    low_half = list(range(1, 25))
    high_half = list(range(25, 50))
    odds = [n for n in all_nums if n % 2 != 0]
    evens = [n for n in all_nums if n % 2 == 0]

    for _ in range(500):
      sample = random.sample(all_nums, n_count)
      lows = len([n for n in sample if n in low_half])
      n_odds = len([n for n in sample if n in odds])
      if abs(lows - (n_count/2)) <= 1.5 and abs(n_odds - (n_count/2)) <= 1.5:
        return sorted(sample)
    return sorted(random.sample(all_nums, n_count))

# --- 2. Smart Quick Pick Panel ---
st.subheader("Smart Quick Pick (機動揀選)")
qp_col1, qp_col2 = st.columns(2)

if method in ["Single (單式)", "Multiple (複式)"]:
  default_pick_size = 6 if method == "Single (單式)" else 8
  target_count = qp_col1.number_input("How many numbers to Quick Pick?", min_value=6 if method == "Single (單式)" else 7, max_value=49, value=default_pick_size)

  if qp_col2.button("Balanced Random Quick Pick"):
      chosen = generate_balanced_numbers(target_count)
      st.session_state.selected_single_multiple = chosen
      for num in range(1, 50):
          st.session_state[f"num_{num}"] = num in chosen

  if qp_col2.button("True Chaos Random Quick Pick"):
      chosen = sorted(random.sample(range(1, 50), target_count))
      st.session_state.selected_single_multiple = chosen
      for num in range(1, 50):
          st.session_state[f"num_{num}"] = num in chosen

else: # Banker method Quick Pick options
  st.write("Set your targets for your Bankers and Legs generation:")
  b_target = qp_col1.number_input("Target Bankers:", min_value=1, max_value=5, value=2)
  l_target = qp_col1.number_input("Target Legs:", min_value=7-b_target, max_value=49-b_target, value=6)

  if qp_col2.button("Generate Random Banker Selection"):
      pool = list(range(1, 50))
      b_chosen = sorted(random.sample(pool, b_target))
      st.session_state.selected_bankers = b_chosen
      remaining_pool = [n for n in pool if n not in b_chosen]
      l_chosen = sorted(random.sample(remaining_pool, l_target))
      st.session_state.selected_legs = l_chosen
      
      for num in range(1, 50):
          st.session_state[f"b_{num}"] = num in b_chosen
          st.session_state[f"l_{num}"] = num in l_chosen

if st.button("Clear Selections"):
  st.session_state.selected_single_multiple = []
  st.session_state.selected_bankers = []
  st.session_state.selected_legs = []
  for num in range(1, 50):
      st.session_state[f"num_{num}"] = False
      st.session_state[f"b_{num}"] = False
      st.session_state[f"l_{num}"] = False

st.markdown("---")

# --- 3. Interactive Grid Number Selection & Value Synchronization ---
st.subheader("Pick Your Numbers (1 - 49)")
numbers = list(range(1, 50))
cols_per_row = 7

if method in ["Single (單式)", "Multiple (複式)"]:
    current_selected = []
    for i in range(0, len(numbers), cols_per_row):
      cols = st.columns(cols_per_row)
      for j, col in enumerate(cols):
        if i + j < len(numbers):
          num = numbers[i + j]
          is_checked = num in st.session_state.selected_single_multiple
          if col.checkbox(f"{num:02d}", value=is_checked, key=f"num_{num}"):
            current_selected.append(num)
    st.session_state.selected_single_multiple = sorted(current_selected)
    num_selected = len(st.session_state.selected_single_multiple)
else:
    num_selected = 0

# Validations
valid = False
tickets = 0
if method == "Single (單式)":
  if num_selected == 6:
    valid = True
    tickets = 1
  else:
    st.warning("⚠️ Single bet requires exactly 6 numbers.")
elif method == "Multiple (複式)":
  if 7 <= num_selected <= 49:
    valid = True
    tickets = math.comb(num_selected, 6)
  else:
      st.warning("⚠️ Multiple bet requires picking between 7 and 49 numbers.")

else: # Banker / Legs method
    st.write("💡 Bankers (膽) appear in every combination. Legs (腳) fill out the rest.")
    col_banker, col_leg = st.columns(2)

    current_bankers = []
    current_legs = []
    
    with col_banker:
       st.write("Select Bankers (Max 5):")
       for b_num in range(1, 50):
          is_b_checked = b_num in st.session_state.selected_bankers
          if st.checkbox(f"Banker {b_num:02d}", value=is_b_checked, key=f"b_{b_num}"):
            current_bankers.append(b_num)
    
    with col_leg:
      st.write("Select Legs:")
      for l_num in range(1, 50):
        disabled = l_num in current_bankers
        is_l_checked = l_num in st.session_state.selected_legs and not disabled
        if st.checkbox(f"Leg {l_num:02d}", value=is_l_checked, key=f"l_{l_num}", disabled=disabled):
          if not disabled:
            current_legs.append(l_num)
    
    st.session_state.selected_bankers = sorted(current_bankers)
    st.session_state.selected_legs = sorted(current_legs)
    
    b_count = len(st.session_state.selected_bankers)
    l_count = len(st.session_state.selected_legs)

    valid = False
    tickets = 0
    if not (1 <= b_count <= 5):
      st.warning("⚠️ You must select between 1 and 5 Bankers.")
    elif b_count + l_count < 7:
      st.warning("⚠️ Combined total of Bankers + Legs must be at least 7 numbers.")
    elif b_count + l_count > 49:
      st.warning("⚠️ Combined total cannot exceed 49 numbers.")
    else:
        valid = True
        tickets = math.comb(l_count, 6 - b_count)

# --- 4. Final Capital Spent & Probability Outputs ---
if valid and tickets > 0:
  cost_per_ticket = 10
  total_spend = tickets * cost_per_ticket
  
  st.success("✅ Configuration Evaluated Successfully!")
  
  metric_col1, metric_col2 = st.columns(2)
  
  with metric_col1:
    st.metric(label="Total Single Combinations Generated", value=f"{tickets:,}")
  with metric_col2:
    st.metric(label="Total Capital Spent (HKD)", value=f"${total_spend:,}")
  
  st.subheader("Your Probability Distribution")
  
  for prize, single_prob in PRIZE_ODDS.items():
    combined_prob = min(single_prob * tickets, 1.0)
    one_in_x = 1 / combined_prob if combined_prob < 1 else 1
    st.markdown(f"{prize}: `{combined_prob:.8%}` &nbsp;&nbsp; (1 in {one_in_x:,.1f})")
  
  st.markdown("---")
  overall_any_prize = min(ANY_PRIZE_SINGLE_PROB * tickets, 1.0)
  one_in_any = 1 / overall_any_prize if overall_any_prize < 1 else 1
  st.markdown(f"### 🎉 Overall Probability to Win ANY Prize: `{overall_any_prize:.4%}` (1 in {one_in_any:.1f})")
else:
  st.info("Adjust selections or click a Quick Pick generator option above to run.")

# --- 5. Lottery Draw Simulation & Prize Evaluation ---
if valid and tickets > 0:
  st.markdown("---")
  st.subheader("🎲 模擬開獎與派彩結果")
  
  PRIZE_PAYOUTS = {
      "1st Prize (6 Main)": 8000000.0,
      "2nd Prize (5 Main + Special)": 1500000.0,
      "3rd Prize (5 Main)": 80000.0,
      "4th Prize (4 Main + Special)": 9600.0,
      "5th Prize (4 Main)": 640.0,
      "6th Prize (3 Main + Special)": 320.0,
      "7th Prize (3 Main)": 40.0
  }
  
  if st.button("🔮 開始六合彩開獎模擬！", type="primary"):
    draw_pool = list(range(1, 50))
    drawn_all = random.sample(draw_pool, 7)
    main_drawn = sorted(drawn_all[:6])
    special_drawn = drawn_all[6]
    
    st.write("### 🔴 本期開獎號碼")
    cols = st.columns(7)
    for idx, num in enumerate(main_drawn):
      cols[idx].metric(f"正碼 {idx+1}", f"{num:02d}")
    cols[6].metric("特別碼 🌟", f"{special_drawn:02d}")
    
    player_tickets = []
    if method in ["Single (單式)", "Multiple (複式)"]:
      player_tickets = list(combinations(st.session_state.selected_single_multiple, 6))
    elif method == "Banker / Legs (膽拖)":
      needed_legs = 6 - len(st.session_state.selected_bankers)
      leg_combos = list(combinations(st.session_state.selected_legs, needed_legs))
      for lc in leg_combos:
        player_tickets.append(tuple(sorted(list(st.session_state.selected_bankers) + list(lc))))
        
    winning_summary = {k: 0 for k in PRIZE_PAYOUTS.keys()}
    total_won = 0.0
    main_drawn_set = set(main_drawn)

    for ticket in player_tickets:
      ticket_set = set(ticket)
      matched_main = len(ticket_set.intersection(main_drawn_set))
      matched_special = special_drawn in ticket_set
      
      prize_key = None
      if matched_main == 6:
        prize_key = "1st Prize (6 Main)"
      elif matched_main == 5 and matched_special:
        prize_key = "2nd Prize (5 Main + Special)"
      elif matched_main == 5:
        prize_key = "3rd Prize (5 Main)"
      elif matched_main == 4 and matched_special:
        prize_key = "4th Prize (4 Main + Special)"
      elif matched_main == 4:
        prize_key = "5th Prize (4 Main)"
      elif matched_main == 3 and matched_special:
        prize_key = "6th Prize (3 Main + Special)"
      elif matched_main == 3:
        prize_key = "7th Prize (3 Main)"
      
      if prize_key:
        winning_summary[prize_key] += 1
        total_won += PRIZE_PAYOUTS[prize_key]

    st.write("### 📊 派彩報告")
    net_profit = total_won - total_spend

    # =========================================================================
    # 🌟 WINNER & LOSER YOUTUBE EMBEDS
    # =========================================================================
    winner_youtube_id = "ZRtdQ81jPUQ"
    loser_youtube_id = "iLBBRuVDOo4"
    # =========================================================================

    if total_won > 0:
      st.balloons()
      st.success(f"🎉 恭喜中獎！總共贏得獎金：HKD ${total_won:,.1f}")
      
      # Play Winning YouTube Audio via hidden iframe
      win_html = f"""
      <iframe width="0" height="0" src="https://www.youtube.com/embed/{winner_youtube_id}?autoplay=1" frameborder="0" allow="autoplay"></iframe>
      """
      components.html(win_html, height=0)
      
      for prize, count in winning_summary.items():
        if count > 0:
          st.write(f"🔹 {prize}：中 {count} 注 (每注約 ${PRIZE_PAYOUTS[prize]:,.0f} HKD)")
    else:
      st.info("很遺憾，本期所有投注均未中獎。再接再厲！")
      
      # Play Losing YouTube Audio via hidden iframe
      lose_html = f"""
      <iframe width="0" height="0" src="https://www.youtube.com/embed/{loser_youtube_id}?autoplay=1" frameborder="0" allow="autoplay"></iframe>
      """
      components.html(lose_html, height=0)

    if net_profit >= 0:
      st.markdown(f"📈 淨利潤：+HKD ${net_profit:,.1f} 🟢")
    else:
      st.markdown(f"📉 淨虧損：-HKD {abs(net_profit):,.1f} 🔴")
