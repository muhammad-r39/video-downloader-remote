from flask import Flask, request, jsonify
import yt_dlp
import os
import threading

app = Flask(__name__)

@app.route('/get-formats', methods=['POST'])
def get_formats():
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            return jsonify({"error": "URL is required"}), 400

        ydl_opts = {}

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for fmt in info.get('formats', []):
                formats.append({
                    'format_id': fmt['format_id'],
                    'resolution': fmt.get('resolution', 'audio only'),
                    'ext': fmt['ext'],
                    'url': fmt.get('url', '')
                })

        # Extract additional metadata
        video_title = info.get('title', 'Unknown Title')
        platform = info.get('extractor', 'Unknown Platform')
        thumbnail = info.get('thumbnail', '')

        return jsonify({
            "formats": formats,
            "title": video_title,
            "platform": platform.capitalize(),
            "thumbnail": thumbnail
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
