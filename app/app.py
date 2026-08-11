from flask import Flask, jsonify
import os
import psycopg2

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "appdb"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppassword")
    )


@app.route("/")
def home():
    return jsonify({
        "message": "Kubernetes CI/CD Demo - version 3",
        "status": "running"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/ready")
def ready():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result[0] == 1:
            return jsonify({
                "status": "ready",
                "database": "connected"
            }), 200

        return jsonify({
            "status": "not ready"
        }), 503

    except Exception as e:
        return jsonify({
            "status": "not ready",
            "database": "unavailable",
            "error": str(e)
        }), 503


@app.route("/users")
def users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users "
            "(id SERIAL PRIMARY KEY, name VARCHAR(100))"
        )

        cursor.execute(
            "SELECT id, name FROM users"
        )

        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify([
            {"id": row[0], "name": row[1]}
            for row in rows
        ])

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )