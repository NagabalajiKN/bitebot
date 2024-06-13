import os
import time
import schedule
import threading
from dotenv import load_dotenv
import telebot
from pymongo import MongoClient
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Get the bot token and MongoDB URI from environment variables
bot_token = os.getenv('API_KEY')
mongo_uri = os.getenv('MONGO_URI')

# Initialize the bot and MongoDB client
bot = telebot.TeleBot(bot_token)
# Configure the generation parameters for the Gemini model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Generative Model with the given configuration and instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Try to keep all conversations as food and food assistant centric as possible. For all the questions like will you marry me and all those senseless questions give a sarcastic answer and say you are just a food guide. If people ask what can you do mention your name is Bite Bot 🍔 who helps organizations make a smart meal plan to avoid food wastage based on how many will eat a meal. Also mention you can help them with recipes, food suggestions, and almost anything related to foods. And when you are printing like list of foods or something like that make sure you print it in form of list. and include emojis wherever needed related to the message. Also keep the messages and explanations a little shorter until asked to explain. Lets not overwhelm the reader with too much to read.",
)

commands = [
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Get help"),
    BotCommand("ai", "Chat with AI")
]

# Set commands for the bot
bot.set_my_commands(commands)
client = MongoClient(mongo_uri)
db = client['bitebot_db']  # Database name
eaters_collection = db['eaters']  # Collection name
messes_collection = db['messes']

def airesponse(input):
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input)
    return response.text
# Temporary storage for user data
user_data = {}


# Check if the user exists in the database
def check_eater_exists(user_id):
    user = eaters_collection.find_one({"user_id": user_id})
    return user is not None

# Check if the mess exists in the database
def check_mess_exists(mess_id):
    mess = messes_collection.find_one({"mess_id": mess_id})
    return mess is not None

# Add the eater to the database
def add_eater(user_id, e_name, mess_name):
    try:
        eaters_collection.insert_one({"user_id": user_id, "e_name": e_name, "mess_name": mess_name})
        print("Eater added to database")
    except Exception as e:
        print(f"Error adding eater to database: {e}")

def add_mess(mess_id, m_name):
    try:
        messes_collection.insert_one({"mess_id": mess_id, "m_name": m_name})
        print("Mess added to database")
    except Exception as e:
        print(f"Error adding mess to database: {e}")

# Handle type input
def handle_type_input(message):
    user_type = message.text.lower()
    if user_type == "eater":
        bot.send_message(message.chat.id, "🍽️ Great! Please enter your name:")
        bot.register_next_step_handler(message, handle_name_input_eater)
    else:
        bot.send_message(message.chat.id, "🍴 Awesome! Please enter your mess name:")
        bot.register_next_step_handler(message, handle_name_input_mess)

# Handle start command
@bot.message_handler(func=lambda message: message.text == "/start")
def handle_start(message):
    user_id = message.from_user.id
    if check_eater_exists(user_id):
        handle_menu(message)
    elif check_mess_exists(user_id):
        handle_menu_mess(message)
    else:
        bot.send_message(message.chat.id, "Welcome to BiteBot! Are you an eater or a mess? 🍽️")
        bot.register_next_step_handler(message, handle_type_input)

