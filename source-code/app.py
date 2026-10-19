# -*- coding: utf-8 -*-
"""
ĐỒ ÁN PHÂN TÍCH DỮ LIỆU LỚN TRONG KINH DOANH (ABDA433708) - NHÓM 17
HỆ THỐNG PHÂN TÍCH VÀ QUẢN LÝ DỮ LIỆU TIKTOK SHOP (TIKTOK SHOP BIG DATA PORTAL)

Nhiệm vụ 1B: Thiết lập phân quyền người dùng dựa trên chức năng đăng nhập vào hệ thống (RBAC)
Thành viên thực hiện: Trần Quang Huy (qhy) - MSSV: 24126088
"""

import os
import sys
import math
import functools
from datetime import datetime

# Đảm bảo in tiếng Việt chuẩn trên console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import (
    Flask, render_template, request, redirect, 
    url_for, flash, session, g, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId

# ==============================================================================
# CẤU HÌNH ỨNG DỤNG FLASK
# ==============================================================================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "tiktok_shop_bigdata_hcmute_secret_key_2026")

# Chuỗi kết nối MongoDB Atlas của Nhóm 17
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://24126088_db_user:HL5evsytleNo4V0p@cluster0.e1l29uo.mongodb.net/?retryWrites=true&w=majority"
)
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "transactions"

client = None
db = None

def get_db():
    global client, db
    if db is None:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
    return db


# ==============================================================================
# KHỞI TẠO TÀI KHOẢN MẪU BAN ĐẦU (SEED USERS ĐỦ 4 VAI TRÒ RBAC)
# ==============================================================================
def init_default_users():
    """Tự động tạo các tài khoản mẫu với 4 vai trò rõ ràng để kiểm thử phân quyền"""
    try:
        database = get_db()
        users_col = database["users"]

        default_accounts = [
            {
                "username": "admin",
                "email": "admin@tiktokshop.hcmute.edu.vn",
                "fullname": "Trần Quang Huy (Admin)",
                "password_hash": generate_password_hash("admin123"),
                "role": "Admin",
                "department": "Quản Trị Hệ Thống",
                "created_at": datetime.now(),
                "status": "Active"
            },
            {
                "username": "analyst",
                "email": "analyst@tiktokshop.hcmute.edu.vn",
                "fullname": "Chuyên Viên Dữ Liệu (Analyst)",
                "password_hash": generate_password_hash("analyst123"),
                "role": "Analyst",
                "department": "Phân Tích Dữ Liệu Lớn (Big Data)",
                "created_at": datetime.now(),
                "status": "Active"
            },
            {
                "username": "staff",
                "email": "staff@tiktokshop.hcmute.edu.vn",
                "fullname": "Nhân Viên Vận Hành (Staff)",
                "password_hash": generate_password_hash("staff123"),
                "role": "Staff",
                "department": "Vận Hành Đơn Hàng & Livestream",
                "created_at": datetime.now(),
                "status": "Active"
            },
            {
                "username": "khachhang",
                "email": "khachhang@gmail.com",
                "fullname": "Khách Hàng Trải Nghiệm (User)",
                "password_hash": generate_password_hash("user123"),
                "role": "User",
                "department": "Khách Hàng Thành Viên",
                "created_at": datetime.now(),
                "status": "Active"
            }
        ]

        for acc in default_accounts:
            existing = users_col.find_one({"username": acc["username"]})
            if not existing:
                users_col.insert_one(acc)
                print(f"[RBAC SEED] Đã khởi tạo tài khoản mẫu: {acc['username']} ({acc['role']}).")

    except Exception as e:
        print(f"[WARNING] Lỗi khi kiểm tra/khởi tạo users: {e}")


# ==============================================================================
# MIDDLEWARE KIỂM TRA PHIÊN & PHÂN QUYỀN (RBAC - ROLE-BASED ACCESS CONTROL)
# ==============================================================================
@app.before_request
def load_logged_in_user():
    """Tải thông tin người dùng từ session trước mỗi request"""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        try:
            database = get_db()
            g.user = database["users"].find_one({"_id": ObjectId(user_id)})
            if not g.user or g.user.get("status") == "Locked":
                session.clear()
                g.user = None
        except Exception:
            g.user = None


