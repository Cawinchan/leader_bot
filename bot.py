"""
Board Game Tracker Telegram Bot

This bot allows you to:
    • Automatically record games and assign points by rank (/add_auto).
    • Manually add points for each player (/add).
    • View all recorded games (/view).
    • Remove a recorded game (/remove).
    • See leaderboards (/leaderboard).
    • Generate random comebacks (/comeback).
    • ... and more!

Author: Cawin Chan
"""

import os
import random
import logging
import datetime
import sqlite3
from collections import defaultdict

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ---------------
#     CONSTANTS
# ---------------
COMEBACKS = [
    "you den lah",
    "your mother gay",
    "your granny tranny",
    "your sister mister",
    "Your family tree LGBT",
    "your brother a mother",
    "your ancestors incestors",
]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DB_PATH = "/data/board_game_tracker.db"

if not TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN found in environment variables.")

WELCOME_MSG = (
    "Welcome to the Board Game Tracker Bot!\n\n"
    "<b>Here's what you can do:</b>\n"
    "/add - Manually specify points for each player.\n"
    "/adjust - &lt;player_name&gt; &lt;points&gt; (-15 removes 15 points) [reason...](Optional).\n"
    "/add_auto - Record a new game and calculate points automatically.\n"
    "/view - View all recorded games.\n"
    "/view_adjustment - View all adjusted scores.\n"
    "/remove - Delete a recorded game or adjustment.\n"
    "/leaderboard - See the overall and solo-only leaderboards.\n"
    "/comeback - Get a random comeback for fun.\n"
    "/help - See this message.\n\n"
    "Need help? Just type /help anytime!\n\n"
    "ENJOY"
)


# ---------------------------
#  DATABASE UTILS & SETUP
# ---------------------------
def init_db():
    """
    Initialize the SQLite database if it doesn't exist.
    Create or alter tables/columns as needed.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            winner TEXT NOT NULL,
            date TEXT NOT NULL,
            is_team_game INTEGER NOT NULL,
            ranking INTEGER NOT NULL,
            players TEXT NOT NULL,
            game_type TEXT,          -- 'solo', 'team', or 'pair'
            points_awarded REAL      -- Points awarded to 'winner' row
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS adjustments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            date TEXT NOT NULL,
            points REAL NOT NULL,
            reason TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_game_entry(
        game_name: str,
        date: str,
        is_team_game: int,
        game_type: str,
        player_name: str,
        ranking: int,
        all_players_str: str,
        points_awarded: float,
):
    """
    Insert a single row into the 'games' table.

    :param game_name: Name of the game played.
    :param date: Date of the game in 'YYYY-MM-DD' format.
    :param is_team_game: 1 if it's 'team' or 'pair', else 0 if 'solo'.
    :param game_type: 'solo', 'team', or 'pair'.
    :param player_name: Name of the player (winner column).
    :param ranking: Player's rank (e.g., 1 for first place).
    :param all_players_str: Comma-separated list of all players.
    :param points_awarded: Points assigned to the player_name for this row.
    """
    # Normalize to lowercase for consistency
    player_name = player_name.lower()
    normalized_players = [p.strip().lower() for p in all_players_str.split(",")]
    all_players_lower = ", ".join(normalized_players)

    conn = sqlite3.connect("board_game_tracker.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO games (
            name, winner, date, is_team_game, ranking, players, 
            game_type, points_awarded
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            game_name,
            player_name,
            date,
            is_team_game,
            ranking,
            all_players_lower,
            game_type,
            points_awarded,
        ),
    )
    conn.commit()
    conn.close()


def add_adjustment(player_name: str, date: str, points: float, reason: str = ""):
    """
    Insert a single row into the 'adjustments' table.
    For minus points, pass a negative float (e.g. -5.0).
    """
    player_name = player_name.lower()  # Normalize
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO adjustments (player_name, date, points, reason)
        VALUES (?, ?, ?, ?)
        """,
        (player_name, date, points, reason),
    )
    conn.commit()
    conn.close()


