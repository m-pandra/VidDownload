from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    filename = None
    thumbnail = None
    title = None

    if request.method == "POST":
        url = request.form["url"]
        quality = request.form["quality"]

        try:
            # ✅ AMBIL INFO VIDEO TANPA DOWNLOAD
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title")
            thumbnail = info.get("thumbnail")

            # ✅ FORMAT TANGGAL HARI INI
            today = datetime.now().strftime("%Y%m%d")

            # ✅ HITUNG FILE YANG SUDAH ADA DI TANGGAL INI
            existing_files = os.listdir(DOWNLOAD_FOLDER)
            today_files = [f for f in existing_files if f.startswith(f"download-{today}")]
            video_number = len(today_files) + 1

            # ✅ NAMA FILE FINAL
            final_name = f"download-{today}-{video_number}.{info['ext']}"

            # ✅ SETTING DOWNLOAD
            ydl_opts = {
                'format': quality,
                'outtmpl': os.path.join(
                    DOWNLOAD_FOLDER,
                    f"download-{today}-{video_number}.%(ext)s"
                ),
                'noplaylist': True,
                'quiet': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            filename = final_name
            message = "✅ Video siap untuk didownload!"

        except Exception as e:
            message = f"❌ Gagal: {str(e)}"

    return render_template(
        "index.html",
        message=message,
        filename=filename,
        thumbnail=thumbnail,
        title=title
    )

@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# if __name__ == "__main__":
#     if not os.path.exists(DOWNLOAD_FOLDER):
#         os.makedirs(DOWNLOAD_FOLDER)

#     app.run(debug=True)

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    app.run(host="0.0.0.0", port=8080)
