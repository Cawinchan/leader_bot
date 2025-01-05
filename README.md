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
