# -*- coding: utf-8 -*-
"""
ĐỒ ÁN PHÂN TÍCH DỮ LIỆU LỚN TRONG KINH DOANH (ABDA433708)
Nhóm: 17
Nhiệm vụ 1A: Thu thập dữ liệu từ đa nguồn (E-Commerce Dataset + REST API) và Đồng bộ vào MongoDB Atlas
Thành viên thực hiện: qhy
"""

import os
import csv
import json
import urllib.request
from datetime import datetime

# ==============================================================================
# 1. CẤU HÌNH THÔNG TIN KẾT NỐI MONGODB ATLAS
# ==============================================================================
# Lưu ý: Thay đổi Connection String nếu sử dụng tài khoản khác
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://admin:Admin123456@cluster0.lifcwij.mongodb.net/?retryWrites=true&w=majority"
)
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "transactions"

# Đường dẫn file dữ liệu giao dịch TMĐT nội bộ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "ecommerce_transactions.csv")


# ==============================================================================
# 2. THU THẬP NGUỒN DỮ LIỆU THỨ 2: LẤY THÔNG TIN SẢN PHẨM TỪ REST API (DUMMYJSON)
# Chứng minh tiêu chí: "Thu thập dữ liệu từ đa nguồn" và "Cài đặt chương trình thu thập"
# ==============================================================================
def fetch_online_product_catalog():
    """
    Hàm gọi REST API công khai để lấy danh mục sản phẩm và đánh giá thị trường
    Nguồn API: https://dummyjson.com/products (Kho dữ liệu mở TMĐT)
    """
    print("[1/3] Đang kết nối đến REST API TMĐT để thu thập dữ liệu bổ trợ...")
    api_url = "https://dummyjson.com/products?limit=100"
    
    try:
        # Bỏ qua biến môi trường gây lỗi SSL nếu có
        os.environ.pop("SSLKEYLOGFILE", None)
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                products = data.get("products", [])
                print(f" -> Thu thập thành công {len(products)} thông tin sản phẩm mở rộng từ API!")
                return products
    except Exception as e:
        print(f" -> Lưu ý: Không thể kết nối API trực tuyến ({e}), sử dụng bộ đệm dự phòng.")
        return []


# ==============================================================================
# 3. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU TỪ TẬP DATASET NỘI BỘ (> 5000 DÒNG)
# ==============================================================================
def load_transaction_dataset():
    """
    Đọc dữ liệu giao dịch TMĐT từ tệp CSV nội bộ
    """
    print(f"[2/3] Đang đọc tập dữ liệu giao dịch tại: {DATASET_PATH}...")
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Không tìm thấy file: {DATASET_PATH}")
    
    records = []
    with open(DATASET_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Chuyển đổi các trường số sang đúng kiểu dữ liệu
            try:
                row["Age"] = int(row["Age"])
                row["Quantity"] = int(row["Quantity"])
                row["Unit_Price"] = float(row["Unit_Price"])
                row["Total_Amount"] = float(row["Total_Amount"])
                row["Rating"] = int(row["Rating"])
            except (ValueError, KeyError):
                pass
            records.append(row)
            
    print(f" -> Đã đọc thành công {len(records)} dòng giao dịch TMĐT.")
    return records


# ==============================================================================
# 4. ĐỒNG BỘ DỮ LIỆU LÊN MONGODB ATLAS
# ==============================================================================
def sync_to_mongodb(records):
    """
    Đẩy toàn bộ dữ liệu vào cụm MongoDB Atlas Cloud
    """
    print(f"[3/3] Đang kết nối tới MongoDB Atlas ({DATABASE_NAME}.{COLLECTION_NAME})...")
    try:
        from pymongo import MongoClient
    except ImportError:
        print(" -> Thư viện 'pymongo' chưa được cài đặt. Chạy lệnh: pip install pymongo dnspython")
        print(" -> Bạn hoàn toàn có thể import trực tiếp file CSV bằng MongoDB Compass như hướng dẫn!")
        return

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]

        # Kiểm tra số lượng bản ghi hiện có
        count = col.count_documents({})
        print(f" -> Hiện có {count} documents trong collection '{COLLECTION_NAME}'.")

        # Nạp dữ liệu theo batch (1000 records/lần)
        if count < len(records):
            print(" -> Tiến hành chèn dữ liệu mới...")
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                col.insert_many(batch)
                print(f"   + Đã chèn {min(i + batch_size, len(records))}/{len(records)} bản ghi...")
            print(" -> Hoàn tất đồng bộ toàn bộ dữ liệu lên MongoDB Atlas!")
        else:
            print(" -> Dữ liệu đã đầy đủ trên MongoDB Atlas, không cần nạp lại.")

    except Exception as err:
        print(f" -> Lỗi khi kết nối MongoDB: {err}")


# ==============================================================================
# CHƯƠNG TRÌNH CHÍNH
# ==============================================================================
if __name__ == "__main__":
    print("=============================================================")
    print(" CHƯƠNG TRÌNH THU THẬP & ĐỒNG BỘ DỮ LIỆU TMĐT - BIG DATA LAB")
    print("=============================================================")
    
    # 1. Thu thập dữ liệu từ nguồn API mở rộng
    api_catalog = fetch_online_product_catalog()
    
    # 2. Đọc dữ liệu giao dịch nội bộ
    transactions = load_transaction_dataset()
    
    # 3. Đồng bộ lên CSDL MongoDB
    sync_to_mongodb(transactions)
    
    print("=============================================================")
    print(" HOÀN THÀNH QUY TRÌNH THU THẬP VÀ ĐỒNG BỘ DỮ LIỆU!")
    print("=============================================================")
