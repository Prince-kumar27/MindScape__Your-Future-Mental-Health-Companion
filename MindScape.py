import streamlit as st
import tweepy
import pickle
import re
import requests
import datetime
import google.generativeai as genai
from PIL import Image

# Twitter API Credentials (Replace with your own)
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAH44ywEAAAAA%2Ba0vH8E52pO53wNPET%2FUBmyaPiM%3DpdyxOMOTkLnn5dD2SElqGr5uSBCMngfWtIW2Wvk2bX9XutHCgp"

# Gemini API Key (Replace with your actual key)
GEMINI_API_KEY = "AIzaSyDZO45HN9j0YVBDxbxevEFfsYHXE5eV0fI"

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)


menu_icon = Image.open("img.webp")
menu_icon = menu_icon.resize((1024, 1004))  

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# # Load the trained model
# with open(r"C:\Users\DELL\OneDrive\Desktop\XIX\Final year Project\sentiment_model.pkl", "rb") as file:
#     model = pickle.load(file)

# # Load the fitted vectorizer
# with open(r"C:\Users\DELL\OneDrive\Desktop\XIX\Final year Project\tfidf_vectorizer.pkl", "rb") as file:
#     vectorizer = pickle.load(file)
import os
import pickle

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the trained model
model_path = os.path.join(current_dir, "sentiment_model.pkl")
with open(model_path, "rb") as file:
    model = pickle.load(file)

# Load the fitted vectorizer
vectorizer_path = os.path.join(current_dir, "tfidf_vectorizer.pkl")
with open(vectorizer_path, "rb") as file:
    vectorizer = pickle.load(file)


# Function to clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)  
    text = re.sub(r'[^a-zA-Z ]', '', text) 
    return text

# Function to fetch tweets
def fetch_tweets(username, max_tweets=5):
    try:
        user = client.get_user(username=username, user_auth=False)
        tweets = client.get_users_tweets(user.data.id, max_results=max_tweets)
        return [tweet.text for tweet in tweets.data]
    except Exception as e:
        return [f"Error fetching tweets: {e}"]



def generate_suggestions(tweet, sentiment):
    try:
        with st.spinner("Generating mental health suggestions..."):
            prompt = (f"Analyze the following tweet: '{tweet}'. "
                      f"The sentiment is '{sentiment}'. Provide 5-6 practical mental health tips, "
                      f"sorted and concise, to help based on this sentiment.")
            response = genai.GenerativeModel("gemini-1.5-pro-latest").generate_content(prompt)
            return "\n".join(sorted(response.text.strip().split("\n")))
    except Exception as e:
        return f"Error: {e}"



# Function to fetch daily affirmation
def get_daily_affirmation():
    try:
        response = requests.get("https://zenquotes.io/api/today")
        if response.status_code == 200:
            return response.json()[0]['q'] 
        else:
            return "You are strong, capable, and enough. 💙"
    except Exception:
        return "You are doing your best, and that is enough. 😊"

# Ensure daily refresh of affirmation
if "last_updated" not in st.session_state or st.session_state["last_updated"] != datetime.date.today():
    st.session_state["affirmation"] = get_daily_affirmation()
    st.session_state["last_updated"] = datetime.date.today()

# Function for AI Chatbot responses
def chat_with_ai(user_message):
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(f"Provide helpful responses as a mental health chatbot: {user_message}")
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"


st.sidebar.image(menu_icon)  
st.sidebar.title("Navigation")
option = st.sidebar.radio("Choose an option:", ["Analyze a Custom Tweet", "Fetch & Analyze Live Tweets","Daily Affirmations 🌟","AI Chatbot"])


st.markdown(
    """
    <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(-10px); }
            100% { opacity: 1; transform: translateY(0px); }
        }
        .title {
            text-align: Left;
            font-size: 40px;
            color: #ff4081;
            text-shadow: 2px 2px 8px #ff80ab;
            animation: fadeIn 2.5s ease-in-out;
        }
    </style>
    <h1 class='title'>MindScape: Your Future Mental Health Companion</h1>
    """, 
    unsafe_allow_html=True
)



