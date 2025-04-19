# My AI Assistant Bot

Welcome to the **My AI Assistant Bot** repository! This project is an AI-powered Telegram bot designed to help users interact with and learn about Antenhe Sileshi's personal portfolio and projects. The bot is capable of answering questions, sharing project details, and providing personalized responses based on pre-defined information about Antenhe's work, expertise, and achievements.

## Features

- **Interactive Assistant**: Users can interact with the bot to learn more about Antenhe Sileshi’s professional journey, skills, and projects.
- **Command-Based Interface**: The bot supports several commands to retrieve specific information:
  - `/start`: Start the bot and receive a welcome message.
  - `/help`: Provides guidance on how to interact with the bot.
  - `/projects`: Displays a list of key projects Antenhe has worked on.
  - `/ask`: Ask the bot any question about Antenhe, and get an AI-powered response.
- **Groq API Integration**: The bot uses Groq's API for natural language processing and to generate personalized answers based on a detailed portfolio prompt.
- **Environment Configuration**: The bot is fully configurable through environment variables (e.g., Telegram bot token, Groq API key) for easy deployment in any environment.

## How It Works

The bot is built using Python with the `python-telegram-bot` library and integrates with the **Groq AI API**. The bot can respond to user queries by providing predefined responses from the portfolio or by utilizing the Groq API to generate dynamic answers. 

### System Prompt for AI Responses
The bot uses a custom system prompt to answer queries, ensuring that the information it provides is accurate and relevant to Antenhe’s skills, projects, and expertise.

## Requirements

Before running the bot, ensure you have the following:

- Python 3.8+ (or any compatible version)
- An active Telegram bot token (created via [BotFather](https://core.telegram.org/bots#botfather))
- A **Groq API key** to enable AI-powered responses.
- The following Python packages:
  - `python-dotenv` for environment variable management.
  - `python-telegram-bot` for Telegram bot interaction.
  - `requests` for making API calls to Groq.
  - `aiohttp` for handling asynchronous tasks (if you're integrating async features).

## Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/yourusername/my-ai-assistant-bot.git