@bot.message_handler(commands=["ai"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hi there! I'm Bite Bot, your food assistant. How can I help you today? 🍽️",
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    response = airesponse(user_input)
    bot.reply_to(message, response)


# Handle name input for eater
def handle_name_input_eater(message):
    user_id = message.from_user.id
    e_name = message.text
    user_data[user_id] = {'e_name': e_name}  # Store e_name temporarily
    messes = messes_collection.find()
    markup = InlineKeyboardMarkup()
    for mess in messes:
        mess_name = mess["m_name"]
        markup.add(InlineKeyboardButton(f"🍴 {mess_name}", callback_data=f'select_mess_{mess_name}'))
    bot.send_message(message.chat.id, "Please choose your mess:", reply_markup=markup)

# Handle name input for mess
def handle_name_input_mess(message):
    mess_id = message.from_user.id
    m_name = message.text
    add_mess(mess_id, m_name)
    handle_menu_mess(message)

@bot.message_handler(commands=['menu'])
def handle_menu_mess(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Get Order Count", callback_data='mess_option1'))
    markup.add(InlineKeyboardButton("📋 Get Order List", callback_data='mess_option2'))
    markup.add(InlineKeyboardButton("🍛 Leftover Management", callback_data='mess_option3'))
    bot.send_message(message.chat.id, "🍽️ Mess Menu 🍽️\nPlease choose an option:", reply_markup=markup)

# Handle menu command for eaters
@bot.message_handler(commands=['e_menu'])
def handle_menu(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Confirm a Meal", callback_data='eater_option1'))
    markup.add(InlineKeyboardButton("💪 Macro Split", callback_data='eater_option2'))
    bot.send_message(message.chat.id, "🍽️ Eater Menu 🍽️\nPlease choose an option:", reply_markup=markup)

# Handle button clicks
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    if call.data.startswith('select_mess_'):
        mess_name = call.data.split('select_mess_')[1]
        e_name = user_data[user_id]['e_name']  # Retrieve e_name from temporary storage
        add_eater(user_id, e_name, mess_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🍽️ Mess {mess_name} selected and saved!")
        
        user_data.pop(user_id, None)  # Clear temporary storage for the user
        handle_menu(call.message)
    elif call.data.startswith('eater_option'):
        handle_eater_option(call)
    elif call.data.startswith('mess_option'):
        handle_mess_option(call)
    elif call.data.startswith('activity_'):
        handle_activity_level(call)
    elif call.data.startswith('goal_'):
        handle_body_goal(call)


def handle_eater_option(call):
    if call.data == 'eater_option1':
        menu = ["🥐 Breakfast : Dosa, Pasta", "🍲 Lunch : Biryani, Spaghetti", "🍛 Dinner : Curd rice, Ramen"]
        menu_text = "\n".join(menu)
        bot.send_message(call.message.chat.id, menu_text)
        handle_confirm_meal(call)

    elif call.data == 'eater_option2':
        bot.send_message(call.message.chat.id, "Please enter your height in cm:")
        bot.register_next_step_handler(call.message, handle_height_input)
    elif call.data.startswith('eater_option1_'):
        handle_meal_option(call)

def handle_mess_option(call):
    if call.data == 'mess_option1':
        get_order_count(call)
    elif call.data == 'mess_option2':
        get_order_list(call)
    elif call.data == 'mess_option3':
        handle_leftover_management(call)

# Handle confirm a meal option
def handle_confirm_meal(call):
    user_id = call.from_user.id
    e_name = eaters_collection.find_one({"user_id": user_id})["e_name"]
    mess_name = eaters_collection.find_one({"user_id": user_id})["mess_name"]

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🥐 Breakfast", callback_data='eater_option1_breakfast'))
    markup.add(InlineKeyboardButton("🍲 Lunch", callback_data='eater_option1_lunch'))
    markup.add(InlineKeyboardButton("🍛 Dinner", callback_data='eater_option1_dinner'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please choose a meal option:", reply_markup=markup)

# Handle meal option selection
def handle_meal_option(call):
    user_id = call.from_user.id
    e_name = eaters_collection.find_one({"user_id": user_id})["e_name"]
    mess_name = eaters_collection.find_one({"user_id": user_id})["mess_name"]
    option = call.data.split('_')[2]  # Corrected index to 2
    orders_collection = db['orders']

    if orders_collection.find_one({"e_name": e_name, "m_name": mess_name, "option": option}):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🍽️ Meal option for {e_name} already exists!")
    else:
        orders_collection.insert_one({"e_name": e_name, "m_name": mess_name, "option": option})
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🍽️ Meal option '{option}' confirmed and added to orders collection!")
        bot.send_sticker(chat_id=call.message.chat.id, sticker='CAACAgIAAxkBAAICCWZjWiSE33paDp-wbCC_7tvOAAEzkgAC7hQAAuNVUEk4S4qtAhNhvDUE')

# Handle height input
# Handle height input
# Temporary storage for user data
user_data = {}

# Handle height input
def handle_height_input(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['height'] = message.text  # Store height temporarily
    
    bot.send_message(message.chat.id, "Please enter your weight in kg:")
    bot.register_next_step_handler(message, handle_weight_input)

# Handle weight input
def handle_weight_input(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['weight'] = message.text  # Store weight temporarily
  
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Sedentary (little or no exercise)", callback_data='activity_sedentary'))
    markup.add(InlineKeyboardButton("Lightly active (light exercise/sports 1-3 days/week)", callback_data='activity_lightly_active'))
    markup.add(InlineKeyboardButton("Moderately active (moderate exercise/sports 3-5 days/week)", callback_data='activity_moderately_active'))
    markup.add(InlineKeyboardButton("Very active (hard exercise/sports 6-7 days a week)", callback_data='activity_very_active'))
    markup.add(InlineKeyboardButton("Super active (very hard exercise/sports & a physical job)", callback_data='activity_super_active'))
    bot.send_message(message.chat.id, "Please choose your activity level:", reply_markup=markup)

# Handle activity level
@bot.callback_query_handler(func=lambda call: call.data.startswith('activity_'))
def handle_activity_level(call):
    user_id = call.from_user.id
    activity_level = call.data.split('_')[1]
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['activity_level'] = activity_level  # Store activity level temporarily
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Fat Loss", callback_data='goal_fat_loss'))
    markup.add(InlineKeyboardButton("Muscle Gain", callback_data='goal_muscle_gain'))
    markup.add(InlineKeyboardButton("Maintenance", callback_data='goal_maintenance'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Please choose your body goal:", reply_markup=markup)

# Handle body goal
@bot.callback_query_handler(func=lambda call: call.data.startswith('goal_'))
def handle_body_goal(call):
    user_id = call.from_user.id
    goal = call.data.split('_')[1]
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['goal'] = goal  # Store goal temporarily
    
    height = float(user_data[user_id].get('height', 0))  # Get height if available, default to 0 if not found
    weight = float(user_data[user_id].get('weight', 0))  # Get weight if available, default to 0 if not found
    activity_level = user_data[user_id].get('activity_level')
    goal = user_data[user_id].get('goal')

    

    if height > 0 and weight > 0 and activity_level and goal:
        # Calculate BMR using Mifflin-St Jeor Equation
        BMR = 10 * weight + 6.25 * height - 5 * 25 + 5  # Assuming age is 25 and male
        activity_factors = {
            'sedentary': 1.2,
            'lightly': 1.375,
            'moderately': 1.55,
            'very': 1.725,
            'super': 1.9
        }
        TDEE = BMR * activity_factors[activity_level]

        if goal == 'fat':
            TDEE *= 0.8  # Decrease by 20%
        elif goal == 'muscle':
            TDEE *= 1.15  # Increase by 15%

        # Calculate macros
        proteins = weight * 2.2  # grams of protein
        fats = TDEE * 0.25 / 9  # grams of fat (25% of calories from fat)
        carbs = (TDEE - (proteins * 4 + fats * 9)) / 4  # grams of carbs

        bot.send_message(call.message.chat.id, f"Based on your inputs, your daily intake should be:\nCalories: {int(TDEE)} kcal\nProteins: {int(proteins)} g\nFats: {int(fats)} g\nCarbs: {int(carbs)} g")
    else:
        bot.send_message(call.message.chat.id, "Please provide all necessary inputs before calculating macros.")

# Calculate and send macros
def calculate_macros(message):
    user_id = message.from_user.id
    if user_id in user_data:
        height = float(user_data[user_id].get('height', 0))  # Get height if available, default to 0 if not found
        weight = float(user_data[user_id].get('weight', 0))  # Get weight if available, default to 0 if not found
        activity_level = user_data[user_id].get('activity_level')
        goal = user_data[user_id].get('goal')

       

        if height > 0 and weight > 0 and activity_level and goal:
            # Calculate BMR using Mifflin-St Jeor Equation
            BMR = 10 * weight + 6.25 * height - 5 * 25 + 5  # Assuming age is 25 and male
            activity_factors = {
                'sedentary': 1.2,
                'lightly': 1.375,
                'moderately': 1.55,
                'very': 1.725,
                'super': 1.9
            }
            TDEE = BMR * activity_factors[activity_level]

            if goal == 'fat':
                TDEE *= 0.8  # Decrease by 20%
            elif goal == 'muscle':
                TDEE *= 1.15  # Increase by 15%

            # Calculate macros
            proteins = weight * 2.2  # grams of protein
            fats = TDEE * 0.25 / 9  # grams of fat (25% of calories from fat)
            carbs = (TDEE - (proteins * 4 + fats * 9)) / 4  # grams of carbs

            bot.send_message(message.chat.id, f"Based on your inputs, your daily intake should be:\nCalories: {int(TDEE)} kcal\nProteins: {int(proteins)} g\nFats: {int(fats)} g\nCarbs: {int(carbs)} g")
        else:
            bot.send_message(message.chat.id, "Please provide all necessary inputs before calculating macros.")
    else:
        bot.send_message(message.chat.id, "User data not found. Please start again.")
        print(f"User data not found for user {user_id}")  # Additional debug statement

# Get the count of orders for the mess
def get_order_count(call):
    mess_name = messes_collection.find_one({"mess_id": call.from_user.id})["m_name"]
    orders_collection = db['orders']
    order_count = orders_collection.count_documents({"m_name": mess_name})
    bot.send_message(call.message.chat.id, f"📊 The count of orders for {mess_name} is {order_count}")

# Get the list of orders for the mess
def get_order_list(call):
    mess_name = messes_collection.find_one({"mess_id": call.from_user.id})["m_name"]
    orders_collection = db['orders']
    order_list = orders_collection.find({"m_name": mess_name})
    message = f"📋 Orders for {mess_name}:\n"
    for order in order_list:
        e_name = order["e_name"]
        option = order["option"]
        message += f"- {e_name}: {option}\n"
    bot.send_message(call.message.chat.id, message)

def handle_leftover_management(call):
    # Prompt for the amount of leftover food
    bot.send_message(call.message.chat.id, "🍛 Please enter the amount of leftover food (in kilograms):")
    bot.register_next_step_handler(call.message, handle_leftover_amount)

def handle_leftover_amount(message):
    # Get the amount of leftover food
    amount = message.text
    try:
        amount = float(amount)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid input. Please enter a numerical value for the amount of leftover food in kilograms.")
        return

    # Send the message to the NGO
    send_leftover_message(amount)
    bot.send_message(message.chat.id, f"✅ Leftover management complete! A message has been sent to our partner NGOs about {amount}kg of leftover food.")

def send_leftover_message(amount):
    # Assuming we have a predefined NGO phone number
    NGO_PHONE_NUMBER = "+919455295823"
    # Here you would integrate with an SMS API to send the message
    # For the sake of this example, we'll just print the message to the console
    message = f"Hello NGO, we have {amount}kg of leftover food available for pickup."
    print(f"Sending message to {NGO_PHONE_NUMBER}: {message}")
    # If using an actual SMS API, the code would look something like this:
    # sms_api.send_message(to=NGO_PHONE_NUMBER, message=message)

# Schedule reminder function
def schedule_reminder():
    while True:
        schedule.run_pending()
        time.sleep(1)

def send_reminder():
    for eater in eaters_collection.find():
        user_id = eater["user_id"]
        bot.send_message(user_id, "🔔 Ting tong! Time for dinner!!")

# Schedule the reminder at 8:45 PM every day
schedule.every().day.at("20:45").do(send_reminder)

# Start the scheduler in a separate thread
reminder_thread = threading.Thread(target=schedule_reminder)
reminder_thread.start()

# Start polling
bot.polling()
