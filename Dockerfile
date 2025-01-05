# Use a minimal Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot script
COPY . /app/

# Copy the SQLite database file to the persistent volume path
COPY board_game_tracker.db /data/

# Expose port (not strictly needed for this bot but good practice)
EXPOSE 8080

# Run the bot
CMD ["python", "bot.py"]