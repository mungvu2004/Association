# 🚚 Generate Routes Guide

> **Script để tạo tuyến đường tối ưu từ orders sử dụng association rules đã train**

---

## 📋 Tổng Quan

`generate_routes.py` là script **ĐỘC LẬP** để tạo tuyến đường giao hàng từ danh sách orders, sử dụng association rules đã được train trước đó.

### 🎯 Mục Đích

- Nhận vào: **Orders CSV** (danh sách đơn hàng cần giao)
- Sử dụng: **District Rules** + **Road Rules** (đã train từ `main.py`)
- Xuất ra: **Optimized Routes** (tuyến đường tối ưu với thứ tự giao hàng)

---

## 🚀 Cách Sử Dụng

### 1️⃣ **Chạy Với Cấu Hình Mặc Định**

```bash
python generate_routes.py
```

**Mặc định**:
- Input: `data/orders.csv`
- Rules: `output/district_rules_trained.csv`, `output/road_rules_trained.csv`
- Output: `output/final_routes.csv`
- Max orders/route: 8

### 2️⃣ **Chạy Với Arguments Tùy Chỉnh**

```bash
python generate_routes.py \
    --orders data/my_orders.csv \
    --district-rules output/district_rules.csv \
    --road-rules output/road_rules.csv \
    --output output/my_routes.csv \
    --max-orders 10
```

**Arguments**:
- `--orders`: Path to orders CSV file
- `--district-rules`: Path to district rules CSV file
- `--road-rules`: Path to road rules CSV file
- `--output`: Path to output routes CSV file
- `--max-orders`: Maximum orders per route (default: 8)

---

## 📊 Input Format

### Orders CSV (`data/orders.csv`)

**Required columns**:
```csv
order_id,district,road_name,customer_name,phone,address_detail,...
O0001,Thanh Xuân,Trần Duy Hưng,Đào Công Huy,581431885,"Số 48",...
O0002,Cầu Giấy,Nguyễn Văn Huyên,Nguyễn Hà,876021444,"Số 30",...
```

**Minimum required columns**:
- `district`: Tên quận
- `road_name`: Tên đường

### Rules CSV

**Format** (tự động generate từ `main.py`):
```csv
antecedents,consequents,support,confidence,lift,quality_score
"{'Quận 1'}","{'Quận 3'}",0.123,0.85,2.34,1.99
```

---

## 📈 Output Format

### Final Routes CSV (`output/final_routes.csv`)

```csv
order_id,district,road_name,route_id,sequence,...
O0001,Thanh Xuân,Trần Duy Hưng,R001,1,...
O0083,Thanh Xuân,Cầu vượt Ngã Tư Sở,R001,2,...
O0036,Thanh Xuân,Nguyễn Văn Trỗi,R001,3,...
```

**New columns added**:
- `route_id`: Mã tuyến đường (R001, R002, ...)
- `sequence`: Thứ tự giao hàng trong tuyến (1, 2, 3, ...)

---

## 🔧 Algorithm

### 2-Step Optimization

#### **Step 1: District-Level Optimization**
```python
Initial grouping: Nhóm orders theo quận
↓
District rules: Tối ưu thứ tự các quận
↓
Result: [Quận A → Quận B → Quận C]
```

#### **Step 2: Road-Level Optimization** (Within Each District)
```python
For each district in route:
    Road rules: Tối ưu thứ tự các đường trong quận
    ↓
    Result: [Đường 1 → Đường 2 → Đường 3]
```

### Example Flow

```
Input: 8 orders in 3 districts

Step 1 - District optimization:
├─ Thanh Xuân (5 orders)
├─ Cầu Giấy (2 orders)
└─ Đống Đa (1 order)

District rules suggest: Thanh Xuân → Đống Đa → Cầu Giấy

Step 2 - Road optimization (Thanh Xuân):
├─ Trần Duy Hưng (2 orders)
├─ Nguyễn Văn Trỗi (2 orders)
└─ Phạm Hùng (1 order)

Road rules suggest: Trần Duy Hưng → Phạm Hùng → Nguyễn Văn Trỗi

Final route sequence:
R001: 
  1. Thanh Xuân - Trần Duy Hưng (O001)
  2. Thanh Xuân - Trần Duy Hưng (O083)
  3. Thanh Xuân - Phạm Hùng (O098)
  4. Thanh Xuân - Nguyễn Văn Trỗi (O036)
  5. Thanh Xuân - Nguyễn Văn Trỗi (O112)
  6. Đống Đa - Láng Hạ (O045)
  7. Cầu Giấy - Nguyễn Văn Huyên (O067)
  8. Cầu Giấy - Trần Thái Tông (O089)
```

