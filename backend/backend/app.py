from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
import os
from werkzeug.utils import secure_filename
import uuid 

# Ensure backend path is included
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import story logic
try:
    from story_trip import StoryTrip
    print("story_trip.py loaded successfully")
except Exception as e:
    print("CRITICAL ERROR: Could not load story_trip.py")
    print(f"Details: {e}")
    sys.exit(1)

template_dir = os.path.join(current_dir, 'template')
static_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'frontend', 'static'))
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
CORS(app)

print(f"Using template folder: {template_dir}")
print(f"Using static folder: {static_dir}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_story', methods=['GET'])
def get_story():

    # ✅ FIX: request is now imported properly
    personality = int(request.args.get('personality', 1))
    mood = int(request.args.get('mood', 1))
    budget = int(request.args.get('budget', 1))
    preference = int(request.args.get('preference', 1))

    trip = StoryTrip(personality, mood, budget, preference)

    trip.generate_world()
    trip.generate_companion()
    trip.generate_environment()
    trip.generate_mission()
    trip.generate_danger()
    trip.generate_reward()
    trip.generate_ending()

    return jsonify({
        "status": "success",
        "story": trip.show_experience(),
        "image": trip.image_file
    })


@app.route('/save_story', methods=['POST'])
def save_story():
    data = request.get_json() or {}
    story_text = data.get('story', '')
    image = data.get('image', '')

    if not story_text:
        return jsonify({"status": "error", "message": "No story provided"}), 400

    # Ensure directory for saved stories exists inside static folder so files are served
    saved_dir = os.path.join(static_dir, 'saved_stories')
    os.makedirs(saved_dir, exist_ok=True)

    # Create a safe unique filename
    file_id = str(uuid.uuid4())
    text_filename = secure_filename(f"story_{file_id}.txt")
    json_filename = secure_filename(f"story_{file_id}.json")

    # Write text file
    text_path = os.path.join(saved_dir, text_filename)
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(story_text)

    # Write metadata JSON
    meta = {
        "story": story_text,
        "image": image
    }
    json_path = os.path.join(saved_dir, json_filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        import json as _json
        _json.dump(meta, f, ensure_ascii=False, indent=2)

    file_url = f"{request.url_root.rstrip('/')}{app.static_url_path}/saved_stories/{text_filename}"

    return jsonify({"status": "success", "url": file_url})


@app.route('/download_story/<filename>', methods=['GET'])
def download_story(filename):
    # Serve from the saved_stories directory under static
    saved_dir = os.path.join(static_dir, 'saved_stories')
    return app.send_static_file(f"saved_stories/{filename}")


@app.route('/list_stories', methods=['GET'])
def list_stories():
    saved_dir = os.path.join(static_dir, 'saved_stories')
    os.makedirs(saved_dir, exist_ok=True)

    files = []
    for name in sorted(os.listdir(saved_dir), reverse=True):
        # only show downloadable story text files (.txt)
        if name.lower().endswith('.txt'):
            url = f"{request.url_root.rstrip('/')}{app.static_url_path}/saved_stories/{name}"
            files.append({"name": name, "url": url})

    return jsonify({"status": "success", "files": files})


@app.route('/delete_story', methods=['POST'])
def delete_story():
    data = request.get_json() or {}
    filename = data.get('filename')
    if not filename:
        return jsonify({"status": "error", "message": "filename required"}), 400

    safe_name = secure_filename(filename)
    saved_dir = os.path.join(static_dir, 'saved_stories')
    target_path = os.path.join(saved_dir, safe_name)

    # Prevent path traversal
    try:
        if os.path.commonpath([os.path.abspath(saved_dir)]) != os.path.commonpath([os.path.abspath(saved_dir), os.path.abspath(target_path)]):
            return jsonify({"status": "error", "message": "Invalid filename"}), 400
    except Exception:
        return jsonify({"status": "error", "message": "Invalid filename"}), 400

    if not os.path.exists(target_path):
        return jsonify({"status": "error", "message": "File not found"}), 404

    try:
        os.remove(target_path)
        # also try removing companion file (.txt <-> .json)
        base, ext = os.path.splitext(safe_name)
        for alt_ext in ('.txt', '.json'):
            alt = os.path.join(saved_dir, base + alt_ext)
            if os.path.exists(alt):
                try:
                    os.remove(alt)
                except Exception:
                    pass
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not delete: {e}"}), 500

    return jsonify({"status": "success"})


if __name__ == '__main__':
    print("Server starting on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)