def get_adjustments():
    """
    Return all rows from the 'adjustments' table as a list of tuples:
    (id, player_name, date, points, reason).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, player_name, date, points, reason FROM adjustments")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_games():
    """
    Return all rows from the 'games' table as a list of tuples:
    (id, name, winner, date, is_team_game, ranking, players, game_type, points_awarded).
    """
    conn = sqlite3.connect("board_game_tracker.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            id, name, winner, date, is_team_game, ranking, players, game_type, points_awarded
        FROM games
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_past_players():
    """
    Returns a distinct list of any player who has appeared in the 'winner' column of 'games'.
    """
    conn = sqlite3.connect("board_game_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT LOWER(winner) FROM games")
    rows = [row[0] for row in cursor.fetchall()]
    conn.close()
    return list(set(rows))


def delete_game(game_id: int):
    """
    Remove a particular game row from the 'games' table by its ID.
    """
    conn = sqlite3.connect("board_game_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------
#  POINTS ASSIGNMENT LOGIC & LEADERBOARD FUNCTIONS
# ---------------------------------------------------
def award_points_for_game(game_type: str, players: list, rankings: list):
    """
    Compute points for each player automatically based on game type and rank.

    Scenarios:
    1) solo (4 players):
       - rank 1 => +6, rank 2 => +3, rank 3 => +1, rank 4 => +0

    2) team (4v1 scenario):
       - If solo player is rank=1 => solo player gets +6, team players get +0
       - If the team is rank=1 => each rank-1 team member gets 6 / (# of members), solo gets +0

    3) pair:
       - rank=1 => total 6 points shared among all rank-1 players
       - rank=2 => total 3 points shared among all rank-2 players
       - rank=3 => total 1 point shared among all rank-3 players
       - rank=4 => 0
    """
    from collections import defaultdict

    players = [p.lower() for p in players]  # Normalize
    awarded_points = {p: 0.0 for p in players}
    rank_map = defaultdict(list)

    # Create rank_map => {1: [player1, player2], 2: [...], ...}
    for player, rank in zip(players, rankings):
        rank_map[rank].append(player)

    if game_type == "solo":
        # Mapping rank => assigned points
        distribution = {1: 6, 2: 3, 3: 1, 4: 0}
        for rank, group in rank_map.items():
            points_for_rank = distribution.get(rank, 0)
            for player in group:
                awarded_points[player] = float(points_for_rank)

    elif game_type == "team":
        # 4v1 scenario
        rank1_players = rank_map.get(1, [])
        if len(rank1_players) == 1:
            # If exactly 1 player is rank=1 => that is the solo winner => +6
            solo_winner = rank1_players[0]
            awarded_points[solo_winner] = 6.0
        else:
            # Otherwise, the team is rank=1 => each gets 6 / (# in rank1 group)
            for player in rank1_players:
                awarded_points[player] = 6.0 / len(rank1_players)

    elif game_type == "pair":
        # rank => total pot to be shared
        pair_distribution = {1: 6, 2: 3, 3: 1, 4: 0}
        for rank, group in rank_map.items():
            pot = pair_distribution.get(rank, 0)
            if group:
                split_amount = float(pot) / len(group)
                for player in group:
                    awarded_points[player] = split_amount

    return awarded_points


def capitalize_name(name: str) -> str:
    """
    Convert a player's name to Title Case, e.g., 'john doe' => 'John Doe'.
    """
    return name.title()


def classify_player(player_name: str, points: float, game_count: int) -> str:
    """
    Example classification for players based on average points:
    - Type A if average > 3
    - Type B if 1 < average <= 3
    - Type C otherwise
    """
    if game_count == 0:
        return "Type C Player"  # fallback
    avg_points = points / game_count
    if avg_points > 3:
        return "Type A Player"
    elif avg_points > 1:
        return "Type B Player"
    else:
        return "Type C Player"


async def view_adjustments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /view_adjustments - Show all manual plus/minus adjustments.
    """
    rows = get_adjustments()
    if not rows:
        await update.message.reply_text("No manual adjustments found.")
        return

    lines = []
    for row in rows:
        # row => (id, player_name, date, points, reason)
        adj_id = row[0]
        p_name = row[1]
        d_str = row[2]
        pts = row[3]
        reason = row[4] or ""
        lines.append(
            f"[ID {adj_id}] {p_name.title()} => {pts:+.1f} pts on {d_str}\n"
            f"   Reason: {reason}"
        )

    await update.message.reply_text("Adjustments:\n\n" + "\n\n".join(lines))


