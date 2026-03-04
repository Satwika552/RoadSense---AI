# app.py
# Main Flask application — connects all components together

from flask import Flask, render_template, request, jsonify, send_file
import os
from utils.detect import detect_damage
from utils.severity import summarize_detections
from utils.report import generate_report

app = Flask(__name__)

# Config
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "mp4", "avi", "mov"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Save uploaded file
    upload_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(upload_path)

    # Run detection
    result_filename, detections = detect_damage(upload_path)

    if result_filename is None:
        return jsonify({"error": "Could not process image"}), 500

    # Summarize results
    summary = summarize_detections(detections)

    # Generate PDF report
    report_filename = generate_report(detections, summary, result_filename)

    return jsonify({
        "result_image": f"/static/uploads/{result_filename}",
        "report_url": f"/static/uploads/{report_filename}",
        "detections": detections,
        "summary": summary
    })

@app.route("/download/<filename>")
def download(filename):
    path = os.path.join("static", "uploads", filename)
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    print("Starting RoadSense AI...")
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)