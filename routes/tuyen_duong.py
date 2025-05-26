from flask import Blueprint, jsonify, json
from models.database import get_connection

tuyen_duong_bp = Blueprint('tuyen_duong', __name__)

@tuyen_duong_bp.route('/get-tuyen-duong', methods=['GET'])
def get_tuyen_duong():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, ST_AsGeoJSON(geom) FROM tuyen_duong;")
        result = cursor.fetchall()
        tuyen_list = []
        for row in result:
            tuyen_list.append({
                "name": row[0],
                "geom": json.loads(row[1])
            })
        return jsonify(tuyen_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500