def remove_adjustment(adj_id: int):
    """
    Delete an adjustment row from the 'adjustments' table by its ID.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM adjustments WHERE id = ?", (adj_id,))
    conn.commit()
    conn.close()


def compute_leaderboards():
    rows = get_games()
    total_points = defaultdict(float)
    solo_points = defaultdict(float)
    game_count = defaultdict(int)

    # Sum from 'games' table
    for row in rows:
        player = row[2].lower()
        g_type = row[7]
        p_award = row[8] or 0
        total_points[player] += p_award

        if g_type == "solo":
            solo_points[player] += p_award

        game_count[player] += 1

    # Now add adjustments (which can be positive or negative)
    adj_rows = get_adjustments()  # or however you retrieve them
    for adj in adj_rows:
        # (id, player_name, date, points, reason)
        p_name = adj[1].lower()
        p_val = adj[3] or 0
        total_points[p_name] += p_val
        # if you also want the minus to affect solo leaderboard, do:
        # solo_points[p_name] += p_val

    # Build final sorted lists
    def build_list(points_dict):
        data = []
        for player, pts in points_dict.items():
            is_provisional = (game_count[player] < 3)
            data.append((player, pts, is_provisional))
        data.sort(key=lambda x: x[1], reverse=True)
        return data

    overall_list = build_list(total_points)
    solo_only_list = build_list(solo_points)
    return overall_list, solo_only_list, game_count


# ---------------------------------------------------
#  TELEGRAM BOT COMMAND & MESSAGE HANDLERS
# ---------------------------------------------------
async def dom_joke_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Simple command handler that returns a silly statement about 'Dom'.
    """
    await update.message.reply_text("Dom is gay")


async def xuanli_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /xuanli command: Responds with "god gamer".
    """
    await update.message.reply_text("God Gamer")


async def cawin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /cawin command: Responds with "still thinking about what to play next".
    """
    await update.message.reply_text("still thinking...")


async def junming_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /junming command: Responds with one of the three phrases for Junming.
    """
    responses = [
        "I just thought of a funny play",
        "CORRECT",
        "What am I doing? 3 is not 4",
    ]
    response = random.choice(responses)
    await update.message.reply_text(response)


async def austen_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /austen command: Responds with one of the two phrases for Austen.
    """
    responses = [
        "Why think so much",
        "If I don't fight you, how can I sleep at night?",
        "🖕🖕"
    ]
    response = random.choice(responses)
    await update.message.reply_text(response)


async def random_comeback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a random comeback from the predefined list COMEBACKS.
    """
    comeback = random.choice(COMEBACKS)
    await update.message.reply_text(comeback)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start command: Greet the user and show the welcome message.
    """
    await update.message.reply_text(WELCOME_MSG, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /help command: Show the same welcome/instruction message as /start.
    """
    await update.message.reply_text(WELCOME_MSG, parse_mode="HTML")


# ---------------------------
#  /minus (MANUAL POINTS)
# ---------------------------
async def adjust_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Usage: /adjust - &lt;player_name&gt; &lt;points&gt; (-15 removes 15 points) [reason...](Optional)

    e.g. /adjust bob -3 tardiness
         /adjust alice 3 national service

    This will record an adjustment of -3 for 'bob' or 3 'alice'.
    """
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /adjust <player_name> <points>(-15 removes 15 points) [reason...](Optional)"
        )
        return

    player_name = args[0]
    # attempt to parse the float
    try:
        points_to_adjust = float(args[1])
    except ValueError:
        await update.message.reply_text("Invalid points. Must be a number, e.g. 5 or 3.5")
        return

    reason = " ".join(args[2:]) if len(args) > 2 else ""

    # Use today's date by default
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Insert negative points into 'adjustments'
    add_adjustment(player_name, date_str, points_to_adjust, reason)

    response = (
        f"{points_to_adjust} points have been subtracted from {player_name.title()}."
    )
    if reason:
        response += f" (Reason: {reason})"

    await update.message.reply_text(response)


