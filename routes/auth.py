# routes/auth.py
from flask import Blueprint, request, jsonify
from models.database import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""   
            SELECT u.id_nv, n.chuc_vu
            FROM users u join nhan_vien n on u.id_nv = n.id_nv
            WHERE username = %s AND password = crypt(%s, password)
        """, (username, password))
        result = cur.fetchone()
        if result:
            id_nv, chuc_vu  = result
            return jsonify({
                'message': 'Đăng nhập thành công',
                'id_nv': id_nv,
                'chuc_vu': chuc_vu,
            })
        else:
            return jsonify({'message': 'Sai tài khoản hoặc mật khẩu'}), 401
    finally:
        conn.close()


