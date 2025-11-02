# FP-Growth Association Rules Mining

Dự án triển khai thuật toán **FP-Growth từ đầu** (from scratch) để tìm luật kết hợp (association rules) từ dữ liệu giao hàng, phân tích cả **Quận (District)** và **Đường (Road)**.

## 📋 Mô tả

Dự án này sử dụng thuật toán FP-Growth (Frequent Pattern Growth) để khai phá các mẫu phổ biến và luật kết hợp từ dữ liệu giao hàng. Hệ thống được thiết kế mô-đun hóa, dễ bảo trì và mở rộng.

### Tính năng chính:

- ✅ **Thuật toán FP-Growth thuần túy**: Triển khai từ đầu, không sử dụng thư viện bên ngoài
- ✅ **Lọc thông minh**: Sử dụng Lift và Quality Score để lọc rules chất lượng cao
- ✅ **Chuẩn hóa dữ liệu**: Normalize tên quận và đường để tăng khả năng tìm patterns
- ✅ **Phân tích đa chiều**: Hỗ trợ phân tích cả Quận và Đường
- ✅ **Logging chi tiết**: Sử dụng `logging` standard library cho debugging

## 🏗️ Cấu trúc dự án

```
algorithms/
├── config.py              # Cấu hình và hằng số
├── data_handler.py        # Xử lý I/O và chuẩn hóa dữ liệu
├── core_fptree.py         # Thuật toán FP-Growth thuần túy
├── association_rules.py   # Tạo và lọc luật kết hợp
├── main.py                # File thực thi chính
├── README.md              # Tài liệu dự án
├── data/
│   └── optimized_routes_standard.csv  # Dữ liệu đầu vào
├── district_rules.csv     # Kết quả phân tích quận
└── road_rules.csv         # Kết quả phân tích đường
```

## 📦 Modules

### 1. `config.py` - Module Cấu hình
Chứa tất cả các hằng số, biến cấu hình, và thiết lập đường dẫn.

**Nội dung:**
- Đường dẫn file input/output
- Cấu hình cho phân tích District (min_support, min_confidence, min_lift, v.v.)
- Cấu hình cho phân tích Road
- Cấu hình logging

### 2. `data_handler.py` - Module Xử lý I/O
Chứa mọi logic I/O và chuẩn hóa dữ liệu.

**Functions:**
- `normalize_district_name(district)`: Chuẩn hóa tên quận (loại bỏ tiền tố 'Quận ', 'Huyện ', v.v.)
- `normalize_road_name(road)`: Chuẩn hóa tên đường (loại bỏ tiền tố 'Đường ', 'Phố ', v.v.)
- `load_transactions_from_csv(filepath, column_name)`: Đọc dữ liệu từ CSV và tạo transactions
- `save_rules_to_csv(rules, filepath, config)`: Lưu kết quả rules ra file CSV

### 3. `core_fptree.py` - Module Thuật toán FP-Growth
Chứa logic thuật toán FP-Growth thuần túy. **Module này không phụ thuộc vào bất kỳ module nào khác.**

**Classes:**
- `FPNode`: Đại diện cho một nút trong FP-Tree
- `FPTree`: Triển khai cấu trúc FP-Tree

**Functions:**
- `mine_fp_tree(transactions, min_support_count, prefix)`: Khai phá frequent itemsets bằng FP-Growth

### 4. `association_rules.py` - Module Luật Kết Hợp
Chứa logic tạo và lọc luật kết hợp từ frequent itemsets.

**Functions:**
- `filter_rules_by_quality(rules, config)`: Lọc rules theo Lift và Quality Score
- `generate_association_rules(frequent_itemsets, total_transactions, config)`: Tạo association rules

### 5. `main.py` - Module Thực Thi Chính
File điều phối luồng làm việc chính.

**Functions:**
- `run_analysis(transactions, config, analysis_name)`: Chạy phân tích FP-Growth
- `main()`: Hàm chính thực thi toàn bộ pipeline

