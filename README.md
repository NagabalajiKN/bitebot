# BiteBot

BiteBot is a food assistant Telegram bot that helps organizations make smart meal plans to avoid food wastage based on how many people will eat a meal. It can also assist with recipes, food suggestions, and managing leftovers. Additionally, it sends notifications to an NGO when there's leftover food available for pickup.

## Features

### Eater Registration
- Allows users to register as eaters and select their mess.
- Eaters can confirm their meals for breakfast, lunch, and dinner.

### Mess Registration
- Allows mess managers to register and manage meal confirmations.

### Meal Confirmation
- Eaters can confirm their meals for breakfast, lunch, and dinner.

### Macro Calculation
- Provides macro nutrient splits based on user inputs.

### Order Management
- Mess managers can view order counts and order lists.

### Leftover Management
- Sends notifications to NGOs about leftover food.

## Getting Started

### Prerequisites
- Python 3.7+
- MongoDB
- Telegram bot token
- Gemini API key

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/bitebot.git
    cd bitebot
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables. Create a `.env` file in the project root directory and add the following:
    ```bash
    API_KEY=your_telegram_bot_token
    MONGO_URI=your_mongodb_uri
    GEMINI_API_KEY=your_gemini_api_key
    ```

### Usage

Start the bot:
```bash
python bot.py
