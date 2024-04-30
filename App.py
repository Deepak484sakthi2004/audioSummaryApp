from flask import Flask, render_template, request, url_for
import whisper
import os
from pytube import YouTube
from pathlib import Path
import shutil
import pandas as pd
import google.generativeai as genai
from pydub import AudioSegment
from io import BytesIO

app = Flask(__name__)

GOOGLE_API_KEY = 'AIzaSyDYcywS_Pex1M1fe6VYkO2TXtH_7GA7iJ8'
genai.configure(api_key=GOOGLE_API_KEY)

def load_model():
    model = whisper.load_model("base")
    return model

def save_video(url, video_filename):
    youtubeObject = YouTube(url)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")
    
    return video_filename

def save_audio(url):
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download()
    base, ext = os.path.splitext(out_file)
    file_name = base + '.mp3'
    try:
        os.rename(out_file, file_name)
    except OSError:
        os.remove(file_name)
        os.rename(out_file, file_name)
    # Remove special characters from the file name
    audio_filename = Path(file_name).stem.replace('?', '').replace('=', '') + '.mp3'
    video_filename = save_video(url, Path(file_name).stem + '.mp4')
    print(yt.title + " Has been successfully downloaded")
    return yt.title, audio_filename, video_filename

def process_uploaded_audio(file_name):
     audio_filename = Path(file_name).stem+'.mp3'
     return audio_filename

def audio_to_transcript(audio_file):
    model = load_model()
    result = model.transcribe(audio_file)
    transcript = result["text"]
    return transcript

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/video_summary', methods=['GET', 'POST'])
def video_summary():
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        # Assuming process_uploaded_audio() returns the audio filename
        title, audio_filename, video_filename = save_audio(youtube_url)
        print("Audio filename:", audio_filename)  # Add this line for debugging
        transcript_result = audio_to_transcript(audio_filename)
        model = genai.GenerativeModel('gemini-pro')
        prompt = transcript_result + " provide me the summary of the text with suitable topic, and a report of it highlighting the key points. Also provide the some other suitable related important informatio regrading it"
        response = model.generate_content(prompt)
        
        return render_template('video_summary.html', transcript_results=transcript_result, response=response.text, video_filename=video_filename)
    else:
        return render_template('video_summary.html')


if __name__ == '__main__':
    app.run(debug=True)
