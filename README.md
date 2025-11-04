# 🚚 Delivery Route Optimization với FP-Growth

> **Dự án phân tích và tối ưu tuyến đường giao hàng sử dụng thuật toán FP-Growth Association Rules Mining**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()
[![Accuracy](https://img.shields.io/badge/Accuracy-P@5%2022.54%25-green.svg)]()

---

## 📋 Tổng Quan

Hệ thống **học máy** để tối ưu hóa tuyến đường giao hàng bằng cách phân tích patterns từ 100,000+ giao dịch thực tế. Sử dụng thuật toán **FP-Growth** (triển khai từ đầu) để tìm association rules và dự đoán tuyến đường tối ưu.

### 🎯 Bài Toán Giải Quyết

**Input**: 
- 📦 200 đơn hàng mới cần giao
- 📊 100,000 giao dịch lịch sử (9,447 routes)
- 📍 24 quận, hàng nghìn tên đường

**Output**:
- 🛣️ 25 tuyến đường tối ưu
- 🎯 Thứ tự giao hàng thông minh
- 📈 Độ chính xác dự đoán 22.54% (Top-5)

### ✨ Điểm Nổi Bật

- ✅ **Thuật toán FP-Growth từ đầu** - Không dùng thư viện ML
- ✅ **Train/Test Split 80/20** - Đánh giá khách quan
- ✅ **Sequence-Aware Prediction** - Hiểu ngữ cảnh route
- ✅ **Multi-Rule Voting** - Kết hợp nhiều luật
- ✅ **Production Ready** - P@5 = 22.54% (Tốt)

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────┐
│                     INPUT DATA                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  100K Trans  │  │  9447 Routes │  │  200 Orders  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│              CORE ALGORITHM (FP-Growth)                      │
│  ┌────────────────┐         ┌────────────────┐             │
│  │  80% TRAIN     │────────▶│  GENERATE      │             │
│  │  (7557 routes) │         │  RULES         │             │
│  └────────────────┘         │  • 500 quận    │             │
│                              │  • 1000 đường  │             │
│                              └────────┬───────┘             │
└──────────────────────────────────────┼──────────────────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
          ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│  20% TEST       │        │  PREDICTION     │        │  OPTIMIZATION   │
│  Evaluate       │        │  Top-K Voting   │        │  Route Planning │
│  • P@1: 8.68%   │        │  • Confidence   │        │  • 25 routes    │
│  • P@3: 17.27%  │        │  • Lift         │        │  • Ordered      │
│  • P@5: 22.54%  │        │  • Position     │        │  • Optimal      │
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

---

## 📂 Cấu Trúc Dự Án

```
algorithms/
│
├── 📄 Core Modules
│   ├── config.py                    # ⚙️  Cấu hình tham số
│   ├── core_fptree.py               # 🌲 FP-Tree algorithm
│   ├── association_rules.py         # 📊 Rules generation
│   └── data_handler.py              # 💾 Data I/O & normalization
│
├── 🚀 Main Scripts
│   ├── main.py                      # 🎯 Production training (100% data)
│   └── train_and_evaluate.py       # 🧪 Evaluation (80/20 split)
│
├── 📊 Data
│   ├── data/
│   │   ├── optimized_routes_standard.csv   # 100K transactions
│   │   └── orders.csv                       # 200 new orders
│   └── output/
│       ├── district_rules.csv               # Rules quận (production)
│       ├── road_rules.csv                   # Rules đường (production)
│       ├── district_rules_trained.csv       # Rules quận (80% train)
│       ├── road_rules_trained.csv           # Rules đường (80% train)
│       └── final_routes.csv                 # Optimized routes
│
└── 📚 Documentation
    ├── README.md                    # 📖 Tổng quan dự án (file này)
    └── TRAIN_AND_EVALUATE_GUIDE.md # 🎓 Hướng dẫn chi tiết

```

---

## � Core Modules

### 1️⃣ `config.py` - Configuration Management

Quản lý tất cả tham số thuật toán và đường dẫn file.

```python
DISTRICT_CONFIG = {
    'min_support': 0.02,      # 2% - Patterns frequency
    'min_confidence': 0.3,    # 30% - Rule confidence
    'min_lift': 1.2,          # 1.2x - Significance
    'max_rules': 500          # Top 500 rules
}
```

**Tham số quan trọng**:
- `min_support`: Tần suất xuất hiện pattern (↓ = nhiều rules, chậm)
- `min_confidence`: Độ tin cậy rule (↓ = nhiều rules yếu)
- `min_lift`: Mức độ quan trọng (↓ = rules ít ý nghĩa)

### 2️⃣ `core_fptree.py` - FP-Growth Algorithm

Triển khai thuật toán FP-Growth từ đầu (no external ML libs).

**Classes**:
- `FPNode`: Node trong FP-Tree
- `FPTree`: Cấu trúc dữ liệu FP-Tree

**Functions**:
- `mine_fp_tree()`: Khai phá frequent itemsets
- Recursive mining với conditional FP-trees

**Performance**: Xử lý 5,396 transactions trong <30 giây

### 3️⃣ `association_rules.py` - Rules Generation

Tạo và lọc association rules từ frequent patterns.

**Metrics**:
```python
Confidence = Support(A ∪ B) / Support(A)
Lift = Support(A ∪ B) / (Support(A) × Support(B))
Quality Score = Confidence × Lift
```

**Filtering**:
- ✅ Min confidence threshold
- ✅ Min lift threshold  
- ✅ Quality score ranking
- ✅ Max rules limit

### 4️⃣ `data_handler.py` - Data Processing

Xử lý I/O và chuẩn hóa dữ liệu.

**Functions**:
- `normalize_district_name()`: "Quận 1" → "1"
- `normalize_road_name()`: "Đường ABC" → "ABC"
- `load_transactions_from_csv()`: CSV → Transactions
- `save_rules_to_csv()`: Rules → CSV

**Normalization Rules**:
- Loại bỏ tiền tố: Quận, Huyện, Đường, Phố, etc.
- Chuẩn hóa case và spacing
- Loại bỏ diacritics (tùy chọn)

---

## 🚀 Main Scripts

### 🎯 `main.py` - Production Training

**Mục đích**: Train model trên **100% dữ liệu** để production.

```bash
python main.py
```

**Output**:
- `output/district_rules.csv` - 233 luật quận
- `output/road_rules.csv` - 401 luật đường

**Use Case**:
- ✅ Deploy model cuối cùng
- ✅ Tạo rules tốt nhất với toàn bộ data
- ❌ Không đánh giá accuracy (no test set)

### 🧪 `train_and_evaluate.py` - Evaluation Pipeline

**Mục đích**: Train + Test với **80/20 split** để đánh giá.

```bash
python train_and_evaluate.py
```

**Workflow**:
1. **Split**: 80% train (7,557 routes) / 20% test (1,890 routes)
2. **Train**: Học rules từ 80%
3. **Test**: Đánh giá trên 20% độc lập
4. **Generate**: Tối ưu routes cho 200 orders

**Output**:
- `district_rules_trained.csv` - 500 rules từ train set
- `road_rules_trained.csv` - 1000 rules từ train set  
- `final_routes.csv` - 25 optimized routes
- **Metrics**: P@1, P@3, P@5

**Use Case**:
- ✅ Đánh giá accuracy thực tế
- ✅ Thử nghiệm config mới
- ✅ Validation trước deploy

---

## 📊 Hiệu Suất & Kết Quả

### 🎯 Độ Chính Xác (Precision@K)

| Metric | District | Road | Average | Rating |
|--------|----------|------|---------|--------|
| **P@1** | 12.27% | 5.09% | **8.68%** | ⭐⭐ |
| **P@3** | 24.45% | 10.09% | **17.27%** | ⭐⭐⭐ |
| **P@5** | 31.63% | 13.45% | **22.54%** | ⭐⭐⭐⭐ |

**Đánh giá**: ✅ **TỐT** (P@5: 20-30%)

### 📈 Lịch Sử Cải Tiến

| Version | Algorithm | P@5 | Improvement |
|---------|-----------|-----|-------------|
| v1.0 | Set-based | 7.68% | Baseline |
| v2.0 | Sequence-aware | 11.38% | +48% |
| v3.0 | Position bonus | **22.54%** | **+193%** 🚀 |

### ⚡ Performance

| Task | Time | Throughput |
|------|------|------------|
| Load 100K trans | <2s | 50K trans/s |
| Train District | ~10s | 303 trans/s |
| Train Road | ~20s | 270 trans/s |
| Test 1251 routes | ~15s | 83 routes/s |
| Generate 25 routes | <1s | Instant |

**Hardware**: Standard CPU (no GPU needed)

---

## 🛠️ Installation & Usage

### Prerequisites

```bash
python >= 3.8
pandas >= 1.3.0
scikit-learn >= 0.24.0  # Only for train_test_split
```

### Installation

```bash
# Clone repository
git clone https://github.com/mungvu2004/Association.git
cd Association/algorithms

# Install dependencies
pip install pandas scikit-learn

# Verify data
ls data/  # Should see optimized_routes_standard.csv & orders.csv
```

### Quick Start

#### Option 1: Production Training (100% data)
```bash
python main.py
```
**Output**: `district_rules.csv`, `road_rules.csv` (best quality)

#### Option 2: Evaluation Pipeline (80/20 split)
```bash
python train_and_evaluate.py
```
**Output**: Rules + Metrics + Optimized Routes

### Configuration

Edit `config.py` để tùy chỉnh:

```python
# Faster training (less rules)
DISTRICT_CONFIG['min_support'] = 0.05  # 5% instead of 2%

# More rules (slower)
DISTRICT_CONFIG['min_support'] = 0.01  # 1% instead of 2%
ROAD_CONFIG['min_confidence'] = 0.3    # 30% instead of 40%
```

---

## 💡 Key Concepts

### 🌲 FP-Growth Algorithm

**Ưu điểm** so với Apriori:
- ✅ Chỉ scan database 2 lần (vs nhiều lần)
- ✅ Không generate candidate sets
- ✅ Nhanh hơn 10-100x với large datasets

**Cách hoạt động**:
1. **First scan**: Đếm frequency → frequent items
2. **Second scan**: Build FP-tree (compressed structure)
3. **Recursive mining**: Extract patterns từ conditional FP-trees

### 📊 Association Rules

**Format**: `A → B` (If A then B)

**Example**:
```
{Quận 1, Quận 3} → {Quận 10}
Confidence: 85%  # Khi đi Q1, Q3 thì 85% đi Q10
Lift: 2.3       # Tăng 130% khả năng đi Q10
Support: 5%     # Xuất hiện trong 5% routes
```

### 🎯 Sequence-Aware Prediction

**Vấn đề**: Rules thông thường không quan tâm thứ tự
```python
Rule: {A, B, C} → D
Route: [X, Y, A, B, C]  # Match!
Route: [A, B, C, X, Y]  # Match! (Nhưng context khác)
```

**Giải pháp**: Position Bonus
```python
# Ưu tiên rules khớp với 3 items cuối
recent_items = current_path[-3:]
overlap = len(antecedents & recent_items)
position_bonus = 1.0 + (overlap / len(antecedents))
score = confidence × quality_score × position_bonus
```

**Kết quả**: P@5 tăng từ 11.38% → 22.54% (+98%)

### 🔄 Multi-Rule Voting

Thay vì dùng 1 rule tốt nhất, kết hợp nhiều rules:

```python
candidates = {}
for rule in matching_rules:
    for location in rule.consequents:
        score = rule.confidence × rule.quality_score × position_bonus
        candidates[location] += score  # Accumulate votes

return top_k(candidates)
```

**Lợi ích**:
- ✅ Robust hơn với noise
- ✅ Tận dụng nhiều patterns
- ✅ Top-5 predictions chính xác hơn

---

## 📈 Optimization Tips

### 🚀 Tăng Tốc Training

**Vấn đề**: Training lâu hơn 5 phút

**Nguyên nhân**: `min_support` quá thấp → quá nhiều patterns

**Giải pháp**:
```python
# config.py
DISTRICT_CONFIG['min_support'] = 0.05  # 5% thay vì 2%
ROAD_CONFIG['min_support'] = 0.02      # 2% thay vì 1%
```

**Trade-off**: Ít rules hơn nhưng nhanh hơn 5-10x

### 🎯 Tăng Độ Chính Xác

**Vấn đề**: P@5 < 15%

**Giải pháp**:

1. **Giảm min_support** → Nhiều patterns rare
```python
DISTRICT_CONFIG['min_support'] = 0.015  # 1.5%
```

2. **Giảm min_confidence** → Nhiều rules
```python
DISTRICT_CONFIG['min_confidence'] = 0.25  # 25%
```

3. **Kiểm tra data quality**
```python
# Xem distribution
df['district'].value_counts()
df.groupby('trip_id').size().describe()
```

### ⚖️ Balance Speed vs Accuracy

| Config | Train Time | Rules | P@5 | Recommendation |
|--------|------------|-------|-----|----------------|
| Fast | ~5s | 100 | 10-15% | Development |
| Balanced | ~15s | 500 | 20-25% | ✅ **Production** |
| Accurate | ~60s | 2000 | 25-30% | Research |

**Balanced config** (recommended):
```python
DISTRICT_CONFIG = {
    'min_support': 0.02,
    'min_confidence': 0.3,
    'min_lift': 1.2,
    'max_rules': 500
}
```

---

## 🐛 Troubleshooting

### ❌ Script Chạy Quá Chậm

**Triệu chứng**: Treo ở "Đang mine FP-tree..." >5 phút

**Fix**:
```python
# Tăng min_support
DISTRICT_CONFIG['min_support'] = 0.05  # Double it
```

### ❌ Không Sinh Được Rules

**Triệu chứng**: "Rules: 0" hoặc "Rules: <10"

**Fix**:
```python
# Giảm tất cả thresholds
config['min_support'] = 0.01
config['min_confidence'] = 0.2
config['min_lift'] = 1.1
```

### ❌ KeyError hoặc TypeError

**Triệu chứng**: Lỗi khi đọc CSV

**Fix**:
1. Kiểm tra CSV có đúng columns: `trip_id`, `district`, `road_name`
2. Kiểm tra encoding: UTF-8 với BOM
3. Kiểm tra missing values:
```python
df.isnull().sum()
```

### ❌ P@5 Quá Thấp (<5%)

**Nguyên nhân**:
1. Config quá strict (support/confidence cao)
2. Data không đủ patterns
3. Test set khác biệt quá nhiều với train

**Fix**:
```python
# 1. Relax config
config['min_support'] = 0.01
config['min_confidence'] = 0.25

# 2. Check data distribution
train_districts = train_df['district'].unique()
test_districts = test_df['district'].unique()
overlap = set(train_districts) & set(test_districts)
print(f"Overlap: {len(overlap)}/{len(test_districts)}")
```

---

## 📚 Advanced Topics

### 🔬 Understanding Metrics

**Precision@K**: Trong top-K predictions, có bao nhiêu đúng?
```
P@5 = 22.54% nghĩa là:
- Trong 10,000 dự đoán
- 2,254 lần actual location nằm trong top-5
```

**Confidence**: Độ tin cậy rule
```
Confidence(A → B) = 85% nghĩa là:
- Trong tất cả routes có A
- 85% cũng có B
```

**Lift**: Mức độ quan trọng
```
Lift = 2.3 nghĩa là:
- Khi có A, khả năng có B tăng 130% (2.3x)
- Lift > 1: Positive correlation
- Lift = 1: Independent
- Lift < 1: Negative correlation
```

### 🧪 Experiment with Parameters

**Scenario 1**: Cần rules chất lượng cao, ít nhưng chính xác
```python
config = {
    'min_support': 0.05,
    'min_confidence': 0.6,
    'min_lift': 1.5,
    'max_rules': 200
}
```

**Scenario 2**: Cần coverage rộng, nhiều rules
```python
config = {
    'min_support': 0.01,
    'min_confidence': 0.25,
    'min_lift': 1.1,
    'max_rules': 1500
}
```

**Scenario 3**: Balanced (recommended)
```python
config = {
    'min_support': 0.02,
    'min_confidence': 0.3,
    'min_lift': 1.2,
    'max_rules': 500
}
```

### 📊 Custom Evaluation

Thêm metrics riêng vào `train_and_evaluate.py`:

```python
# Mean Reciprocal Rank (MRR)
def calculate_mrr(test_routes, rules):
    reciprocal_ranks = []
    for route in test_routes:
        for i in range(len(route)-1):
            predictions = predict_next_locations(route[:i+1], rules)
            actual = route[i+1]
            try:
                rank = predictions.index(actual) + 1
                reciprocal_ranks.append(1.0 / rank)
            except ValueError:
                reciprocal_ranks.append(0.0)
    return sum(reciprocal_ranks) / len(reciprocal_ranks)
```

---

## 🤝 Contributing

### Development Setup

```bash
# Clone repo
git clone https://github.com/mungvu2004/Association.git
cd Association/algorithms

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install pandas scikit-learn
```

### Code Style

```python
# Follow PEP 8
# Use type hints
def predict_next_locations(
    current_path: list,
    rules: list,
    top_k: int = 5
) -> list:
    """Docstring with clear explanation"""
    ...
```

### Adding New Features

1. **New evaluation metric**: Edit `train_and_evaluate.py` → `calculate_precision_at_k()`
2. **New data source**: Edit `data_handler.py` → add new loader
3. **New algorithm**: Create new module, follow same interface

---

## 📖 Documentation

- 📘 **README.md** (this file): Project overview
- 📗 **TRAIN_AND_EVALUATE_GUIDE.md**: Detailed guide for evaluation script
- 📙 **Code comments**: Inline documentation in all modules

---

## 🎓 Learning Resources

### FP-Growth Algorithm
- [Original Paper](https://www.cs.sfu.ca/~jpei/publications/sigmod00.pdf) - Han et al. (2000)
- [Tutorial](https://www.geeksforgeeks.org/fp-growth-algorithm/) - GeeksforGeeks

### Association Rules
- [Market Basket Analysis](https://towardsdatascience.com/market-basket-analysis)
- [Metrics Explained](https://michael.hahsler.net/research/association_rules/)

### Route Optimization
- [Vehicle Routing Problem](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [ML for Logistics](https://arxiv.org/abs/2006.04095)

---

## 📊 Project Statistics

- **Lines of Code**: ~1,500
- **Modules**: 5 core + 2 scripts
- **Data Processed**: 100,000+ transactions
- **Routes Analyzed**: 9,447 routes
- **Rules Generated**: 1,500+ total
- **Accuracy**: P@5 = 22.54% (Tốt)
- **Performance**: <60s total runtime

---

## 🏆 Achievements

- ✅ **From Scratch**: FP-Growth triển khai hoàn toàn không dùng ML libs
- ✅ **Production Ready**: P@5 22.54% (mục tiêu 20%+)
- ✅ **Optimized**: 193% improvement qua 3 iterations
- ✅ **Scalable**: Xử lý 100K+ transactions mượt mà
- ✅ **Well Documented**: Comprehensive docs + comments

---

## 📞 Contact & Support

- **GitHub**: [mungvu2004/Association](https://github.com/mungvu2004/Association)
- **Issues**: Report bugs hoặc feature requests via GitHub Issues

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **FP-Growth Algorithm**: Jiawei Han, Jian Pei, Yiwen Yin (2000)
- **Python Community**: pandas, scikit-learn contributors
- **Contributors**: All who helped optimize and improve this project

---

**Last Updated**: December 2024  
**Version**: 3.0  
**Status**: ✅ Production Ready  
**Maintainer**: mungvu2004

---

<div align="center">
  
### ⭐ Star this repo if you find it useful!

Made with ❤️ and lots of ☕

</div>