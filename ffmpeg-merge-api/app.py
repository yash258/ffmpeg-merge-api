from flask import Flask, request, jsonify
import subprocess
import os
import requests
import uuid

app = Flask(__name__)
STATIC_FOLDER = 'static'
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "FFmpeg Merge API is running!"

@app.route("/merge", methods=["POST"])
def merge():
    data = request.get_json()
    audio_url = data.get("audio_url")
    video_url = data.get("video_url")
    if not audio_url or not video_url:
        return jsonify({"error": "Missing audio_url or video_url"}), 400

    try:
        # Generate unique filenames
        audio_file = f"{uuid.uuid4()}.mp3"
        video_file = f"{uuid.uuid4()}.mp4"
        output_file = f"{uuid.uuid4()}.mp4"

        audio_path = os.path.join(STATIC_FOLDER, audio_file)
        video_path = os.path.join(STATIC_FOLDER, video_file)
        output_path = os.path.join(STATIC_FOLDER, output_file)

        # Download audio
        with open(audio_path, "wb") as f:
            f.write(requests.get(audio_url).content)

        # Download video
        with open(video_path, "wb") as f:
            f.write(requests.get(video_url).content)

        # Merge with FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd, check=True)

        # Return URL
        merged_url = request.host_url + f"static/{output_file}"
        return jsonify({"merged_url": merged_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
