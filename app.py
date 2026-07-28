import os
import threading
import uuid

from flask import Flask, render_template, request, jsonify

from vinted_client import search_and_filter, VintedError

app = Flask(__name__)

# Simpel in-memory jobliste - fint til lokal, enkeltbruger-brug.
JOBS = {}


def run_job(job_id, search_url, country_code, max_pages, order):
    def progress_cb(msg):
        JOBS[job_id]["progress"] = msg

    try:
        results = search_and_filter(
            search_url,
            country_code=country_code,
            max_pages=max_pages,
            order=order,
            progress_cb=progress_cb,
        )
        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["results"] = results
    except VintedError as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
    except Exception as e:  # uventede fejl skal stadig vises pænt i UI
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = f"Uventet fejl: {e}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json(force=True) or {}
    search_url = (data.get("url") or "").strip()
    country_code = (data.get("country") or "DK").strip()
    order = (data.get("order") or "relevance").strip()
    try:
        max_pages = max(1, min(10, int(data.get("max_pages") or 10)))
    except (TypeError, ValueError):
        max_pages = 10

    if not search_url:
        return jsonify({"error": "Indsæt en Vinted søge-URL"}), 400

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "running",
        "progress": "Starter...",
        "results": None,
        "error": None,
    }

    thread = threading.Thread(
        target=run_job, args=(job_id, search_url, country_code, max_pages, order), daemon=True
    )
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def api_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Ukendt job"}), 404
    return jsonify(job)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