if option == "Analyze a Custom Tweet":
    st.subheader("📢 Tweet Sentiment Analyzer")
    
    st.markdown(
        """
        <style>
            .tweet-box {
                font-size: 18px;
                padding: 12px;
                border-radius: 10px;
                border: 2px solid #4CAF50;
                background-color: #f9f9f9;
            }
            .analyze-btn {
                background-color: #ff4081;
                color: white;
                font-size: 18px;
                padding: 10px 20px;
                border-radius: 8px;
                cursor: pointer;
            }
            .analyze-btn:hover {
                background-color: #e6006b;
            }
        </style>
        """, 
        unsafe_allow_html=True
    )

    user_input = st.text_area(
        "💬 Enter a tweet to analyze:",
        placeholder="Type or paste a tweet here...",
        height=70
    )

    if st.button("🔍 Analyze Sentiment", key="analyze", help="Click to analyze the sentiment of the tweet!"):
        if user_input:
            cleaned_text = clean_text(user_input)
            sentiment = "Positive" if model.predict(vectorizer.transform([cleaned_text]))[0] == 1 else "Negative"
            
            st.success(f"**Sentiment:** {sentiment}")
            st.subheader("✨ MindScape AI Mental Health Suggestions:")
            st.write("\n".join(sorted(generate_suggestions(user_input, sentiment).split("\n"))))
        else:
            st.warning("⚠️ Please enter a tweet to analyze.")



elif option == "Fetch & Analyze Live Tweets":
    st.subheader("Live Twitter Sentiment Analysis")
    username = st.text_input("Enter Twitter Handle (without @):")
    max_tweets = st.slider("Number of tweets to fetch:", 1, 10, 5)

    if st.button("Fetch & Analyze Tweets"):
        if username:
            tweets = fetch_tweets(username, max_tweets)
            for i, tweet in enumerate(tweets):
                cleaned_tweet = clean_text(tweet)
                vectorized_tweet = vectorizer.transform([cleaned_tweet])
                prediction = model.predict(vectorized_tweet)
                sentiment = "Positive" if prediction[0] == 1 else "Negative"
                st.write(f"**Tweet {i+1}:** {tweet}")
                st.write(f"**Sentiment:** {sentiment}")
                
                
                suggestion = generate_suggestions(sentiment)
                st.write("### MindScape AI Suggestions:")
                st.write(suggestion)
                st.write("---")
elif option == "Daily Affirmations 🌟":
    st.subheader("🌟 Your Daily Affirmation 🌟")

    
    st.markdown(
        f"""
        <style>
            
            .affirmation {{
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px;
                background: #f0fff0;
                border-radius: 10px;
                animation: fadeIn 2s ease-in-out;
            }}
        </style>
        <div class='affirmation'>{st.session_state["affirmation"]}</div>
        """,
        unsafe_allow_html=True)
    

elif option == "AI Chatbot":
    st.subheader("🤖 AI Mental Health Chatbot")
    st.write("Talk to our AI-powered chatbot for mental health support and guidance.")

    # Clear chat history when switching to AI Chatbot
    if "last_option" not in st.session_state or st.session_state.last_option != "AI Chatbot":
        st.session_state.chat_history = []  # Reset chat history
        st.session_state.last_option = "AI Chatbot"  # Store the current option

    # Initialize chat history if not already present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        st.markdown(message)

    # Input field for continuous conversation
    user_input = st.chat_input("Type your message here...")

    if user_input:
        response = chat_with_ai(user_input)[:200]  # Limit response length
        st.session_state.chat_history.append(f"**You:** {user_input}")  # Store user message
        st.session_state.chat_history.append(f"**AI:** {response}")  # Store AI response
        st.rerun()  # Refresh chat dynamically
else:
 st.warning("Please enter a Twitter handle.")