# ---------------------------
#  /add (MANUAL POINTS)
# ---------------------------
async def add_points_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add command: Start the conversation for manually adding points.
    We'll store conversation state in context.user_data.
    """
    context.user_data["command"] = "add"
    context.user_data["manual_add_stage"] = "game_name"
    await update.message.reply_text("What game was played? (e.g., 'Catan')")


async def handle_add_points_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the multi-step conversation for manually adding points to each player.
    The steps are stored in context.user_data["manual_add_stage"].
    """
    if "manual_add_stage" not in context.user_data:
        await update.message.reply_text("Please use /add to start adding a game.")
        return

    stage = context.user_data["manual_add_stage"]
    text = update.message.text.strip()

    if stage == "game_name":
        context.user_data["game_name"] = text
        context.user_data["manual_add_stage"] = "game_type"
        await update.message.reply_text(
            "Is this a 'solo', 'team', or 'pair' game?\n"
            "Type exactly 'solo', 'team', or 'pair'."
        )

    elif stage == "game_type":
        game_type_lower = text.lower()
        if game_type_lower not in ["solo", "team", "pair"]:
            await update.message.reply_text("Please type 'solo', 'team', or 'pair'.")
            return
        context.user_data["game_type"] = game_type_lower
        context.user_data["is_team_game"] = 1 if game_type_lower != "solo" else 0

        # Suggest past players
        past_players = get_past_players()
        if past_players:
            past_players_msg = (
                    "\nHere are some previous players:\n  " + ", ".join(past_players)
            )
        else:
            past_players_msg = "\nNo previous players found."

        context.user_data["manual_add_stage"] = "players"
        await update.message.reply_text(
            "Who played? Provide player names separated by commas.\n"
            f"Example: 'Alice, Bob, Charlie'\n"
            f"{past_players_msg}"
        )

    elif stage == "players":
        players = [p.strip().lower() for p in text.split(",") if p.strip()]
        if not players:
            await update.message.reply_text("Please enter at least one player name.")
            return
        context.user_data["players"] = players
        context.user_data["manual_add_stage"] = "points"
        await update.message.reply_text(
            "Now enter the points earned for each player in the same order.\n"
            "Example: '6, 3, 1, 0'"
        )

    elif stage == "points":
        try:
            points = list(map(float, text.split(",")))
            num_of_players = len(context.user_data["players"])
            if len(points) != num_of_players:
                # *** PRESERVE the comedic line here ***
                raise ValueError(
                    f"You den lah! You give {len(points)} but got {num_of_players}, what you want me to do?."
                )
            context.user_data["points"] = points
            context.user_data["manual_add_stage"] = "date"
            await update.message.reply_text(
                "What is the date of the game? (YYYY-MM-DD)\n"
                "Type 'today' if it's today's date."
            )
        except Exception as e:
            await update.message.reply_text(f"Error parsing points: {e}")

    elif stage == "date":
        if text.lower() in ["today", "now"]:
            date_str = datetime.date.today().strftime("%Y-%m-%d")
        else:
            date_str = text

        game_name = context.user_data["game_name"]
        game_type_str = context.user_data["game_type"]
        is_team_game = context.user_data["is_team_game"]
        players = context.user_data["players"]
        points = context.user_data["points"]

        # Insert a row per player
        for player, point_val in zip(players, points):
            add_game_entry(
                game_name=game_name,
                date=date_str,
                is_team_game=is_team_game,
                game_type=game_type_str,
                player_name=player,
                ranking=-1,  # Ranking not relevant for manual points entry
                all_players_str=", ".join(players),
                points_awarded=point_val,
            )

        # Report the result
        result_msg = (
                f"Game '{game_name}' on {date_str} recorded.\n"
                "Points awarded manually:\n" +
                "\n".join(f"{p}: +{pt}" for p, pt in zip(players, points))
        )
        await update.message.reply_text(result_msg)
        context.user_data.clear()


