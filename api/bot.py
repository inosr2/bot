import os
import telebot
import google.generativeai as genai
from flask import Flask, request, jsonify

# Get API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing necessary environment variables!")

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Create Gemini AI model
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

@app.route('/api/webhook', methods=['POST'])
def webhook():
    try:
        # Parse incoming webhook data
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        
        # Process the update
        bot.process_new_updates([update])
        
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Welcome message handler
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """
🌟 **Welcome to the AI Lina Bot!** 🌟

I'm here to assist, entertain, and amaze you! Here's what I can do:  

✨ **Ask Me Anything**  
Use `/ask` to ask any question, and I'll provide an AI-powered answer!  

🎨 **Imagine and Create**  
Use `/imagine` to describe something, and I'll paint you a word picture.  

🧮 **Solve Math Problems**  
Need math help? Use `/math` and send your math problem for step-by-step solutions.  

🌍 **Translate Text**  
Say it in another language! Use `/translate` and provide a target language + text.

🔮 **Chat Freely**  
Just message me directly—I'm all ears and ready to assist!  

❓ **Help**  
Use `/help` anytime to see this menu again.  

🚀 Let's get started!  
Type a command or send me a message and let the magic begin! ✨
    """
    bot.reply_to(message, welcome_text)

# AI Question Answering Handler
@bot.message_handler(commands=['ask'])
def handle_question(message):
    try:
        question = message.text.split(' ', 1)[1]
        response = model.generate_content(question)
        bot.reply_to(message, response.text)
    except IndexError:
        bot.reply_to(message, "Please provide a question after /ask")
    except Exception as e:
        bot.reply_to(message, f"Sorry, an error occurred: {str(e)}")

# Image Description Generator
@bot.message_handler(commands=['imagine'])
def imagine_description(message):
    try:
        prompt = message.text.split(' ', 1)[1]
        description_response = model.generate_content(f"Describe a creative scene: {prompt}")
        bot.reply_to(message, description_response.text)
    except IndexError:
        bot.reply_to(message, "Please provide a description prompt after /imagine")
    except Exception as e:
        bot.reply_to(message, f"Imagination error: {str(e)}")

# Math Problem Solver
@bot.message_handler(commands=['math'])
def solve_math(message):
    try:
        problem = message.text.split(' ', 1)[1]
        solution_response = model.generate_content(f"Solve this math problem step by step: {problem}")
        bot.reply_to(message, solution_response.text)
    except IndexError:
        bot.reply_to(message, "Please provide a math problem after /math")
    except Exception as e:
        bot.reply_to(message, f"Math solving error: {str(e)}")

# Translation Handler
@bot.message_handler(commands=['translate'])
def translate_text(message):
    try:
        parts = message.text.split(' ', 2)
        target_lang = parts[1]
        text = parts[2]
        
        translation_prompt = f"Translate the following text to {target_lang}: {text}"
        translation_response = model.generate_content(translation_prompt)
        
        bot.reply_to(message, translation_response.text)
    except IndexError:
        bot.reply_to(message, "Usage: /translate [language] [text]")
    except Exception as e:
        bot.reply_to(message, f"Translation error: {str(e)}")

# General message handler for direct chat
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "I'm having trouble processing your message.")

# Webhook setup function
def set_webhook():
    webhook_url = 'https://your-vercel-domain.vercel.app/api/webhook'
    bot.set_webhook(url=webhook_url)

# For local testing and Vercel compatibility
def handler(event, context):
    return app(event, context)

if __name__ == '__main__':
    app.run(debug=True)
