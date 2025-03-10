from flask import Flask, request, render_template, send_file, after_this_request, send_from_directory
import yt_dlp
from flask_socketio import SocketIO
import os
from pathlib import Path
import eyed3
import tempfile
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, COMM

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')

def sanitize_filename(filename):
    sanitized = filename.translate(str.maketrans('', '', '【】「」\'/')).replace(' ', '_').strip()[:100]
    return sanitized

def download_audio(url, output_file):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': output_file,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def set_metadata(file_path, title, artist_name, comment):
    # eyed3を使ってタグを設定
    audiofile = eyed3.load(file_path)
    if title:
        audiofile.tag.title = title
    if artist_name:
        audiofile.tag.artist = artist_name
    if comment:
        audiofile.tag.comments.set(comment)
    audiofile.tag.save()

    # mutagenを使ってタグを設定
    audio = MP3(file_path, ID3=ID3)
    if title:
        audio.tags.add(TIT2(encoding=3, text=title))
    if artist_name:
        audio.tags.add(TPE1(encoding=3, text=artist_name))
    if comment:
        audio.tags.add(COMM(encoding=3, lang='eng', desc='desc', text=comment))
    audio.save()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/images/<path:filename>')
def send_image(filename):
    return send_from_directory('images', filename)

@app.route('/download', methods=['POST'])
def download():
    youtube_url = request.form.get('youtube_url')
    custom_filename = request.form.get('custom_filename', '')
    title = request.form.get('title', '')
    artist_name = request.form.get('artist_name', '')
    comment = request.form.get('comment', '')

    if not custom_filename:
        return "Custom Filename is required"

    sanitized_filename = sanitize_filename(custom_filename)

    # 一時ディレクトリを作成
    temp_dir = tempfile.gettempdir()
    temp_output = os.path.join(temp_dir, sanitized_filename)

    try:
        download_audio(youtube_url, temp_output)
    except Exception as e:
        return f"Error downloading file: {e}"

    final_output_file = temp_output + '.mp3'

    if not os.path.exists(final_output_file):
        return f"File not found: {final_output_file}"

    # 元のファイル名をMP3タグとして使用
    set_metadata(final_output_file, title or custom_filename, artist_name, comment)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(final_output_file)
        except Exception as e:
            print(f"Error deleting file: {e}")
        return response

    return send_file(final_output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
