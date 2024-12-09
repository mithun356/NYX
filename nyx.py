import streamlit as st
import openai
from gtts import gTTS
import os
import speech_recognition as sr
from io import BytesIO
from PIL import Image
import requests
from datetime import datetime

st.set_page_config(page_title="NYX", layout="wide")

openai.api_key = st.secrets["openai"]["api_key"]

def play_audio(text):
    try:
        tts = gTTS(text, lang="en")
        temp_audio_path = os.path.join("temp_audio.mp3")
        tts.save(temp_audio_path)
        st.audio(temp_audio_path, format="audio/mp3")
        os.remove(temp_audio_path)
    except Exception as e:
        st.error(f"Error generating audio: {e}")

def real_time_prediction(command):
    if "weather" in command.lower():
        return "The weather is sunny with a temperature of 25°C."
    elif "time" in command.lower():
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
    else:
        return "I am unable to perform that task currently. Let me help you with something else."

st.markdown(
    """
    <h1 style="text-align: center;">
        <span style="color:red;">N</span><span style="color:black;">YX</span>
    </h1>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <p style="text-align: center; font-size: 18px;">
    NYX is an AI-powered assistant that helps you with tasks like chatting, generating images from descriptions, and providing real-time information. You can interact with NYX via text or voice commands for a seamless experience.
    </p>
    """, 
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["Chat", "Image Generation", "Settings"])

if "conversation" not in st.session_state:
    st.session_state["conversation"] = []

with tab1:
    st.header("Ask Nyx!")
    
    st.write("### Chat History")
    for entry in st.session_state["conversation"]:
        if entry["role"] == "user":
            st.markdown(f"**You**: {entry['content']}")
        else:
            st.markdown(f"**Assistant**: {entry['content']}")

    user_input = st.text_input("Type your message:")

    if st.button("Click to Speak"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now!")
            try:
                audio = recognizer.listen(source, timeout=5)
                user_input = recognizer.recognize_google(audio)
                st.write(f"**Transcribed Input**: {user_input}")

                prediction_response = real_time_prediction(user_input)
                if prediction_response != "I am unable to perform that task currently. Let me help you with something else.":
                    st.session_state["conversation"].append({"role": "assistant", "content": prediction_response})
                    st.write(f"**Assistant**: {prediction_response}")
                    play_audio(prediction_response)
                else:
                    if len(st.session_state["conversation"]) == 0:
                        st.session_state["conversation"].append({"role": "user", "content": user_input})

                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=st.session_state["conversation"]
                    )
                    bot_response = response.choices[0].message['content']
                    st.session_state["conversation"].append({"role": "assistant", "content": bot_response})
                    st.write(f"**Assistant**: {bot_response}")
                    play_audio(bot_response)

            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your voice input.")
            except sr.WaitTimeoutError:
                st.error("Timeout: No speech detected.")

    if st.button("Send"):
        if user_input:
            st.session_state["conversation"].append({"role": "user", "content": user_input})

            prediction_response = real_time_prediction(user_input)
            if prediction_response != "I am unable to perform that task currently. Let me help you with something else.":
                st.session_state["conversation"].append({"role": "assistant", "content": prediction_response})
                st.write(f"**Assistant**: {prediction_response}")
                play_audio(prediction_response)
            else:
                if len(st.session_state["conversation"]) == 1:
                    st.session_state["conversation"].insert(0, {"role": "user", "content": user_input})

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state["conversation"]
                )
                bot_response = response.choices[0].message['content']
                st.session_state["conversation"].append({"role": "assistant", "content": bot_response})
                st.write(f"**Assistant**: {bot_response}")
                play_audio(bot_response)

    if st.button("Clear Chat History"):
        st.session_state["conversation"] = []
        st.success("Chat history cleared!")

with tab2:
    st.header("Generate Images")
    
    image_prompt = st.text_input("Describe the image you want:")

    if st.button("Click to Speak for Image"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now for image description!")
            try:
                audio = recognizer.listen(source, timeout=5)
                image_prompt = recognizer.recognize_google(audio)
                st.write(f"**Transcribed Input**: {image_prompt}")
                
                if image_prompt:
                    image_response = openai.Image.create(
                        prompt=image_prompt,
                        n=1,
                        size="512x512"
                    )
                    image_url = image_response['data'][0]['url']
                    image = Image.open(requests.get(image_url, stream=True).raw)
                    st.image(image, caption="Generated Image")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand your voice input.")
            except sr.WaitTimeoutError:
                st.error("Timeout: No speech detected.")

    if st.button("Generate Image"):
        if image_prompt:
            image_response = openai.Image.create(
                prompt=image_prompt,
                n=1,
                size="512x512"
            )
            image_url = image_response['data'][0]['url']
            image = Image.open(requests.get(image_url, stream=True).raw)
            st.image(image, caption="Generated Image")

with tab3:
    st.header("Settings & Privacy")
    st.write("This application ensures the privacy of your interactions:")
    st.markdown("""
    - **No data storage:** All inputs and outputs are transient and not stored permanently.
    - **Encrypted communication:** Your queries are sent securely to OpenAI's API.
    """)
    if st.button("Clear All Data"):
        st.session_state["conversation"] = []
        st.success("All data cleared!")

st.markdown("---")
st.write("Developed with ❤️ using Streamlit and OpenAI.")
