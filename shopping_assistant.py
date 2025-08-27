import speech_recognition as sr
import pyttsx3
import spacy
import json
import re
import streamlit as st
from datetime import datetime

# -------------------------
# INITIAL SETUP
# -------------------------
recognizer = sr.Recognizer()
speaker = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")   # NLP model

# Shopping list & categories
shopping_list = []
categories = {
    "milk": "dairy", "cheese": "dairy", "yogurt": "dairy",
    "apple": "fruits", "banana": "fruits", "orange": "fruits",
    "bread": "bakery", "rice": "grains", "water": "beverages"
}

# Load history for smart suggestions
try:
    with open("history.json", "r") as f:
        history = json.load(f)
except:
    history = {"purchases": []}

# -------------------------
# SPEECH & FEEDBACK
# -------------------------
def speak(text):
    speaker.say(text)
    speaker.runAndWait()

def listen_command(language="en-US"):
    """Listen to user voice and return text"""
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now!")
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language=language)
        st.success(f"👉 You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        st.error("❌ Could not understand")
        return ""
    except sr.RequestError:
        st.error("⚠️ Could not connect to speech service")
        return ""

# -------------------------
# NLP HELPERS
# -------------------------
def extract_item_and_qty(command):
    """Extract item and quantity from a voice command"""
    doc = nlp(command)
    qty = 1
    item = None

    # Quantity via regex
    match = re.search(r'\d+', command)
    if match:
        qty = int(match.group())

    # Find noun in sentence
    for token in doc:
        if token.pos_ == "NOUN":
            item = token.text.lower()
            break

    return item, qty

# -------------------------
# SHOPPING LIST COMMANDS
# -------------------------
def process_command(command):
    global shopping_list

    if "add" in command or "buy" in command or "need" in command:
        item, qty = extract_item_and_qty(command)
        if item:
            shopping_list.append({"item": item, "qty": qty, "category": categories.get(item, "others")})
            history["purchases"].append({"item": item, "date": str(datetime.now().date())})
            save_history()
            speak(f"Added {qty} {item} to your list.")
        else:
            speak("I could not detect the item.")

    elif "remove" in command or "delete" in command:
        item, _ = extract_item_and_qty(command)
        for i in shopping_list:
            if i["item"] == item:
                shopping_list.remove(i)
                speak(f"Removed {item} from your list.")
                return
        speak(f"{item} is not in your list.")

    elif "show" in command or "list" in command:
        if shopping_list:
            speak("Here is your shopping list.")
        else:
            speak("Your shopping list is empty.")

    elif "find" in command or "search" in command:
        # Mock product DB
        if "apple" in command:
            st.info("🍎 Found organic apples, $3.5/kg")
            speak("I found organic apples for three point five dollars per kilo.")
        else:
            speak("I could not find that item right now.")

    elif "suggest" in command:
        suggest_items()

    elif "stop" in command or "exit" in command:
        speak("Goodbye! Happy shopping!")
        return False

    else:
        speak("Sorry, I didn't understand.")
    return True

# -------------------------
# SMART SUGGESTIONS
# -------------------------
def suggest_items():
    if history["purchases"]:
        last_items = [p["item"] for p in history["purchases"][-3:]]
        st.info(f"🛒 Based on your history, you may need: {', '.join(last_items)}")
        speak("I suggest you might need " + ", ".join(last_items))
    else:
        speak("No shopping history available yet.")

def save_history():
    with open("history.json", "w") as f:
        json.dump(history, f)

# -------------------------
# STREAMLIT UI
# -------------------------
def main():
    st.title("🛍 Voice Command Shopping Assistant")
    st.write("Speak commands like: 'Add milk', 'Remove apples', 'Show my list', 'Suggest items', 'Find apples under $5'")

    if st.button("🎤 Start Voice Command"):
        cmd = listen_command(language="en-US")  # you can change to 'hi-IN' for Hindi
        if cmd:
            process_command(cmd)

    if shopping_list:
        st.subheader("🛒 Current Shopping List")
        for item in shopping_list:
            st.write(f"- {item['qty']} × {item['item']} ({item['category']})")
    else:
        st.write("Shopping list is empty.")

if __name__ == "__main__":
    main()
