from flask import Flask, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# Directory to temporarily store downloaded videos
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/download', methods=['POST'])
def download_video():
    try:
        data = request.get_json()
        url = data.get('url')
        format_id = data.get('format_id')  # Get the selected format from the user

        if not url or not format_id:
            return jsonify({"error": "URL and format_id are required"}), 400

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': format_id,  # Use the selected format
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        # Create a public-facing URL for the file (assuming static hosting)
        file_name = os.path.basename(file_path)
        public_url = f"https://video-downloader-9ilz.onrender.com/{DOWNLOAD_DIR}/{file_name}"

        return jsonify({"download_url": public_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-formats', methods=['POST'])
def get_formats():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400

        ydl_opts = {'listformats': True}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for fmt in info.get('formats', []):
                formats.append({
                    'format_id': fmt['format_id'],
                    'resolution': fmt.get('resolution', 'audio only'),
                    'ext': fmt['ext']
                })

        # Extract additional metadata
        video_title = info.get('title', 'Unknown Title')
        platform = info.get('extractor', 'Unknown Platform')
        thumbnail = info.get('thumbnail', '')

        return jsonify({
            "formats": formats,
            "title": video_title,
            "platform": platform,
            "thumbnail": thumbnail
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
