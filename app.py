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
            # ===========================
            # ✅ AMBIL INFO TANPA DOWNLOAD
            # ===========================
            ydl_info_opts = {
                "quiet": True,
                "nocheckcertificate": True,
                "cookiefile": None,
                "force_ipv4": True,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0"
                }
            }

            with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "Downloader")

            # ===========================
            # ✅ FIX THUMBNAIL INSTAGRAM / TIKTOK / FB
            # ===========================
            if info.get("thumbnail"):
                thumbnail = info["thumbnail"]
            elif info.get("thumbnails"):
                thumbnail = info["thumbnails"][-1]["url"]
            else:
                thumbnail = None

            # ===========================
            # ✅ FORMAT NAMA FILE TANGGAL
            # ===========================
            today = datetime.now().strftime("%Y%m%d")

            existing_files = os.listdir(DOWNLOAD_FOLDER)
            today_files = [f for f in existing_files if f.startswith(f"download-{today}")]
            video_number = len(today_files) + 1

            final_name = f"download-{today}-{video_number}.{info['ext']}"

            # ===========================
            # ✅ SETTING DOWNLOAD
            # ===========================
            ydl_opts = {
                "format": quality,
                "outtmpl": os.path.join(
                    DOWNLOAD_FOLDER,
                    f"download-{today}-{video_number}.%(ext)s"
                ),
                "noplaylist": True,
                "quiet": True,
                "nocheckcertificate": True,
                "merge_output_format": "mp4",

                "http_headers": {
                    "User-Agent": "Mozilla/5.0"
                },

                # ✅ FIX TIKTOK & IG WATERMARK
                "extractor_args": {
                    "tiktok": {
                        "impersonation": ["web"]
                    }
                }
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

if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    app.run(host="0.0.0.0", port=8080)
