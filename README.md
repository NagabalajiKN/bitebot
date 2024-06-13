BiteBot is a food assistant Telegram bot that helps organizations make smart meal plans to avoid food wastage based on how many people will eat a meal. It can also assist with recipes, food suggestions, and managing leftovers. Additionally, it sends notifications to an NGO when there's leftover food available for pickup.

Features
Eater Registration: Allows users to register as eaters and select their mess.
Mess Registration: Allows mess managers to register and manage meal confirmations.
Meal Confirmation: Eaters can confirm their meals for breakfast, lunch, and dinner.
Macro Calculation: Provides macro nutrient splits based on user inputs.
Order Management: Mess managers can view order counts and order lists.
Leftover Management: Sends notifications to NGOs about leftover food.
Getting Started
Prerequisites
Python 3.7+
MongoDB
Telegram bot token
Gemini API key
Installation
Clone the repository: bash git clone https://github.com/yourusername/bitebot.git cd bitebot

Create and activate a virtual environment: bash python -m venv venv source venv/bin/activate # On Windows, use venv\Scripts\activate

Install the required packages: bash pip install -r requirements.txt

Set up your environment variables. Create a .env file in the project root directory and add the following:

API_KEY=your_telegram_bot_token MONGO_URI=your_mongodb_uri GEMINI_API_KEY=your_gemini_api_key

Usage
Start the bot: bash python bot.py

Interact with the bot on Telegram using the commands:

/start - Start the bot and register as an eater or mess.
/ai - Chat with the AI food assistant.
/menu - Access the mess manager menu.
/e_menu - Access the eater menu.
Functionality Overview
AI Response
BiteBot uses the Gemini model to provide food-related assistance. It helps with recipes, food suggestions, and meal planning.

Eater Registration
Users register as eaters and select their mess.
Eaters confirm their meals for breakfast, lunch, and dinner.
Mess Management
Mess managers register their mess.
View order counts and order lists.
Manage leftovers and notify NGOs about leftover food.
Macro Calculation
Users provide height, weight, activity level, and body goals to receive macro nutrient splits.
Leftover Management
Sends a Telegram message to the NGO contact when there's leftover food.
Scheduler
The bot includes a scheduler that sends a reminder for dinner every day at 8:45 PM.

Contributing
Contributions are welcome! Please open an issue or submit a pull request.

License
This project is licensed under the MIT License.

Acknowledgements
pyTelegramBotAPI - A simple, but extensible Python implementation for the Telegram Bot API.
pymongo - Python driver for MongoDB.
schedule - Python job scheduling for humans.
