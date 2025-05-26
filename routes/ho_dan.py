from flask import Blueprint, request, jsonify, json
from datetime import datetime, date
from models.database import get_connection

ho_dan_bp = Blueprint('ho_dan', __name__)

@ho_dan_bp.route('/get-thongtin', methods=['POST'])
def get_thongtin():
    # Lấy dữ liệu latitude, longitude từ request
    data = request.get_json()
    lat, lng = data['lat'], data['lng']
    
    # Kết nối đến cơ sở dữ liệu PostgreSQL
    conn = get_connection()

    try:
        # Truy vấn dữ liệu từ bảng thong_tin_thanh_toan
        sql = """
            SELECT 
                d.id_hodan, 
                d.ten_chu_ho, 
                d.diachi, 
                t.trang_thai, 
                t.thang_nam, 
                ST_AsGeoJSON(d.geom) AS geom  -- Chuyển đổi cột geom thành GeoJSON
            FROM ho_dan d join thanh_toan t on d.id_hodan = t.id_hodan
            WHERE ST_Contains(geom, ST_SetSRID(ST_Point(%s, %s), 4326))
        """
        
        cur = conn.cursor()
        cur.execute(sql, (lng, lat))  # Lưu ý thứ tự lng, lat
        row = cur.fetchone()

        if row:
            # Trả về thông tin hộ dân dưới dạng JSON
            return jsonify({
                'id_hodan': row[0],
                'ten_chu_ho': row[1],
                'diachi': row[2],
                'trang_thai': row[3],
                'thang_nam': row[4],
                'geom': row[5]  # Trả về GeoJSON cho geom
            })
        else:
            return jsonify({'message': 'Không tìm thấy hộ dân tại vị trí này.'}), 404
    except Exception as e:
        # Xử lý lỗi
        return jsonify({'message': f"Lỗi khi truy vấn cơ sở dữ liệu: {str(e)}"}), 500
    finally:
        # Đảm bảo đóng kết nối
        conn.close()

@ho_dan_bp.route('/get-thongtin-all', methods=['POST'])
def get_thongtin_all():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                d.id_hodan, 
                d.ten_chu_ho, 
                d.diachi, 
                t.trang_thai, 
                t.thang_nam, 
                ST_AsGeoJSON(d.geom) AS geom  -- Chuyển đổi cột geom thành GeoJSON
            FROM ho_dan d join thanh_toan t on d.id_hodan = t.id_hodan
            LIMIT 100
        """)
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append({
                'id_hodan': row[0],
                'ten_chu_ho': row[1] ,
                'diachi': row[2] ,
                'trang_thai': row[3] ,
                'thang_nam': row[4] ,
                'geom': row[5]
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({'message': f"Lỗi: {str(e)}"}), 500
    finally:
        conn.close()

@ho_dan_bp.route('/update-trang-thai', methods=['POST'])
def update_trang_thai():
    data = request.get_json()
    print("Received data:", data)
    try:
        id_hodan = data['id_hodan']
        trang_thai = data.get('trang_thai', 'Đã thanh toán')
        id_nv = data.get('id_nv')

        if not id_nv:
            return jsonify({'message': 'Thiếu id_nv'}), 400
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
           INSERT INTO thanh_toan (id_hodan, trang_thai, id_nv)
            VALUES (%s, %s, %s)
            ON CONFLICT (id_hodan, thang_nam)
            DO UPDATE SET 
                trang_thai = EXCLUDED.trang_thai,
                ngay_thu = CURRENT_DATE,
                id_nv = EXCLUDED.id_nv;
        """, (id_hodan, trang_thai, id_nv))

        conn.commit()
        return jsonify({'message': 'Cập nhật thành công'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': f"Lỗi: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@ho_dan_bp.route('/suggest-ho-dan', methods=['POST'])
def suggest_ho_dan():
    data = request.get_json()
    keyword = data.get('keyword', '').lower()

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                d.id_hodan, 
                d.ten_chu_ho, 
                d.diachi, 
                t.trang_thai, 
                t.thang_nam, 
                ST_AsGeoJSON(d.geom) AS geom  -- Chuyển đổi cột geom thành GeoJSON
            FROM ho_dan d join thanh_toan t on d.id_hodan = t.id_hodan
            WHERE LOWER(ten_chu_ho) LIKE %s OR LOWER(diachi) LIKE %s
        """, [f"%{keyword}%", f"%{keyword}%"])
        results = cur.fetchall()
        suggestions = [{
            'id_hodan': r[0],
            'ten_chu_ho': r[1],
            'diachi': r[2]
        } for r in results]
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@ho_dan_bp.route('/get-ho-dan-by-id/<int:id_hodan>', methods=['GET'])
def get_ho_dan_by_id(id_hodan):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id_hodan, ten_chu_ho, diachi, ST_AsGeoJSON(geom)
            FROM ho_dan
            WHERE id_hodan = %s
        """, (id_hodan,))
        row = cur.fetchone()
        if row:
            return jsonify({
                'id_hodan': row[0],
                'ten_chu_ho': row[1],
                'diachi': row[2],
                'geom': json.loads(row[3])
            })
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