# ---------------------------
#  /add_auto (AUTO POINTS)
# ---------------------------
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /add_auto command: Start the conversation for automatically assigning points
    based on the rank of each player.
    """
    context.user_data["command"] = "add_auto"
    context.user_data["add_stage"] = "game_name"
    await update.message.reply_text("What game was played? (e.g., 'Catan')")


async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the multi-step conversation for auto-calculating points.
    The steps are stored in context.user_data["add_stage"].
    """
    if "add_stage" not in context.user_data:
        await update.message.reply_text("Please use /add_auto to start adding a game.")
        return

    stage = context.user_data["add_stage"]
    text = update.message.text.strip().lower()

    if stage == "game_name":
        context.user_data["game_name"] = text
        context.user_data["add_stage"] = "game_type"
        await update.message.reply_text(
            "Is this a 'solo' (1v1v1v1), 'team' (4v1), or 'pair' (2v2 or 2v3v2) game?\n"
            "Type exactly 'solo', 'team', or 'pair'."
        )

    elif stage == "game_type":
        if text not in ["solo", "team", "pair"]:
            await update.message.reply_text("Please type 'solo', 'team', or 'pair'.")
            return
        context.user_data["game_type"] = text
        context.user_data["is_team_game"] = 1 if text != "solo" else 0

        past_players = get_past_players()
        if past_players:
            past_players_msg = (
                    "\nHere are some previous players:\n  " + ", ".join(past_players)
            )
        else:
            past_players_msg = "\nNo previous players found."
        context.user_data["add_stage"] = "players"

        await update.message.reply_text(
            "Who played? Provide player names separated by commas.\n"
            f"Example: 'Alice, Bob, Charlie'\n"
            f"{past_players_msg}"
        )

    elif stage == "players":
        players = [p.strip().lower() for p in update.message.text.split(",") if p.strip()]
        if not players:
            await update.message.reply_text("Please enter at least one player name.")
            return
        context.user_data["players"] = players
        context.user_data["add_stage"] = "rankings"
        await update.message.reply_text(
            "Now enter the rankings for each player in the same order.\n"
            "Example: '1, 2, 3, 4' (1 = first place, etc.)\n\n"
            "For a team game, group the winning players with rank=1, etc."
        )

    elif stage == "rankings":
        try:
            rankings = list(map(int, update.message.text.split(",")))
            num_of_players = len(context.user_data["players"])
            if len(rankings) != num_of_players:
                # *** PRESERVE the comedic line here ***
                raise ValueError(
                    f"You den lah! You give {len(rankings)} but got {num_of_players}, what you want me to do?."
                )
            context.user_data["rankings"] = rankings
            context.user_data["add_stage"] = "date"
            await update.message.reply_text(
                "What is the date of the game? (YYYY-MM-DD)\n"
                "Type 'today' if it's today's date."
            )
        except Exception as e:
            await update.message.reply_text(f"Error parsing rankings: {e}")

    elif stage == "date":
        if text in ["today", "now"]:
            date_str = datetime.date.today().strftime("%Y-%m-%d")
        else:
            date_str = update.message.text.strip()

        game_name = context.user_data["game_name"]
        game_type_str = context.user_data["game_type"]
        is_team_game = context.user_data["is_team_game"]
        players = context.user_data["players"]
        rankings = context.user_data["rankings"]

        # Calculate points automatically
        awarding = award_points_for_game(game_type_str, players, rankings)

        # Insert a row per player
        for p, r in zip(players, rankings):
            points_earned = awarding.get(p, 0)
            add_game_entry(
                game_name=game_name,
                date=date_str,
                is_team_game=is_team_game,
                game_type=game_type_str,
                player_name=p,
                ranking=r,
                all_players_str=", ".join(players),
                points_awarded=points_earned,
            )

        # Build result message
        result_msg = (
                f"Game '{game_name}' on {date_str} recorded.\n"
                "Points awarded:\n" +
                "\n".join(f"{p}: +{awarding[p]}" for p in players)
        )
        await update.message.reply_text(result_msg)
        context.user_data.clear()


