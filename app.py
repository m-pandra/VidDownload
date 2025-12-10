from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import yt_dlp
import os
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
COOKIE_FILE = os.path.join(BASE_DIR, "cookies.txt")

# ✅ CACHE PREVIEW (SUPAYA INDEX SINKRON)
PREVIEW_CACHE = {}

# =========================
# ✅ HOME VIDEO DOWNLOADER
# =========================
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
            ydl_info_opts = {
                "quiet": True,
                "cookiefile": COOKIE_FILE,
                "force_ipv4": True,
                "http_headers": {"User-Agent": "Mozilla/5.0"}
            }

            with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "Downloader")

            if info.get("thumbnail"):
                thumbnail = info["thumbnail"]
            elif info.get("thumbnails"):
                thumbnail = info["thumbnails"][-1]["url"]

            today = datetime.now().strftime("%Y%m%d")
            existing_files = os.listdir(DOWNLOAD_FOLDER)
            today_files = [f for f in existing_files if f.startswith(f"download-{today}")]
            video_number = len(today_files) + 1

            final_name = f"download-{today}-{video_number}.{info['ext']}"

            ydl_opts = {
                "format": quality,
                "outtmpl": os.path.join(DOWNLOAD_FOLDER, f"download-{today}-{video_number}.%(ext)s"),
                "noplaylist": True,
                "quiet": True,
                "cookiefile": COOKIE_FILE,
                "merge_output_format": "mp4",
                "http_headers": {"User-Agent": "Mozilla/5.0"}
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


# =========================
# ✅ IG STORY PREVIEW (FIX FULL)
# =========================
@app.route("/ig-story", methods=["GET", "POST"])
def ig_story():
    message = ""
    previews = []
    username = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            message = "❌ Username tidak boleh kosong!"
        else:
            try:
                story_url = f"https://www.instagram.com/stories/{username}/"

                ydl_opts_info = {
                    "quiet": True,
                    "skip_download": True,
                    "cookiefile": COOKIE_FILE,
                    "extract_flat": False,
                    "noplaylist": False,
                    "playlist_items": "1-100",
                    "force_ipv4": True,
                    "http_headers": {"User-Agent": "Mozilla/5.0"}
                }

                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(story_url, download=False)

                # ✅ FIX: PAKSA JIKA ENTRIES KOSONG
                entries = info.get("entries", [])
                if not entries:
                    entries = [info]

                PREVIEW_CACHE[username] = entries

                for index, item in enumerate(entries, start=1):
                    thumb = item.get("thumbnail")
                    if not thumb and item.get("thumbnails"):
                        thumb = item["thumbnails"][-1]["url"]

                    previews.append({
                        "index": index,
                        "title": item.get("title", f"Story {index}"),
                        "thumbnail": thumb
                    })

                message = f"✅ {len(previews)} story berhasil dimuat!"

            except Exception as e:
                message = f"❌ Gagal: {str(e)}"

    return render_template(
        "ig_story.html",
        message=message,
        previews=previews,
        username=username
    )


# =========================
# ✅ DOWNLOAD 1 STORY SESUAI PREVIEW (ANTI SALAH)
# =========================
@app.route("/download-story", methods=["POST"])
def download_story():
    username = request.form.get("username")
    index = request.form.get("index")

    if not username or not index:
        return "Data tidak valid!"

    index = int(index)

    story_url = f"https://www.instagram.com/stories/{username}/"

    today = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"igstory-{username}-{index}-{today}.mp4"

    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, filename),
        "cookiefile": COOKIE_FILE,

        # ✅ INI KUNCI UTAMA BIAR GA SALAH DOWNLOAD
        "playlist_items": str(index),

        "merge_output_format": "mp4",
        "quiet": True,
        "http_headers": {"User-Agent": "Mozilla/5.0"}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([story_url])

        return redirect(url_for("download_file", filename=filename))

    except Exception as e:
        return f"❌ Gagal download: {str(e)}"


# =========================
# ✅ DOWNLOAD FILE
# =========================
@app.route("/downloads/<path:filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


# =========================
# ✅ RUN SERVER
# =========================
if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    app.run(host="0.0.0.0", port=8080, debug=True)
