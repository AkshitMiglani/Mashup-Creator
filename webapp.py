import sys
from youtube_channel_videos_scraper_bot import *
from pytube import YouTube
import os
from pydub import AudioSegment
import glob
import zipfile
import youtube_dl
from youtubesearchpython import VideosSearch
from flask import Flask, render_template,request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


app=Flask(__name__)
def main(formData):
    name=formData[0]
    num=int(formData[1])
    time=int(formData[2])
    email=formData[3]
    out="102003701"

    videosSearch = VideosSearch(name, limit = num)

    urls=[]
    for i in range(0,num):
        urls.append(videosSearch.result()["result"][i]["link"])
        download_audio(urls[i])

    list_files=glob.glob('./*.mp3')
    for i in range(num):
        audio_file = list_files[i]
        cut_audios(audio_file, num, time)

    s1=AudioSegment.from_mp3("./audio0trimmed.mp3")
    for i in range(1,num):
        audio_file="./audio"+ str(i)+"trimmed.mp3"
        s2=AudioSegment.from_mp3(audio_file)
        s1=s1.append(s2,crossfade=1500)
    s1.export("./mashup.mp3",format="mp3")
    zip = zipfile.ZipFile(out+".zip", "w", zipfile.ZIP_DEFLATED)
    zip.write("./mashup.mp3")
    zip.close()

    files=glob.glob('./*.mp3')
    for file in files:
        os.remove(file)


    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email import encoders

    fromaddr = "Enter E-Mail ID"
    toaddr = email

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Your Mashup is ready"

    # open the file to be sent
    filename = "mashup.zip"
    attachment = open("102003701.zip", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "Enter Password")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/",methods=['POST'])
def home():
    formData=[]
    formData.append(request.form['singername'])
    formData.append(request.form['no_of_videos'])
    formData.append(request.form['timestamp'])
    formData.append(request.form['email'])
    main(formData)
    return "<h1><center>Thanking You</center></h1>"
def get_video_time_in_ms(video_timestamp):
    vt_split = video_timestamp.split(":")
    if (len(vt_split) == 3):
        hours = int(vt_split[0]) * 60 * 60 * 1000
        minutes = int(vt_split[1]) * 60 * 1000
        seconds = int(vt_split[2]) * 1000
    else:
        hours = 0
        minutes = int(vt_split[0]) * 60 * 1000
        seconds = int(vt_split[1]) * 1000
    
    return hours + minutes + seconds

def cut_audios(singer_name, num, time):
    for i in range(num):
        audio = AudioSegment.from_file(singer_name)
        audio = audio[:time * 1000]
        audio.export('audio'+str(i)+'trimmed.mp3', format='mp3')

def download_audio(yt_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yt_url])

if __name__=="__main__":
    app.run(debug=True)
