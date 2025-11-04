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
    'min_support': 0.02,         # 2% - Cân bằng giữa tốc độ và độ chính xác
    'min_confidence': 0.5,       # 30% - Giảm để có nhiều rules hơn
    'min_lift': 1.2,             # Patterns có ý nghĩa (tăng 20%+)
    'min_quality_score': 0.3,    # confidence × lift >= 0.3
    'max_rules': 5000             # Giới hạn output
}

# Cấu hình cho phân tích Đường (Road)
ROAD_CONFIG = {
    'min_support': 0.01,         # 1% - Giảm để có nhiều patterns
    'min_confidence': 0.7,       # 40% - Giảm để có nhiều rules
    'min_lift': 1.2,             # Patterns có ý nghĩa
    'min_quality_score': 0.4,    # confidence × lift >= 0.4
    'max_rules': 10000            # Giới hạn output
}

# --- LOGGING CONFIGURATION ---
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
