# app.py
from flask import Flask
from flask_cors import CORS

from routes.auth import auth_bp
from routes.ho_dan import ho_dan_bp
from routes.tuyen_duong import tuyen_duong_bp
from routes.thanh_toan import thanh_toan_bp

app = Flask(__name__)
CORS(app)

# Đăng ký các blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(ho_dan_bp)
app.register_blueprint(tuyen_duong_bp)
app.register_blueprint(thanh_toan_bp)

if __name__ == '__main__':
    app.run(debug=True)