## 🚀 Cài đặt và Chạy

### Yêu cầu hệ thống:
- Python 3.7+
- Không cần thư viện bên ngoài (chỉ sử dụng standard library)

### Cách chạy:

```bash
# Di chuyển vào thư mục dự án
cd algorithms

# Chạy chương trình
python main.py
```

### Cấu hình:

Chỉnh sửa file `config.py` để thay đổi các tham số:

```python
# Cấu hình cho phân tích Quận
DISTRICT_CONFIG = {
    'min_support': 0.01,         # Support tối thiểu (1%)
    'min_confidence': 0.5,       # Confidence tối thiểu (50%)
    'min_lift': 1.5,             # Lift tối thiểu (1.5)
    'min_quality_score': 0.4,    # Quality Score tối thiểu
    'max_rules': 500             # Số lượng rules tối đa
}
```

## 📊 Dữ liệu đầu vào

File CSV cần có các cột:
- `trip_id`: ID của chuyến giao hàng
- `district`: Tên quận
- `road_name`: Tên đường

**Ví dụ:**
```csv
trip_id,district,road_name
T001,Quận 1,Đường Nguyễn Huệ
T001,Quận 1,Đường Lê Lợi
T002,Quận 3,Phố Võ Văn Tần
```

## 📈 Kết quả đầu ra

### 1. `district_rules.csv` - Luật kết hợp cho Quận
```csv
antecedents,consequents,support,confidence,lift,quality_score
{'Quận 1'},{'Quận 3'},0.1234,0.8500,2.3456,1.9938
```

### 2. `road_rules.csv` - Luật kết hợp cho Đường
```csv
antecedents,consequents,support,confidence,lift,quality_score
{'Nguyễn Huệ'},{'Lê Lợi'},0.0567,0.7800,1.9876,1.5503
```

## 🔧 Metrics Giải thích

### Support
Tỷ lệ transactions chứa itemset trong tổng số transactions.
```
Support(A) = count(A) / total_transactions
```

### Confidence
Xác suất xuất hiện consequent khi có antecedent.
```
Confidence(A → B) = Support(A ∪ B) / Support(A)
```

### Lift
Đo mức độ mối quan hệ giữa antecedent và consequent.
```
Lift(A → B) = Confidence(A → B) / Support(B)
```
- Lift > 1: Có mối quan hệ dương (positive correlation)
- Lift = 1: Độc lập (independent)
- Lift < 1: Có mối quan hệ âm (negative correlation)

### Quality Score
Điểm chất lượng tổng hợp.
```
Quality Score = Confidence × Lift
```

## 🎯 Use Cases

### 1. Tối ưu hóa tuyến đường giao hàng
Xác định các quận/đường thường đi cùng nhau để tối ưu hóa lộ trình.

### 2. Dự đoán điểm giao hàng tiếp theo
Dựa trên các điểm đã đi qua, dự đoán điểm tiếp theo có khả năng cao.

### 3. Phân nhóm khu vực giao hàng
Nhóm các quận/đường có patterns tương tự để phân bổ tài nguyên hiệu quả.

## 🐛 Debugging

Chương trình sử dụng `logging` standard library. Log level có thể điều chỉnh trong `config.py`:

```python
LOG_LEVEL = 'INFO'  # Có thể thay đổi thành 'DEBUG', 'WARNING', 'ERROR'
```

Để xem thông tin chi tiết hơn, thay đổi thành `DEBUG`:
```python
LOG_LEVEL = 'DEBUG'
```

## 📝 Lưu ý

1. **Min Support Count**: Luôn được đảm bảo tối thiểu là 1 để tránh bỏ sót patterns
2. **Normalization**: Tên quận và đường được chuẩn hóa để tăng khả năng tìm patterns
3. **Quality Filtering**: Rules được lọc dựa trên nhiều tiêu chí để đảm bảo chất lượng cao