def login_required(view):
    """Decorator yêu cầu đăng nhập trước khi truy cập bất kỳ tài nguyên nào"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Vui lòng đăng nhập để truy cập hệ thống!", "warning")
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


def roles_required(*allowed_roles):
    """Decorator phân quyền người dùng theo vai trò (RBAC)"""
    def decorator(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                flash("Vui lòng đăng nhập trước!", "warning")
                return redirect(url_for("login"))
            
            user_role = g.user.get("role", "User")
            if user_role not in allowed_roles:
                flash(
                    f"Truy cập bị từ chối! Chức năng này yêu cầu vai trò: {', '.join(allowed_roles)}. "
                    f"Vai trò hiện tại của bạn là '{user_role}'.", 
                    "danger"
                )
                return redirect(url_for("dashboard"))
            return view(**kwargs)
        return wrapped_view
    return decorator


# ==============================================================================
# CÁC ROUTE XÁC THỰC: ĐĂNG NHẬP, ĐĂNG KÝ, ĐĂNG XUẤT
# ==============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "").strip()

        if not identifier or not password:
            flash("Vui lòng điền đầy đủ tên đăng nhập/email và mật khẩu!", "danger")
            return render_template("login.html")

        try:
            database = get_db()
            user = database["users"].find_one({
                "$or": [{"username": identifier.lower()}, {"email": identifier.lower()}]
            })

            if user and check_password_hash(user["password_hash"], password):
                if user.get("status") == "Locked":
                    flash("Tài khoản của bạn đã bị Quản Trị Viên khóa. Vui lòng liên hệ Admin!", "danger")
                    return render_template("login.html")

                session.clear()
                session["user_id"] = str(user["_id"])
                session["username"] = user["username"]
                session["role"] = user.get("role", "User")
                session["fullname"] = user.get("fullname", user["username"])
                
                if f"({session['role']})" in session["fullname"]:
                    flash(f"Đăng nhập thành công! Chào mừng {session['fullname']}.", "success")
                else:
                    flash(f"Đăng nhập thành công! Chào mừng {session['fullname']} ({session['role']}).", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Tên đăng nhập hoặc mật khẩu không chính xác!", "danger")
        except Exception as e:
            flash(f"Lỗi kết nối cơ sở dữ liệu: {e}", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not email or not password:
            flash("Vui lòng điền đầy đủ các trường thông tin bắt buộc!", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Mật khẩu xác nhận không khớp!", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Mật khẩu phải có độ dài tối thiểu 6 ký tự!", "danger")
            return render_template("register.html")

        try:
            database = get_db()
            users_col = database["users"]

            if users_col.find_one({"$or": [{"username": username}, {"email": email}]}):
                flash("Tên tài khoản hoặc Email đã tồn tại trên hệ thống!", "warning")
                return render_template("register.html")

            # Người dùng đăng ký tự do mặc định nhận vai trò User
            new_user = {
                "username": username,
                "fullname": fullname if fullname else username,
                "email": email,
                "password_hash": generate_password_hash(password),
                "role": "User",
                "department": "Khách Hàng Thành Viên",
                "created_at": datetime.now(),
                "status": "Active"
            }
            users_col.insert_one(new_user)
            flash("Đăng ký tài khoản thành công! Bạn có thể đăng nhập ngay bây giờ.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            flash(f"Lỗi khi đăng ký tài khoản: {e}", "danger")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Bạn đã đăng xuất an toàn khỏi hệ thống.", "info")
    return redirect(url_for("login"))


# ==============================================================================
# ROUTE DASHBOARD: BẢNG ĐIỀU KHIỂN TRỰC QUAN HÓA THEO PHÂN QUYỀN (RBAC)
# ==============================================================================
@app.route("/")
@login_required
def dashboard():
    """Trang Dashboard hiển thị số liệu phân tích TikTok Shop tùy theo vai trò"""
    database = get_db()
    col_trans = database[COLLECTION_NAME]
    
    # Số liệu mặc định
    total_orders = 0
    total_revenue = 0
    avg_order_value = 0
    total_anomalies = 0
    recent_orders = []
    cat_stats = []
    traffic_stats = []
    top_creators = []
    total_users = 0

    try:
        total_orders = col_trans.count_documents({})

        # 1. Thống kê tổng doanh thu GMV
        pipeline_rev = [
            {"$group": {"_id": None, "totalRevenue": {"$sum": "$Total_Amount"}}}
        ]
        rev_res = list(col_trans.aggregate(pipeline_rev))
        total_revenue = rev_res[0]["totalRevenue"] if rev_res else 0
        avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0

        # 2. Thống kê đơn hàng bất thường (Anomaly Detection)
        total_anomalies = col_trans.count_documents({"Is_Anomaly": 1})

        # 3. Lấy 8 giao dịch TikTok Shop gần đây nhất
        recent_orders = list(col_trans.find().limit(8))

        # 4. Thống kê theo ngành hàng chính (Main_Category)
        pipeline_cat = [
            {"$group": {"_id": "$Main_Category", "count": {"$sum": 1}, "revenue": {"$sum": "$Total_Amount"}}},
            {"$sort": {"count": -1}},
            {"$limit": 6}
        ]
        cat_stats = list(col_trans.aggregate(pipeline_cat))

        # 5. Thống kê theo nguồn đơn (Traffic_Source - Livestream vs Video vs Showcase)
        pipeline_traffic = [
            {"$group": {"_id": "$Traffic_Source", "count": {"$sum": 1}, "revenue": {"$sum": "$Total_Amount"}}},
            {"$sort": {"count": -1}}
        ]
        traffic_stats = list(col_trans.aggregate(pipeline_traffic))

        # 6. Top Creators/KOLs mang lại doanh thu cao nhất trên TikTok Shop
        pipeline_creators = [
            {"$match": {"Creator_Name": {"$nin": ["None (Gian hàng trực tiếp)", "None (Tìm kiếm tự nhiên)"]}}},
            {"$group": {"_id": "$Creator_Name", "orders": {"$sum": 1}, "revenue": {"$sum": "$Total_Amount"}}},
            {"$sort": {"revenue": -1}},
            {"$limit": 5}
        ]
        top_creators = list(col_trans.aggregate(pipeline_creators))

        # 7. Thống kê người dùng
        total_users = database["users"].count_documents({})

    except Exception as e:
        flash(f"Lỗi khi truy vấn số liệu thống kê: {e}", "warning")

    return render_template(
        "dashboard.html",
        total_orders=total_orders,
        total_revenue=total_revenue,
        avg_order_value=avg_order_value,
        total_anomalies=total_anomalies,
        recent_orders=recent_orders,
        cat_stats=cat_stats,
        traffic_stats=traffic_stats,
        top_creators=top_creators,
        total_users=total_users
    )


# ==============================================================================
# ROUTE TRANSACTIONS: XEM & TÌM KIẾM DỮ LIỆU TIKTOK SHOP
# ==============================================================================
@app.route("/transactions")
@login_required
@roles_required("Admin", "Analyst", "Staff")
def view_transactions():
    """Trang xem và lọc dữ liệu TikTok Shop (Có hỗ trợ phân trang & lọc nâng cao)"""
    database = get_db()
    col_trans = database[COLLECTION_NAME]

    search_query = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    traffic_filter = request.args.get("traffic", "").strip()
    anomaly_filter = request.args.get("anomaly", "").strip()
    page = int(request.args.get("page", 1))
    per_page = 20

    query = {}
    if search_query:
        query["$or"] = [
            {"Order_ID": {"$regex": search_query, "$options": "i"}},
            {"Customer_Name": {"$regex": search_query, "$options": "i"}},
            {"Product_Name": {"$regex": search_query, "$options": "i"}},
            {"Creator_Name": {"$regex": search_query, "$options": "i"}},
            {"Shop_Name": {"$regex": search_query, "$options": "i"}},
            {"Shipping_City": {"$regex": search_query, "$options": "i"}}
        ]
    if status_filter:
        query["Order_Status"] = status_filter
    if traffic_filter:
        query["Traffic_Source"] = traffic_filter
    if anomaly_filter == "1":
        query["Is_Anomaly"] = 1
    elif anomaly_filter == "0":
        query["Is_Anomaly"] = 0

    try:
        total_found = col_trans.count_documents(query)
        total_pages = max(1, math.ceil(total_found / per_page))
        page = max(1, min(page, total_pages))
        skip_count = (page - 1) * per_page

        transactions = list(col_trans.find(query).skip(skip_count).limit(per_page))
    except Exception as e:
        transactions = []
        total_found = 0
        total_pages = 1
        flash(f"Lỗi truy vấn dữ liệu: {e}", "danger")

    return render_template(
        "transactions.html",
        transactions=transactions,
        total_found=total_found,
        page=page,
        total_pages=total_pages,
        search_query=search_query,
        status_filter=status_filter,
        traffic_filter=traffic_filter,
        anomaly_filter=anomaly_filter
    )


# ==============================================================================
# NHIỆM VỤ 1B CỐT LÕI: QUẢN LÝ NGƯỜI DÙNG & PHÂN QUYỀN (CHỈ DÀNH CHO ADMIN)
# ==============================================================================
@app.route("/users")
@login_required
@roles_required("Admin")
def user_management():
    """Trang quản trị người dùng và phân quyền (RBAC) - CHỈ ADMIN MỚI CÓ QUYỀN TRUY CẬP"""
    database = get_db()
    users_col = database["users"]
    all_users = list(users_col.find())
    return render_template("users.html", users=all_users)


@app.route("/users/create", methods=["POST"])
@login_required
@roles_required("Admin")
def create_user():
    """Admin tạo tài khoản mới và cấp quyền trực tiếp"""
    username = request.form.get("username", "").strip().lower()
    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "User")
    department = request.form.get("department", "Nhân Viên")

    if not username or not email or not password:
        flash("Vui lòng điền đầy đủ tên đăng nhập, email và mật khẩu!", "danger")
        return redirect(url_for("user_management"))

    if role not in ["Admin", "Analyst", "Staff", "User"]:
        flash("Vai trò phân quyền không hợp lệ!", "danger")
        return redirect(url_for("user_management"))

    try:
        database = get_db()
        users_col = database["users"]

        if users_col.find_one({"$or": [{"username": username}, {"email": email}]}):
            flash("Tên đăng nhập hoặc Email đã tồn tại!", "warning")
            return redirect(url_for("user_management"))

        new_user = {
            "username": username,
            "fullname": fullname if fullname else username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": role,
            "department": department,
            "created_at": datetime.now(),
            "status": "Active"
        }
        users_col.insert_one(new_user)
        flash(f"Đã tạo thành công tài khoản '{username}' với vai trò: {role}!", "success")
    except Exception as e:
        flash(f"Lỗi khi tạo tài khoản: {e}", "danger")

    return redirect(url_for("user_management"))


@app.route("/users/update-role", methods=["POST"])
@login_required
@roles_required("Admin")
def update_user_role():
    """Chức năng thay đổi vai trò (Role) của người dùng"""
    user_id = request.form.get("user_id")
    new_role = request.form.get("role")
    
    if new_role not in ["Admin", "Analyst", "Staff", "User"]:
        flash("Vai trò phân quyền không hợp lệ!", "danger")
        return redirect(url_for("user_management"))

    # Ngăn Admin tự hạ quyền của chính mình nếu là Admin duy nhất
    if str(g.user["_id"]) == user_id and new_role != "Admin":
        flash("Cảnh báo an toàn: Bạn không thể tự hạ quyền Admin của chính mình!", "warning")
        return redirect(url_for("user_management"))

    try:
        database = get_db()
        database["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role}}
        )
        flash(f"Đã cập nhật phân quyền thành công sang: {new_role}!", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật quyền: {e}", "danger")

    return redirect(url_for("user_management"))


@app.route("/users/toggle-status", methods=["POST"])
@login_required
@roles_required("Admin")
def toggle_user_status():
    """Khóa hoặc kích hoạt tài khoản người dùng"""
    user_id = request.form.get("user_id")
    current_status = request.form.get("status")
    new_status = "Locked" if current_status == "Active" else "Active"

    if str(g.user["_id"]) == user_id:
        flash("Bạn không thể tự khóa tài khoản của chính mình!", "warning")
        return redirect(url_for("user_management"))

    try:
        database = get_db()
        database["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"status": new_status}}
        )
        action_text = "khóa" if new_status == "Locked" else "mở khóa"
        flash(f"Đã {action_text} tài khoản thành công!", "info")
    except Exception as e:
        flash(f"Lỗi khi đổi trạng thái: {e}", "danger")

    return redirect(url_for("user_management"))


@app.route("/users/delete", methods=["POST"])
@login_required
@roles_required("Admin")
def delete_user():
    """Xóa tài khoản người dùng khỏi hệ thống"""
    user_id = request.form.get("user_id")

    if str(g.user["_id"]) == user_id:
        flash("Bạn không thể tự xóa tài khoản của chính mình!", "danger")
        return redirect(url_for("user_management"))

    try:
        database = get_db()
        database["users"].delete_one({"_id": ObjectId(user_id)})
        flash("Đã xóa tài khoản người dùng thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi xóa người dùng: {e}", "danger")

    return redirect(url_for("user_management"))


# ==============================================================================
# ROUTE PROFILE: THÔNG TIN HỒ SƠ CÁ NHÂN & ĐỔI MẬT KHẨU
# ==============================================================================
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Trang thông tin cá nhân của người dùng và đổi mật khẩu"""
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        current_password = request.form.get("current_password", "").strip()
        new_password = request.form.get("new_password", "").strip()

        database = get_db()
        users_col = database["users"]

        updates = {}
        if fullname:
            updates["fullname"] = fullname

        if current_password and new_password:
            if not check_password_hash(g.user["password_hash"], current_password):
                flash("Mật khẩu hiện tại không chính xác!", "danger")
                return render_template("profile.html")
            if len(new_password) < 6:
                flash("Mật khẩu mới phải có tối thiểu 6 ký tự!", "danger")
                return render_template("profile.html")
            updates["password_hash"] = generate_password_hash(new_password)

        if updates:
            try:
                users_col.update_one({"_id": g.user["_id"]}, {"$set": updates})
                flash("Đã cập nhật thông tin cá nhân thành công!", "success")
            except Exception as e:
                flash(f"Lỗi cập nhật hồ sơ: {e}", "danger")

    return render_template("profile.html")


# ==============================================================================
# ROUTE API: THỐNG KÊ NHANH DẠNG JSON
# ==============================================================================
@app.route("/api/summary")
@login_required
def api_summary():
    """API trả về JSON tóm tắt số liệu (hỗ trợ kiểm thử và tích hợp)"""
    database = get_db()
    col_trans = database[COLLECTION_NAME]
    return jsonify({
        "status": "success",
        "total_orders": col_trans.count_documents({}),
        "total_anomalies": col_trans.count_documents({"Is_Anomaly": 1}),
        "total_users": database["users"].count_documents({}),
        "current_user": {
            "username": g.user["username"],
            "role": g.user.get("role", "User")
        }
    })


# ==============================================================================
# KHỞI CHẠY ỨNG DỤNG
# ==============================================================================
if __name__ == "__main__":
    init_default_users()
    print("=============================================================")
    print(" HỆ THỐNG TIKTOK SHOP BIG DATA PORTAL (NHÓM 17)")
    print(" ĐANG CHẠY TẠI ĐỊA CHỈ: http://127.0.0.1:5000")
    print("=============================================================")
    app.run(host="0.0.0.0", port=5000, debug=True)
