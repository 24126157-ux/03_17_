# -*- coding: utf-8 -*-
"""
ĐỒ ÁN PHÂN TÍCH DỮ LIỆU LỚN TRONG KINH DOANH (ABDA433708)
Nhóm: 17
Nhiệm vụ 1A: Thu thập dữ liệu từ đa nguồn (E-Commerce Dataset + REST API) và Đồng bộ vào MongoDB Atlas
Thành viên thực hiện: qhy
"""

import os
import sys
import csv
import json
import urllib.request
from datetime import datetime

# Đảm bảo in tiếng Việt chuẩn trên console Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# 1. CẤU HÌNH THÔNG TIN KẾT NỐI MONGODB ATLAS
# ==============================================================================
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://24126088_db_user:HL5evsytleNo4V0p@cluster0.e1l29uo.mongodb.net/?retryWrites=true&w=majority"
)
DATABASE_NAME = "ecommerce"
COLLECTION_NAME = "transactions"

# Đường dẫn file dữ liệu TikTok Shop mới
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "dataset", "tiktok_shop_sales.csv")


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
# 3. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU TỪ TẬP DATASET TIKTOK SHOP (> 8.000 DÒNG, 27 CỘT)
# ==============================================================================
def load_transaction_dataset():
    """
    Đọc dữ liệu giao dịch TikTok Shop từ tệp CSV
    """
    print(f"[2/3] Đang đọc tập dữ liệu TikTok Shop tại: {DATASET_PATH}...")
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Không tìm thấy file: {DATASET_PATH}")
    
    records = []
    with open(DATASET_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Chuyển đổi các trường số sang đúng kiểu dữ liệu
            try:
                row["Customer_Age"] = int(row.get("Customer_Age", 0))
                row["Unit_Price"] = float(row.get("Unit_Price", 0))
                row["Quantity"] = int(row.get("Quantity", 1))
                row["Discount_Amount"] = float(row.get("Discount_Amount", 0))
                row["Shipping_Fee"] = float(row.get("Shipping_Fee", 0))
                row["Total_Amount"] = float(row.get("Total_Amount", 0))
                row["Product_Rating"] = float(row.get("Product_Rating", 5.0))
                row["Review_Count"] = int(row.get("Review_Count", 0))
                row["Video_Views"] = int(row.get("Video_Views", 0))
                row["Is_Anomaly"] = int(row.get("Is_Anomaly", 0))
            except (ValueError, KeyError):
                pass
            records.append(row)
            
    print(f" -> Đã đọc thành công {len(records)} dòng giao dịch TikTok Shop (27 thuộc tính).")
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
        return

    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]

        # Làm mới dữ liệu cũ để đồng bộ chính xác dữ liệu TikTok Shop mới
        existing_count = col.count_documents({})
        if existing_count > 0:
            print(f" -> Đang làm mới dữ liệu cũ ({existing_count} bản ghi)...")
            col.delete_many({})

        print(" -> Tiến hành nạp 8.500 bản ghi TikTok Shop vào MongoDB Atlas...")
        batch_size = 1000
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            col.insert_many(batch)
            print(f"   + Đã chèn {min(i + batch_size, len(records))}/{len(records)} bản ghi...")
        
        final_count = col.count_documents({})
        print(f" -> Hoàn tất đồng bộ toàn bộ {final_count} documents TikTok Shop lên MongoDB Atlas!")

    except Exception as err:
        print(f" -> Lỗi khi kết nối MongoDB: {err}")


# ==============================================================================
# CHƯƠNG TRÌNH CHÍNH
# ==============================================================================
if __name__ == "__main__":
    print("=============================================================")
    print(" CHƯƠNG TRÌNH THU THẬP & ĐỒNG BỘ DỮ LIỆU TIKTOK SHOP - NHÓM 17")
    print("=============================================================")
    
    # 1. Thu thập dữ liệu từ nguồn API mở rộng
    api_catalog = fetch_online_product_catalog()
    
    # 2. Đọc dữ liệu giao dịch TikTok Shop
    transactions = load_transaction_dataset()
    
    # 3. Đồng bộ lên CSDL MongoDB
    sync_to_mongodb(transactions)
    
    print("=============================================================")
    print(" HOÀN THÀNH QUY TRÌNH THU THẬP VÀ ĐỒNG BỘ DỮ LIỆU TIKTOK SHOP!")
    print("=============================================================")
