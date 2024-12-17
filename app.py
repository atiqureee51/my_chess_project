import streamlit as st
import chess
import chess.svg
from stockfish import Stockfish
import base64

# --- CONFIGURATION ---
# Path to stockfish engine binary - update this if different.
STOCKFISH_PATH = "./stockfish"

# Initialize Stockfish with a high skill level and depth for maximum difficulty.
# Skill level: 20 is max. 
# For additional difficulty, we will also set a high depth.
stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Skill Level": 20})
stockfish.set_depth(25)

# Set page config
st.set_page_config(page_title="World's Hardest Chess", page_icon="♖")

# --- SESSION STATE ---
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "moves" not in st.session_state:
    st.session_state.moves = []
if "engine_turn" not in st.session_state:
    st.session_state.engine_turn = False
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "player_color" not in st.session_state:
    # Let player choose color at start
    st.session_state.player_color = "white"

# --- FUNCTIONS ---
def render_board(board):
    # Renders the chess board as SVG
    svg = chess.svg.board(board=board, size=400, orientation=st.session_state.player_color)
    return svg

def make_move(move_uci):
    # Make a move on the board using UCI notation if legal.
    move = chess.Move.from_uci(move_uci)
    if move in st.session_state.board.legal_moves:
        st.session_state.board.push(move)
        return True
    return False

def engine_move():
    # Ask stockfish for the best move
    stockfish.set_fen_position(st.session_state.board.fen())
    best_move = stockfish.get_best_move()
    if best_move:
        st.session_state.board.push_uci(best_move)

def check_game_over():
    board = st.session_state.board
    if board.is_game_over():
        return True, board.result()
    return False, None

# --- MAIN APP ---
st.title("World's Hardest Chess")

# On first load, let user select color
if len(st.session_state.moves) == 0 and st.session_state.board.fullmove_number == 1:
    st.session_state.player_color = st.selectbox("Choose your color:", ["white", "black"])
    if st.session_state.player_color == "black" and not st.session_state.game_over:
        # If player chooses black, engine moves first.
        engine_move()
    
# Display the board
board_svg = render_board(st.session_state.board)
st.write(board_svg, unsafe_allow_html=True)

# Display game status
game_over, result = check_game_over()
if game_over:
    st.session_state.game_over = True
    st.markdown(f"**Game Over! Result: {result}**")
else:
    st.session_state.game_over = False

# Move input section
if not st.session_state.game_over:
    # Determine if it's human's turn or engine's turn
    turn_color = "white" if st.session_state.board.turn == chess.WHITE else "black"

    if ((turn_color == "white" and st.session_state.player_color == "white") or
        (turn_color == "black" and st.session_state.player_color == "black")):

        # Human's turn
        st.subheader("Your Move")
        # We could provide a text input for a UCI move or a from-square and to-square combo
        # For user-friendliness, let's provide a selectbox of all legal moves in UCI form
        legal_moves_uci = [move.uci() for move in st.session_state.board.legal_moves]
        chosen_move = st.selectbox("Select your move:", [""] + legal_moves_uci)
        if st.button("Make Move") and chosen_move != "":
            if make_move(chosen_move):
                # After human move, check if game is over
                game_over, result = check_game_over()
                if not game_over:
                    # Engine moves next
                    engine_move()
            else:
                st.error("Illegal move. Please try again.")

    else:
        # Engine's turn (if somehow user action triggered it)
        # This situation should be handled automatically after a human move
        pass

    # Re-display updated board after moves
    board_svg = render_board(st.session_state.board)
    st.write(board_svg, unsafe_allow_html=True)

    # Check game status again after engine move
    game_over, result = check_game_over()
    if game_over:
        st.markdown(f"**Game Over! Result: {result}**")

# Restart button
if st.button("Restart Game"):
    st.session_state.board = chess.Board()
    st.session_state.moves = []
    st.session_state.game_over = False
    st.session_state.player_color = "white"
    st.experimental_rerun()
