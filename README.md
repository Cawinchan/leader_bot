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

Below is an **example** section you can add to your README, detailing **step-by-step instructions** for deploying your bot on [Fly.io](https://fly.io). Feel free to adjust for your specific workflow or preferences.

---

## Deploying on Fly.io

### 1. Install **flyctl**

**macOS, Linux, or WSL** (install latest version):
```bash
curl -L https://fly.io/install.sh | sh
```

**Install the latest pre-release version**:
```bash
curl -L https://fly.io/install.sh | sh -s pre
```

**Install a specific version (example: 0.0.200)**:
```bash
curl -L https://fly.io/install.sh | sh -s 0.0.200
```

**Windows**:  
Open PowerShell and run:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

> **Note**: After installation, ensure `flyctl` is accessible in your terminal (you may need to restart your shell or add it to your PATH).

---

### 2. Authenticate with Fly.io

```bash
fly auth login
```
Follow the prompts to sign in with your Fly.io account (or create one if needed).

---

### 3. Initialize Your Fly App

Inside your **leader_bot** project directory:

```bash
flyctl launch
```

You’ll be prompted to:
1. Choose a **unique name** for your app (e.g., `telegram-bot`).
2. Select a **region** (for example, `sin` for Singapore).
3. DO NOT create a new `fly.toml` file.
4. DO NOT create a new .gitignore file

> **Tip**: If you already created an app on Fly.io’s dashboard, you can skip naming or region prompts by specifying `--name` and `--region` flags to `flyctl launch`.

---

### 4. Configure Your Resources

1. **Instances**:
   ```bash
   flyctl scale count 1
   ```
   This ensures only one instance of your bot is running to keep costs low.

---

### 5. Set Your Secrets

Your bot token must be kept private, so store it as a Fly.io **secret**:
```bash
flyctl secrets set TELEGRAM_BOT_TOKEN=your_actual_token
```
Replace `your_actual_token` with the actual token from [@BotFather](https://core.telegram.org/bots#botfather).

---

### 6. Deploy Your Bot

When ready, run:
```bash
flyctl deploy
```
Fly.io will build and deploy your Docker image (or use a builder like herokuish or Nixpacks, depending on your `fly.toml` config).

---

### 7. Monitoring & Logs

1. **View logs**:
   ```bash
   flyctl logs
   ```
   This streams your application logs in real-time.

2. **Monitor application health**:
   ```bash
   flyctl monitor
   ```
   This gives you a quick overview of CPU, memory usage, and other metrics in real time.

3. **Check app status**:
   ```bash
   flyctl status
   ```
   See the current status of your running instance(s).

---

### 8. Common Next Steps

- **Updating**: Make changes, then run `flyctl deploy` again. Fly.io will roll out your new version.
- **Scaling**: 
  - Increase memory or CPU if your bot needs more resources.  
  - Add more instances if your usage spikes.  
- **Secrets**: Update them anytime:
  ```bash
  flyctl secrets set NEW_SECRET=value
  ```
  Then Fly.io restarts your app with the updated environment variables.

---

With this, your **Board Game Tracker Bot** should be up and running on Fly.io, ready to track games and entertain users!

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



