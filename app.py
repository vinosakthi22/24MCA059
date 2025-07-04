from flask import Flask, request, jsonify, redirect, g
from utils import generate_shortcode, calculate_expiry, format_iso
from models import get_connection, create_tables
from logging_middleware import init_logging
from datetime import datetime

app = Flask(__name__)
init_logging(app)
create_tables()

@app.route('/shorturls', methods=['POST'])
def create_shorturl():
    data = request.get_json()
    original_url = data.get('url')
    shortcode = data.get('shortcode') or generate_shortcode()
    validity = data.get('validity', 30)

    if not original_url:
        return jsonify({"error": "Missing URL"}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM urls WHERE shortcode = ?", (shortcode,))
    if cur.fetchone():
        return jsonify({"error": "Shortcode already in use"}), 409

    expiry = calculate_expiry(validity)
    cur.execute("INSERT INTO urls (original_url, shortcode, expires_at) VALUES (?, ?, ?)",
                (original_url, shortcode, expiry))
    conn.commit()
    conn.close()

    return jsonify({
        "shortLink": f"http://localhost:5000/{shortcode}",
        "expiry": format_iso(expiry),
        "logID": g.log_id,
        "message": "log created successfully"
    }), 201

@app.route('/<shortcode>')
def redirect_to_original(shortcode):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, original_url, expires_at FROM urls WHERE shortcode = ?", (shortcode,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Shortcode not found"}), 404

    url_id, original_url, expires_at = result
    if datetime.utcnow() > expires_at:
        return jsonify({"error": "Shortcode expired"}), 410

    referrer = request.referrer or "Direct"
    cur.execute("INSERT INTO click_logs (url_id, timestamp, referrer, location) VALUES (?, ?, ?, ?)",
                (url_id, datetime.utcnow(), referrer, "India"))
    conn.commit()
    conn.close()

    return redirect(original_url)

@app.route('/shorturls/<shortcode>', methods=['GET'])
def get_stats(shortcode):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, original_url, created_at, expires_at FROM urls WHERE shortcode = ?", (shortcode,))
    result = cur.fetchone()
    if not result:
        return jsonify({"error": "Not found"}), 404

    url_id, original_url, created_at, expires_at = result
    cur.execute("SELECT timestamp, referrer, location FROM click_logs WHERE url_id = ?", (url_id,))
    clicks = cur.fetchall()

    return jsonify({
        "original_url": original_url,
        "created_at": format_iso(created_at),
        "expires_at": format_iso(expires_at),
        "click_count": len(clicks),
        "click_logs": [
            {
                "timestamp": format_iso(row[0]),
                "referrer": row[1],
                "location": row[2]
            } for row in clicks
        ],
        "logID": g.get("log_id", "none"),
        "message": "log created successfully"
    })

if __name__ == '__main__':
    app.run(debug=True)
