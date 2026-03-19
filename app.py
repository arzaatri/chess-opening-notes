import streamlit as st
import pandas as pd
import os

# --- 1. DATA SETUP (Keep your existing DataFrame logic) ---
# (Assuming vertex and edge are loaded as discussed previously)
@st.cache_data
def load_data():
    return pd.read_csv("vertices.csv").fillna('').set_index("name")
if 'df_vertices' not in st.session_state:
    st.session_state.df_vertices = load_data()

vertex = st.session_state.df_vertices
edge = pd.read_csv("edges.csv").set_index("src")

# --- 2. THE "TOP-START" & STYLE HACK ---
st.set_page_config(layout="wide", page_title="Chess Opening Explorer")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 1. Kill all ghost padding and headers */
    [data-testid="stHeader"], [data-testid="stDecoration"] {display: none;}
    .block-container {
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
    }


    /* 2. Compact Header */
    .header-container { text-align: center; margin-top: 0px; padding-top: 0px; }
    .opening-name { font-size: 32px !important; font-weight: 800; margin-bottom: -5px; }
    .move-sequence { font-size: 22px !important; color: #555; }

    /* 3. Box Sizing (Compact) */
    .white-box, .black-box {
        padding: 10px !important; 
        margin-bottom: 8px !important;
        margin-top: 8px;
        min-height: 100px !important;
        font-size: 14px;
        line-height: 1.2;
    }

    /* 4. Image Constraint - Crucial for 1440p */
    [data-testid="column"]:nth-child(2) [data-testid="stVerticalBlock"] {
        display: flex;
        flex-direction: column;
        align-items: center !important;
    } 
    [data-testid="stImage"] {
        text-align: center;
        display: flex;
        justify-content: center;
    }

    [data-testid="stImage"] img {
        /* This forces the 50% viewport height you requested */
        height: 70vh !important; 
        width: 70vw !important;
        object-fit: contain;
        
        /* Center the element itself within the div */
        margin-left: auto;
        margin-right: auto;
        
    }
    /* Box Styles */

    /* 5. Tighten vertical gaps */
    .stVerticalBlock { gap: 0.5rem !important; }
    hr { margin: 0.5rem 0 !important; }
    
    /* Style the actual textarea elements */
    /* --- FIXED COLORS & POSITIONING --- */

    /* Move the side columns down to align better with the board */
    /* Use unique class names to avoid Streamlit's default column logic */
    .stTextArea label p {
        font-size: 18px !important;
        font-weight: 700 !important;
        margin-bottom: -9px !important;
        justify-content: center;
    }

    
    /* Global fix to ensure labels don't mess up spacing */
    .stTextArea label { justify-content: center; }

    /* Fix for Firefox/Chrome: Ensure the border is visible on focus */
    textarea { 
        resize: none !important; 
        font-size: 16px !important;
        field-sizing: content;
    }
    textarea:focus {
        outline: none !important;
        border: 2px solid #FF4B4B !important; /* Slight red highlight when editing */
    }
    
    [data-testid="stTextArea"] textarea {
        min-height: 290px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. STATE MANAGEMENT ---
if 'current_node' not in st.session_state:
    st.session_state.current_node = "Starting Position"
if 'history' not in st.session_state:
    st.session_state.history = []
if 'board_flipped' not in st.session_state:
    st.session_state.board_flipped = False
def flip_board():
    st.session_state.board_flipped = not st.session_state.board_flipped

def move_to(node_name):
    st.session_state.history.append(st.session_state.current_node)
    st.session_state.current_node = node_name

def go_back():
    if st.session_state.history:
        st.session_state.current_node = st.session_state.history.pop()

def reset():
    st.session_state.current_node = "Starting Position"
    st.session_state.history = []

# --- 4. NAVIGATION & HEADER ---
nav_col_left, _, nav_mid, _, nav_col_right = st.columns([2, 2, 4, 2, 2])
with nav_col_left:
    if st.session_state.current_node != "Starting Position":
        st.button("⬅ Back", on_click=go_back, use_container_width=True)
with nav_mid:
    save_col, flip_col = st.columns(2)
    
    with flip_col:
        label = "🔄 Flip Board"
        st.button(label, on_click=flip_board, use_container_width=True)
        
    with save_col:
        if st.button("💾 Save to CSV", use_container_width=True):
            # 1. Update the DataFrame in memory (Session State)
            st.session_state.df_vertices.at[st.session_state.current_node, 'white_ideas'] = st.session_state[f"wi_{st.session_state.current_node}"]
            st.session_state.df_vertices.at[st.session_state.current_node, 'white_risks'] = st.session_state[f"wr_{st.session_state.current_node}"]
            st.session_state.df_vertices.at[st.session_state.current_node, 'black_ideas'] = st.session_state[f"bi_{st.session_state.current_node}"]
            st.session_state.df_vertices.at[st.session_state.current_node, 'black_risks'] = st.session_state[f"br_{st.session_state.current_node}"]
            
            # 2. Write the entire DataFrame back to the disk
            st.session_state.df_vertices.to_csv("vertices.csv")
            
            # 3. Visual feedback that doesn't ruin the layout
            st.toast(f"Saved {st.session_state.current_node}!", icon="♟️")
with nav_col_right:
    st.button("Reset 🔄", on_click=reset, use_container_width=True)
    
# Fetch current data
current_v = vertex.loc[st.session_state.current_node]
edge_to_here = edge[edge['dst'] == st.session_state.current_node]
move_sequence = current_v['moves'] 

# CENTERING HACK: Displaying the name and sequence
st.markdown(f"""
    <div class="header-container">
        <div class="opening-name">{st.session_state.current_node}</div>
        <div class="move-sequence">{move_sequence}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- 5. MAIN CONTENT ---
left_col, mid_col, right_col = st.columns([2,3,2])

with left_col:
    # White Ideas (White Box)
    white_ideas = st.text_area("White ideas", value=current_v["white_ideas"], 
                               key=f"wi_{st.session_state.current_node}")
    # White Risks (White Box)
    white_risks = st.text_area("White risks", value=current_v["white_risks"], 
                               key=f"wr_{st.session_state.current_node}")

suffix = "_black" if st.session_state.board_flipped else "_white"
img_path = f"images/{st.session_state.current_node}{suffix}.png"

with mid_col:
    if os.path.exists(img_path):
        # Create 3 sub-columns: [1, 4, 1] 
        # The middle sub-column (4) holds the image. Hacky way to center
        sub_left, sub_mid, sub_right = st.columns([1, 9, 1])
        with sub_mid:
            st.image(img_path, use_container_width=True)
    else:
        st.info(f"Position Image: {st.session_state.current_node}.png")

with right_col:
    # Black Ideas (Black Box)
    black_ideas = st.text_area("Black ideas", value=current_v["black_ideas"], 
                               key=f"bi_{st.session_state.current_node}")
    # Black Risks (Black Box)
    black_risks = st.text_area("Black risks", value=current_v["black_risks"], 
                               key=f"br_{st.session_state.current_node}")
    
# --- 6. CONTINUATIONS ---
st.markdown("<h4 style='text-align: center; margin: 0;'>Continuations</h4>", unsafe_allow_html=True)
if st.session_state.current_node in edge.index:
    continuations = edge.loc[[st.session_state.current_node]]
    cols = st.columns(len(continuations))
    for i, (index, row) in enumerate(continuations.iterrows()):
        with cols[i]:
            # Need two whitespaces before newline for streamlit to recognize it
            label = f"{row['dst']}  \n{row['added_moves']}"
            st.button(label, key=f"btn_{row['dst']}", on_click=move_to, args=(row['dst'],), use_container_width=True)
            
st.markdown('<div style="margin-bottom: 100px;"></div>', unsafe_allow_html=True)