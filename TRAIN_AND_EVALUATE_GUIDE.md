# 🚀 Train and Evaluate Script - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

Script `train_and_evaluate.py` là công cụ hoàn chỉnh để **train, test và đánh giá** thuật toán FP-Growth trên dữ liệu delivery routes với phương pháp **80/20 train-test split**.

### 🎯 Mục Đích
1. **Chia dữ liệu**: Split 80% train / 20% test theo route_id
2. **Train FP-Growth**: Học association rules từ tập train
3. **Test độ chính xác**: Đánh giá bằng Precision@1, @3, @5
4. **Sinh tuyến đường**: Tối ưu routes từ orders mới

---

## 🏗️ Kiến Trúc Script

### Workflow Chính
```
📊 PHẦN 1: Chia dữ liệu (80/20)
    ↓
🎓 PHẦN 2: Train FP-Growth
    ├── Train luật quận (district)
    └── Train luật đường (road_name)
    ↓
🎯 PHẦN 3: Test độ chính xác
    ├── Test luật quận
    ├── Test luật đường
    └── Tính trung bình Precision@K
    ↓
🚚 PHẦN 4: Sinh tuyến đường
    └── Apply rules lên orders.csv
```

---

## ⚙️ Cấu Hình Quan Trọng

### File: `config.py`

```python
# Cấu hình cho phân tích Quận
DISTRICT_CONFIG = {
    'min_support': 0.02,         # 2% - Patterns xuất hiện ≥2% transactions
    'min_confidence': 0.3,       # 30% - Độ tin cậy tối thiểu
    'min_lift': 1.2,             # Lift ≥1.2 (tăng 20%+)
    'min_quality_score': 0.3,    # Quality score = confidence × lift
    'max_rules': 500             # Giới hạn số rules tối đa
}

# Cấu hình cho phân tích Đường
ROAD_CONFIG = {
    'min_support': 0.01,         # 1% - Cho phép patterns hiếm hơn
    'min_confidence': 0.4,       # 40%
    'min_lift': 1.2,
    'min_quality_score': 0.4,
    'max_rules': 1000
}
```

### Ý Nghĩa Tham Số

| Tham số | Ý nghĩa | Giá trị thấp | Giá trị cao |
|---------|---------|--------------|-------------|
| `min_support` | Tần suất xuất hiện | Nhiều rules, chậm | Ít rules, nhanh |
| `min_confidence` | Độ tin cậy | Nhiều rules yếu | Ít rules mạnh |
| `min_lift` | Mức độ quan trọng | Nhiều rules tầm thường | Ít rules có ý nghĩa |

---

## 🔧 Các Hàm Chính

### 1. Data Processing

#### `split_data_by_routes(data_file, train_ratio=0.8)`
Chia dữ liệu theo **route_id** (không phải transactions) để tránh data leakage.

```python
# Input: 9,447 routes
# Output: 7,557 train routes (80%) + 1,890 test routes (20%)
```

#### `prepare_transactions(df, column_name, min_length=2)`
Chuẩn bị transactions với **loại bỏ duplicates liền kề**, giữ nguyên thứ tự.

```python
# Input:  ['A', 'B', 'B', 'C', 'B', 'D']
# Output: ['A', 'B', 'C', 'B', 'D']  # Loại 'B' trùng, giữ 'B' khác vị trí
```

**⚠️ Quan trọng**: Khác với `set()` - không làm mất thứ tự!

---

### 2. Training

#### `train_single_type(df, column_name, config, type_name, output_file)`
Train FP-Growth cho một loại (quận hoặc đường).

**Quy trình**:
1. Prepare transactions → loại duplicates liền kề
2. Mine FP-tree → tìm frequent patterns
3. Generate association rules → tạo rules từ patterns
4. Filter rules → áp dụng min_confidence, min_lift
5. Save to CSV → lưu kết quả

**Output**: List of rules với format:
```python
{
    'antecedents': {'A', 'B'},      # Điều kiện
    'consequents': {'C'},           # Kết quả
    'confidence': 0.85,             # 85% tin cậy
    'lift': 2.3,                    # Tăng 130%
    'support': 0.05,                # Xuất hiện 5%
    'quality_score': 1.955          # confidence × lift
}
```

---

### 3. Prediction Algorithm

#### `predict_next_locations(current_path, rules, top_k=5)`
Dự đoán vị trí tiếp theo bằng **sequence-aware voting**.

**Cải tiến quan trọng**:
```python
# ❌ Cũ: dùng set() - mất thứ tự
current_set = set(current_path)  

# ✅ Mới: giữ sequence + position bonus
recent_items = set(current_path[-3:])  # 3 items cuối
overlap = len(ant & recent_items) / len(ant)
position_bonus = 1.0 + overlap  # Bonus 0-100%
```

**Logic**:
1. Duyệt qua tất cả rules
2. Check `antecedents ⊆ current_path` (subset)
3. Tính score = `confidence × quality_score × position_bonus`
4. Ưu tiên rules khớp với **recent context** (3 items cuối)
5. Return top-K candidates

---

### 4. Evaluation

#### `calculate_precision_at_k(test_routes, parsed_rules)`
Tính độ chính xác dự đoán.

**Metrics**:
- **Precision@1**: Top-1 prediction đúng
- **Precision@3**: Actual trong top-3 predictions
- **Precision@5**: Actual trong top-5 predictions

**Cách tính**:
```python
for each route in test_routes:
    for each position i:
        current = route[:i+1]
        actual_next = route[i+1]
        predictions = predict_next_locations(current, rules, top_k=5)
        
        if predictions[0] == actual_next:
            correct_at_1 += 1  # và @3, @5
        elif actual_next in predictions[:3]:
            correct_at_3 += 1  # và @5
        elif actual_next in predictions[:5]:
            correct_at_5 += 1

P@K = correct_at_K / total_predictions * 100
```

