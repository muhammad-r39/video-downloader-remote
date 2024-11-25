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

        # Serve the file to the user for download
        return send_file(file_path, as_attachment=True)

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
        formats = []

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for fmt in info.get('formats', []):
                formats.append({
                    'format_id': fmt['format_id'],
                    'resolution': fmt.get('resolution', 'audio only'),
                    'ext': fmt['ext']
                })

        return jsonify({"formats": formats}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
