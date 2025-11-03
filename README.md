# FLASK_PROJECTS
Dự án sử dụng Flask framework với ngôn ngữ Python

--

## Cách sử dụng Bai thuc hanh so 3

B1: Chạy Flask_Router_JWT_v2

B2: Đăng nhập với trường
  Username: testuser
  Password: password123

B3: Chạy Bai_thuc_hanh_so_3 (Bài 2 chạy với port 5000, bài 3 chạy với port 5001)

## Sử dụng Order Service

### B1: Chạy cách trên

### Tạo một đơn hàng (vd):
URL: http://localhost:5002/orders 
Method: POST 
Headers: Authorization 
Body (JSON):
  {
    "customer_name": "Nguyen Van A",
    "customer_email": "vana@example.com",
    "total_amount": 0,
    "status": "pending"
  }

### Thêm một mặt hàng (vd):
URL: http://localhost:5002/order_items 
Method: POST 
Headers: Authorization 
Body (JSON):
{
  "order_id": 1,
  "product_id": 101,
  "product_name": "Bàn phím cơ",
  "quantity": 2,
  "unit_price": 500000
}