# ---------------------------
#   GENERIC MESSAGE HANDLER
# ---------------------------
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fallback message handler for continuing either /add (manual) or /add_auto (auto) workflow.
    """
    command = context.user_data.get("command")
    if command == "add":
        await handle_add_points_manual(update, context)
    elif command == "add_auto":
        await handle_add(update, context)
    else:
        # No active conversation
        pass


# ---------------------------
#   /view, /remove, /leaderboard
# ---------------------------
async def view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /view command: Display all recorded games.
    """
    games = get_games()
    if not games:
        await update.message.reply_text("No games found.")
        return

    lines = []
    for row in games:
        game_id = row[0]
        g_name = row[1]
        winner = row[2]
        g_date = row[3]
        is_team = row[4]
        rank = row[5]
        all_players = ", ".join(capitalize_name(p) for p in row[6].split(", "))
        g_type = row[7]
        pts = row[8]
        lines.append(
            f"[ID {game_id}] {g_name} on {g_date} ({g_type}), rank={rank}\n"
            f"   Player={winner}, +{pts} points, "
            f"All={all_players}, is_team={is_team}"
        )

    await update.message.reply_text("Games:\n\n" + "\n\n".join(lines))


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /remove - Let the user select an entry to remove (either from 'games' or 'adjustments').
    We'll build an inline keyboard listing both.
    """
    # 1) Get game rows
    game_rows = get_games()  # returns list of (id, name, winner, date, is_team_game, ranking, players, game_type, points_awarded)
    # 2) Get adjustment rows
    adj_rows = get_adjustments()  # returns list of (id, player_name, date, points, reason)

    # We'll build a single keyboard with buttons for each item
    keyboard = []

    # First, list all GAMES
    if game_rows:
        for g in game_rows:
            g_id = g[0]
            g_name = g[1]
            winner = g[2]
            g_date = g[3]
            pts = g[8]  # points_awarded
            # Format any label you want to display
            label = f"(Game) ID {g_id}: {g_name} - {winner} ({g_date}) +{pts}pts"
            # callback_data = "game_<id>"
            callback_data = f"game_{g_id}"
            keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    else:
        # Optionally, you can add a line if no games found
        pass

    # Then, list all ADJUSTMENTS
    if adj_rows:
        for a in adj_rows:
            a_id = a[0]
            player_name = a[1]
            adj_date = a[2]
            points = a[3]
            reason = a[4] or ""
            # Format the label
            label = f"(Adj) ID {a_id}: {player_name.title()} => {points:+.1f} ({adj_date})"
            if reason:
                label += f" [{reason}]"
            # callback_data = "adj_<id>"
            callback_data = f"adj_{a_id}"
            keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    else:
        # Optionally, add a line if no adjustments found
        pass

    # If we have NOTHING in the keyboard, let the user know
    if not keyboard:
        await update.message.reply_text("No games or adjustments found to remove.")
        return

    # Otherwise, send them the keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Select an entry to remove (game or adjustment):",
        reply_markup=reply_markup
    )


async def handle_remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    A single callback to handle removal of either a game row or an adjustment row.
    We'll parse the callback data which might be 'game_123' or 'adj_45'.
    """
    query = update.callback_query
    await query.answer()

    # Example callback_data = 'game_5' or 'adj_10'
    data = query.data

    # Distinguish
    if data.startswith("game_"):
        try:
            game_id = int(data.split("_")[1])
        except ValueError:
            await query.edit_message_text("Error: Invalid game ID in callback.")
            return
        # Remove from 'games' table
        delete_game(game_id)
        await query.edit_message_text(text=f"Game entry with ID {game_id} has been removed.")

    elif data.startswith("adj_"):
        try:
            adj_id = int(data.split("_")[1])
        except ValueError:
            await query.edit_message_text("Error: Invalid adjustment ID in callback.")
            return
        # Remove from 'adjustments' table
        remove_adjustment(adj_id)
        await query.edit_message_text(text=f"Adjustment entry with ID {adj_id} has been removed.")
    else:
        # Unrecognized callback_data
        await query.edit_message_text("Error: Unknown callback data!")
        return


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /leaderboard command: Show overall points and solo-only leaderboards.
    Mark players with fewer than 3 games as Provisional.
    """
    overall, solo_only, game_count = compute_leaderboards()

    msg = ["<b>Overall Leaderboard</b>"]
    rank = 1
    for (player, pts, is_prov) in overall:
        display_name = capitalize_name(player)
        if is_prov:
            msg.append(f"{rank}. {display_name} - {pts:.1f} pts (Provisional)")
        else:
            classification = classify_player(player, pts, game_count[player])
            msg.append(f"{rank}. {display_name} - {pts:.1f} pts ({classification})")
        rank += 1

    msg.append("")
    msg.append("<b>Solo-Only Leaderboard</b>")
    rank = 1
    for (player, pts, is_prov) in solo_only:
        display_name = capitalize_name(player)
        if is_prov:
            msg.append(f"{rank}. {display_name} - {pts:.1f} pts (Provisional)")
        else:
            msg.append(f"{rank}. {display_name} - {pts:.1f} pts")
        rank += 1

    await update.message.reply_text("\n".join(msg), parse_mode="HTML")


# ---------------------------
#         MAIN ENTRY
# ---------------------------
def main():
    """
    Main entry point. Sets up the bot, registers command handlers,
    and starts polling for updates.
    """
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # Make sure the DB is initialized
    init_db()

    application = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_points_manual))  # Manual points
    application.add_handler(CommandHandler("add_auto", add))  # Auto points
    application.add_handler(CommandHandler("view", view))
    application.add_handler(CommandHandler("view_adjustments", view_adjustments))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("comeback", random_comeback))
    application.add_handler(CommandHandler("adjust", adjust_command))

    # Player handlers
    application.add_handler(CommandHandler("dom", dom_joke_handler))
    application.add_handler(CommandHandler("xuanli", xuanli_handler))
    application.add_handler(CommandHandler("cawin", cawin_handler))
    application.add_handler(CommandHandler("junming", junming_handler))
    application.add_handler(CommandHandler("austen", austen_handler))

    # Message handler for continuing add/add_auto conversation
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # Callback query handler (used by /remove to confirm deletion)
    application.add_handler(CallbackQueryHandler(handle_remove_callback))

    # Start the bot
    application.run_polling(poll_interval=1)


if __name__ == "__main__":
    main()
