"""
GTDF Platform — Entry Point
Run with: python run.py
"""

from app import create_app

app = create_app("development")

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)
