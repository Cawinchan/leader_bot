# Board Game Tracker Bot

The **Board Game Tracker Bot** is a Telegram bot designed to make tracking board game sessions fun and efficient. Whether you're playing with friends casually or competing seriously, this bot records your games, calculates scores, and keeps leaderboards up to date — with a touch of humor!

## Features

- **Game Logging**: Record board game sessions manually or with automatic point calculation.
- **Game Types**: Supports solo, team, and pair-based games with flexible ranking and scoring systems.
- **Leaderboards**: Displays overall and solo-only rankings with provisional status for new players.
- **Player Classifications**: Categorizes players into types (e.g., Type A, B, C) based on average scores.
- **Manual Adjustments**: Add or subtract points from any player at any time, outside of a recorded game.
- **Humor Included**: Generates random comebacks like "You den lah!" or "Your mother gay" for lighthearted interactions.
- **Database-Powered**: Stores game data in an SQLite database for easy retrieval and updates.

## Commands

| Command             | Description                                                                                           |
|---------------------|-------------------------------------------------------------------------------------------------------|
| `/start`            | Displays the welcome message and introduces the bot's features.                                      |
| `/add`              | Start recording a game and manually assign points for each player.                                   |
| `/add_auto`         | Automatically calculate points based on rankings and record the game.                                |
| `/adjust`           | Manually add or subtract points for a player (e.g., `/adjust bob -5 tardiness`).                     |
| `/view`             | Displays all recorded games with detailed information.                                               |
| `/view_adjustments` | Shows all manual plus/minus adjustments that have been recorded.                                     |
| `/remove`           | Lets you select and delete **either** a game entry **or** an adjustment, via an inline menu.          |
| `/leaderboard`      | Shows overall and solo-only leaderboards with rankings and classifications.                          |
| `/comeback`         | Generates a random, funny comeback from a predefined list.                                           |
| `/dom`              | A fun command for your friend Dom (or anyone else).                                                  |
| `/help`             | Displays the list of commands and features.                                                          |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Cawinchan/leader_bot.git
   cd board-game-tracker-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your `TELEGRAM_BOT_TOKEN` as an environment variable:
   ```bash
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## How It Works

1. Use `/add` or `/add_auto` to record a game. The bot saves details (name, players, rankings, points) in an SQLite database.
2. **Need to penalize or reward points outside of a game?** Use `/adjust` (e.g., `/adjust alice -3 oversleeping`) to directly modify a player's score.
3. Check your progress with `/view` (for games) or `/view_adjustments` (for adjustments).  
4. Remove outdated entries (either game or adjustment) with a unified `/remove`.
5. Enjoy random comebacks or jokes using `/comeback` or `/dom`.

## Example

```plaintext
User: /add_auto
Bot: What game was played? (e.g., 'Catan')
User: Chess
Bot: Is this a 'solo' (1v1v1v1), 'team' (4v1), or 'pair' (2v2 or 2v3v2) game?
User: solo
Bot: Who played? Provide player names separated by commas.
User: Alice, Bob, Charlie, Dave
Bot: Now enter the rankings for each player in the same order.
User: 1, 2, 3, 4
Bot: What is the date of the game? (YYYY-MM-DD)
User: today
Bot: Game 'Chess' on 2025-01-05 recorded.
Points awarded:
Alice: +6
Bob: +3
Charlie: +1
Dave: +0

User: /adjust Charlie 5 side-bet
Bot: 5.0 points have been subtracted from Charlie.
```

*(**Note**: If you use a negative number in `/adjust`, points are subtracted; if you use a positive number, points are added!)*

## Requirements

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://core.telegram.org/bots#botfather))

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Have fun tracking your board games (and dishing out random comebacks) while climbing the leaderboard! 🎲🏆
```

### Key Updates
- **Added** the `/adjust` and `/view_adjustments` commands to the feature list and command table.  
- **Explained** the new manual adjustments feature in both the *Features* section and the *Commands* table.  
- **Mentioned** in *How It Works* that `/adjust` can add or subtract points outside of games.  
- **Highlighted** that `/remove` now handles both games **and** adjustments.  

With these changes, your `README.md` will accurately reflect the **new features** you’ve introduced. Enjoy!



