"""
Configuration Module
Chứa tất cả các hằng số, biến cấu hình, và thiết lập đường dẫn.
"""

import os
from pathlib import Path

# --- PATH CONFIGURATION ---
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
ALGORITHMS_DIR = BASE_DIR / 'algorithms'

# File paths
INPUT_FILE = os.getenv(
    'DELIVERY_TRANSACTIONS_FILE', 
    str(ALGORITHMS_DIR / 'data' / 'optimized_routes_standard.csv')
)
OUTPUT_DISTRICT_RULES = os.getenv(
    'OUTPUT_DISTRICT_RULES', 
    str(ALGORITHMS_DIR / 'output/district_rules.csv')
)
OUTPUT_ROAD_RULES = os.getenv(
    'OUTPUT_ROAD_RULES', 
    str(ALGORITHMS_DIR / 'output/road_rules.csv')
)

# --- ALGORITHM CONFIGURATION ---

# Cấu hình cho phân tích Quận (District)
DISTRICT_CONFIG = {
    'min_support': 0.01,         # 1% - Cho phép rare patterns
    'min_confidence': 0.5,       # 50% - Giảm để bắt nhiều patterns
    'min_lift': 1.5,             # Chỉ lấy patterns mạnh (tăng 50%+)
    'min_quality_score': 0.4,    # confidence × lift >= 0.4
    'max_rules': 500             # Giới hạn output
}

# Cấu hình cho phân tích Đường (Road)
ROAD_CONFIG = {
    'min_support': 0.012,        # 1.2% - Giảm nhẹ
    'min_confidence': 0.7,       # 70% - Giảm để có nhiều rules
    'min_lift': 1.3,             # Patterns có ý nghĩa (tăng 30%+)
    'min_quality_score': 0.5,    # confidence × lift >= 0.5
    'max_rules': 1000            # Giới hạn output
}

# --- LOGGING CONFIGURATION ---
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