---

## 📊 Workflow Integration

### Typical Usage Flow

```
Step 1: Train rules (main.py)
├─ python main.py
├─ Output: district_rules_trained.csv
└─ Output: road_rules_trained.csv

Step 2: Generate routes (generate_routes.py)
├─ python generate_routes.py
├─ Input: orders.csv + trained rules
└─ Output: final_routes.csv ✅
```

### Production Deployment

```bash
# 1. Train model (weekly/monthly)
python main.py

# 2. Generate routes (daily)
python generate_routes.py --orders data/today_orders.csv

# 3. Export to system
# Use final_routes.csv for delivery dispatch
```

---

## 🛠️ Customization

### Adjust Max Orders Per Route

```bash
# For larger capacity vehicles
python generate_routes.py --max-orders 15

# For smaller vehicles
python generate_routes.py --max-orders 5
```

### Use Different Rule Sets

```bash
# Use production rules (trained on 100% data)
python generate_routes.py \
    --district-rules output/district_rules.csv \
    --road-rules output/road_rules.csv
```

---

## 📈 Performance

### Typical Runtime

| Orders | Routes | Processing Time |
|--------|--------|-----------------|
| 100    | 12     | ~1-2 seconds    |
| 200    | 25     | ~2-3 seconds    |
| 500    | 60     | ~5-8 seconds    |
| 1000   | 125    | ~10-15 seconds  |

**Hardware**: Standard CPU, no GPU required

---

## 🐛 Troubleshooting

### ❌ Error: "File not found"

**Problem**: Rules files không tồn tại

**Solution**:
```bash
# Train rules trước
python main.py

# Sau đó generate routes
python generate_routes.py
```

### ❌ Error: "No rules loaded"

**Problem**: Rules CSV rỗng hoặc format sai

**Solution**:
1. Kiểm tra file có data không: `wc -l output/district_rules_trained.csv`
2. Kiểm tra format đúng không (xem phần Input Format)
3. Re-train nếu cần: `python main.py`

### ⚠️ Warning: "Bỏ qua rule không hợp lệ"

**Problem**: Một số rules có format lỗi

**Impact**: Minor - script vẫn chạy với các rules hợp lệ

**Solution**: Không cần fix nếu còn đủ rules (>100)

---

## 💡 Tips & Best Practices

### 1. **Use Fresh Rules**

```bash
# Re-train monthly với data mới nhất
python main.py

# Sử dụng rules mới
python generate_routes.py
```

### 2. **Balance Route Size**

```python
# Không quá ít (tốn phí ship)
--max-orders 3  ❌

# Không quá nhiều (không kịp giao)
--max-orders 20  ❌

# Sweet spot: 6-10 orders
--max-orders 8  ✅
```

### 3. **Check Output Quality**

```bash
# Xem routes generated
python -c "
import pandas as pd
df = pd.read_csv('output/final_routes.csv')
print(f'Routes: {df[\"route_id\"].nunique()}')
print(f'Orders: {len(df)}')
print(f'Avg/route: {len(df)/df[\"route_id\"].nunique():.1f}')
"
```

---

## 📚 Related Files

- **main.py**: Train association rules (80/20 split với evaluation)
- **config.py**: Configuration for FP-Growth parameters
- **EVALUATION_REPORT.md**: Model performance metrics
- **README.md**: Project overview

---

## 🎓 Advanced Usage

### Batch Processing

```bash
# Process multiple order files
for file in data/orders_*.csv; do
    python generate_routes.py --orders $file --output "output/routes_$(basename $file)"
done
```

### API Integration

```python
from generate_routes import generate_routes_from_orders

# Call from another Python script
result_df = generate_routes_from_orders(
    orders_file='data/orders.csv',
    district_rules_file='output/district_rules_trained.csv',
    road_rules_file='output/road_rules_trained.csv',
    output_file='output/routes.csv',
    max_orders_per_route=8
)

print(f"Generated {result_df['route_id'].nunique()} routes")
```

---

## 📞 Support

**Issues**: Report bugs via GitHub Issues  
**Questions**: Check README.md or TRAIN_AND_EVALUATE_GUIDE.md

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready
