# Board Game Tracker Bot

The **Board Game Tracker Bot** is a Telegram bot designed to make tracking board game sessions fun and efficient. Whether you're playing with friends casually or competing seriously, this bot records your games, calculates scores, and keeps leaderboards up to date — with a touch of humor!

## Features

- **Game Logging**: Record board game sessions manually or with automatic point calculation.
- **Game Types**: Supports solo, team, and pair-based games with flexible ranking and scoring systems.
- **Leaderboards**: Displays overall and solo-only rankings with provisional status for new players.
- **Player Classifications**: Categorizes players into types (e.g., Type A, B, C) based on average scores.
- **Humor Included**: Generates random comebacks like "You den lah!" or "Your mother gay" for lighthearted interactions.
- **Database-Powered**: Stores game data in an SQLite database for easy retrieval and updates.

## Commands

| Command       | Description                                                                              |
|---------------|------------------------------------------------------------------------------------------|
| `/start`      | Displays the welcome message and introduces the bot's features.                         |
| `/add`        | Start recording a game and manually assign points for each player.                      |
| `/add_auto`   | Automatically calculate points based on rankings and record the game.                   |
| `/view`       | Displays all recorded games with detailed information.                                  |
| `/remove`     | Lets you select and delete a game entry via an inline menu.                             |
| `/leaderboard`| Shows overall and solo-only leaderboards with rankings and classifications.             |
| `/comeback`   | Generates a random, funny comeback from a predefined list.                              |
| `/dom`        | A fun command for your friend Dom (or anyone else).                                     |
| `/help`       | Displays the list of commands and features.                                             |

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/board-game-tracker-bot.git
   cd board-game-tracker-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your TELEGRAM_BOT_TOKEN as a env variable
   ```bash
   export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

## How It Works

1. Use `/add` or `/add_auto` to record a game.
2. The bot saves game details (name, players, rankings, and points) to an SQLite database.
3. Check your progress with `/view` or `/leaderboard`.
4. Remove outdated entries with `/remove`.
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
```

## Requirements

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://core.telegram.org/bots#botfather))

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Have fun tracking your board games and climbing the leaderboard! 🎲🏆
