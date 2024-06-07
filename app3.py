import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import random
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
with a highlighter with 1000 words with some quiz questions. Please provide the summary of the text given here: """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text
def generate_quiz(summary, num_questions=5):
    sentences = summary.split('. ')
    random.shuffle(sentences)
    questions = sentences[:num_questions]
    return questions

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)

        st.markdown("## Quiz:")
        questions = generate_quiz(summary)
        user_answers = []
        correct_answers = 0

        for i, question in enumerate(questions):
            user_answer = st.text_input(f"Question {i+1}: {question.strip()}")
            user_answers.append(user_answer)

        if st.button("Submit Quiz"):
            feedback = []
            for i, answer in enumerate(user_answers):
                if answer.strip().lower() in questions[i].strip().lower():
                    feedback.append(f"Question {i+1}: Correct")
                    correct_answers += 1
                else:
                    feedback.append(f"Question {i+1}: Incorrect")

            st.markdown("## Quiz Feedback:")
            for comment in feedback:
                st.write(comment)
            st.write(f"Total Correct Answers: {correct_answers} out of {len(questions)}")
