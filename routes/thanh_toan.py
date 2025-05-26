from flask import Blueprint, request, jsonify, json
from datetime import datetime, date
from models.database import get_connection

thanh_toan_bp = Blueprint('thanh_toan', __name__)

@thanh_toan_bp.route('/thongke-trangthai', methods=['GET'])
def thongke_trangthai():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT trang_thai, COUNT(*) 
            FROM thanh_toan 
            GROUP BY trang_thai
        """)
        data = cur.fetchall()
        return jsonify([{'trang_thai': row[0], 'so_luong': row[1]} for row in data])
    finally:
        conn.close()

# from math import ceil

@thanh_toan_bp.route('/danhsach', methods=['GET'])
def danhsach_thanh_toan():
    page = int(request.args.get('page', 1))
    per_page = 50
    offset = (page - 1) * per_page

    trang_thai = request.args.get('trang_thai')
    thang_nam = request.args.get('thang_nam')
    ngay = request.args.get('ngay')  # định dạng yyyy-MM-dd

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Tạo điều kiện lọc động
        where_clauses = []
        params = []

        if trang_thai:
            where_clauses.append("trang_thai = %s")
            params.append(trang_thai)

        if thang_nam:
            where_clauses.append("to_char(ngay_thu, 'MM/YYYY') = %s")
            params.append(thang_nam)

        if ngay:
            where_clauses.append("ngay_thu = %s")
            params.append(ngay)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Đếm tổng
        cur.execute(f"SELECT COUNT(*) FROM thanh_toan {where_sql}", params)
        total_count = cur.fetchone()[0]
        total_pages = (total_count + per_page - 1) // per_page

        # Truy vấn chính
        cur.execute(f"""
            SELECT id_thanh_toan, id_hodan, so_tien, ngay_thu, trang_thai 
            FROM thanh_toan
            {where_sql}
            ORDER BY ngay_thu DESC NULLS LAST
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])

        rows = cur.fetchall()
        results = []
        for r in rows:
            results.append({
                'id': r[0],
                'id_hodan': r[1],
                'so_tien': float(r[2]) if r[2] is not None else 0.0,
                'ngay_thu': r[3].strftime('%d/%m/%Y') if r[3] else None,
                'trang_thai': r[4]
            })

        return jsonify({
            'results': results,
            'total_pages': total_pages
        })
    finally:
        conn.close()



# @thanh_toan_bp.route('/danhsach', methods=['GET'])
# def danhsach_thanh_toan():
#     page = int(request.args.get('page', 1))
#     per_page = 50
#     offset = (page - 1) * per_page

#     conn = get_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute("""
#             SELECT id_thanh_toan, id_hodan, so_tien, ngay_thu, trang_thai 
#             FROM thanh_toan
#             ORDER BY ngay_thu DESC NULLS LAST
#             LIMIT %s OFFSET %s
#         """, (per_page, offset))
#         rows = cur.fetchall()

#         results = []
#         for r in rows:
#             results.append({
#                 'id': r[0],
#                 'id_hodan': r[1],
#                 'so_tien': float(r[2]) if r[2] is not None else 0.0,
#                 'ngay_thu': r[3].isoformat() if r[3] else None,
#                 'trang_thai': r[4]
#             })

#         return jsonify({
#             'results': results,
#             'total_pages': 1  # bạn có thể bổ sung COUNT(*) nếu cần phân trang thực sự
#         })
#     finally:
#         conn.close()