---

## 📊 Hiểu Kết Quả

### Ví Dụ Output

```
======================================================================
🎯 PHẦN 3: TEST ĐỘ CHÍNH XÁC (TẬP TEST 20%)
======================================================================

📍 Test với LUẬT QUẬN:
   • Tổng dự đoán: 4913
   • Precision@1: 12.27% (603/4913)   ← 12.27% top-1 đúng
   • Precision@3: 24.45% (1201/4913)  ← 24.45% trong top-3
   • Precision@5: 31.63% (1554/4913)  ← 31.63% trong top-5

🛣️  Test với LUẬT ĐƯỜNG:
   • Tổng dự đoán: 9043
   • Precision@1: 5.09% (460/9043)
   • Precision@3: 10.09% (912/9043)
   • Precision@5: 13.45% (1216/9043)

📊 TỔNG KẾT ĐỘ CHÍNH XÁC:
   • Precision@1: 8.68%
   • Precision@3: 17.27%
   • Precision@5: 22.54%
   ✅ Độ chính xác TỐT (P@5: 20-30%)
```

### Thang Đánh Giá

| P@5 | Đánh giá | Ý nghĩa |
|-----|----------|---------|
| <10% | ❌ Thấp | Cần cải thiện config/algorithm |
| 10-20% | ⚠️ Trung bình | Chấp nhận được |
| 20-30% | ✅ Tốt | Đạt mục tiêu |
| ≥30% | 🏆 Xuất sắc | Rất tốt |

---

## 🚀 Cách Sử Dụng

### Chạy Script Cơ Bản
```bash
python train_and_evaluate.py
```

### Output Files
```
output/
├── district_rules_trained.csv   # 500 luật quận từ 80% data
├── road_rules_trained.csv       # 1000 luật đường từ 80% data
└── final_routes.csv             # 25 tuyến đường tối ưu từ orders
```

---

## ⚡ Tối Ưu Hiệu Suất

### Vấn Đề: Train Chậm

**Nguyên nhân**: `min_support` quá thấp → quá nhiều patterns → đệ quy sâu

**Giải pháp**:
```python
# Nếu train lâu hơn 5 phút, tăng min_support:
DISTRICT_CONFIG['min_support'] = 0.05  # 5% thay vì 2%
ROAD_CONFIG['min_support'] = 0.02      # 2% thay vì 1%
```

### Vấn Đề: Độ Chính Xác Thấp

**Giải pháp**:
1. **Giảm min_support** → nhiều patterns hơn
2. **Giảm min_confidence** → nhiều rules hơn
3. **Kiểm tra data quality** → đảm bảo routes hợp lệ

---

## 🔍 So Sánh với main.py

| Aspect | main.py | train_and_evaluate.py |
|--------|---------|------------------------|
| **Mục đích** | Production training | Evaluation & validation |
| **Dữ liệu** | 100% data | 80% train / 20% test |
| **Đánh giá** | Không có | Precision@1,3,5 |
| **Use case** | Train model cuối | Thử nghiệm & tối ưu |
| **Output** | Rules tốt nhất | Rules + metrics + routes |

---

## 📈 Lịch Sử Cải Tiến

### Version 1.0 (Ban đầu)
- ❌ Dùng `set()` → mất thứ tự
- ❌ Min_support quá cao (10%)
- ❌ Test routes có duplicates
- ❌ P@5 = 7.68% (Thấp)

### Version 2.0 (Hiện tại)
- ✅ Sequence-aware prediction với position bonus
- ✅ Deduplicate liền kề, giữ thứ tự
- ✅ Config tối ưu (2% / 1% support)
- ✅ P@5 = 22.54% (Tốt) - **Tăng 193%!**

---

## 🎓 Key Takeaways

### 1. **Data Split Đúng Cách**
Chia theo **route_id**, không phải transactions → tránh data leakage

### 2. **Sequence Matters!**
Không dùng `set()` - phải giữ nguyên thứ tự items trong route

### 3. **Position Bonus**
Rules khớp với **recent context** (3 items cuối) quan trọng hơn

### 4. **Balance Speed vs Accuracy**
- Support thấp = chậm, nhiều rules, accuracy cao
- Support cao = nhanh, ít rules, accuracy thấp

### 5. **Evaluation Strategy**
- Train trên 80% → tạo model
- Test trên 20% độc lập → đo accuracy thực tế
- Không bao giờ test trên train data!

---

## 🐛 Troubleshooting

### Script Chạy Chậm (>5 phút)
```python
# Tăng min_support trong config.py
DISTRICT_CONFIG['min_support'] = 0.05  # từ 0.02
ROAD_CONFIG['min_support'] = 0.02      # từ 0.01
```

### Không Sinh Được Rules
```python
# Giảm các thresholds
config['min_confidence'] = 0.2
config['min_lift'] = 1.1
```

### Lỗi "KeyError" hoặc "TypeError"
- Kiểm tra format CSV input
- Đảm bảo có cột `trip_id`, `district`, `road_name`

---

## 📚 References

- **FP-Growth Algorithm**: `core_fptree.py`
- **Association Rules**: `association_rules.py`
- **Data Handler**: `data_handler.py`
- **Configuration**: `config.py`

---

## 🤝 Contributors

Developed and optimized through iterative improvements focusing on:
- Sequence-aware prediction
- Proper train-test splitting
- Performance optimization
- Comprehensive evaluation metrics

---

**Last Updated**: November 2025  
**Status**: ✅ Production Ready  
**Performance**: P@5 = 22.54% (Tốt)
