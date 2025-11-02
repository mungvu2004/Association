"""
Data Handler Module
Chứa mọi logic I/O và chuẩn hóa (load, save, normalize).
"""

import csv
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def normalize_district_name(district):
    """
    Loại bỏ tiền tố 'Quận ', 'Huyện ' để gom nhóm.
    Giải pháp: Normalize tên quận để tăng khả năng tìm patterns.
    
    Args:
        district: Tên quận gốc
    
    Returns:
        Tên quận đã chuẩn hóa
    """
    district = district.strip()
    prefixes = ['Quận ', 'Huyện ', 'Thị xã ', 'Thành phố ']
    for prefix in prefixes:
        if district.startswith(prefix):
            return district[len(prefix):]
    return district


def normalize_road_name(road):
    """
    Loại bỏ tiền tố 'Phố ', 'Đường ', 'Cầu ', v.v. để gom nhóm tên đường.
    Chuẩn hóa tên đường để tăng khả năng tìm patterns.
    
    Args:
        road: Tên đường gốc
    
    Returns:
        Tên đường đã chuẩn hóa
    """
    road = road.strip()
    prefixes = [
        'Phố ',
        'Đường ',
        'Cầu ',
        'Hầm Chui ',
        'Cầu Vượt ',
        'Ngõ ',
        'Đại lộ ',
        'Quốc lộ ',
        'Quốc Lộ ',
        'Tuyến ',
        'Tuyến Số ',
        'Đường Cao Tốc ',
        'Cao Tốc ',
    ]
    for prefix in prefixes:
        if road.startswith(prefix):
            return road[len(prefix):]
    return road


def load_transactions_from_csv(filepath, column_name):
    """
    Đọc file CSV và tạo transactions dựa trên trip_id và column_name.
    Áp dụng normalization cho district names và road names.
    
    Args:
        filepath: Đường dẫn đến file CSV
        column_name: Tên cột cần trích xuất ('district' hoặc 'road_name')
    
    Returns:
        List các transactions (mỗi transaction là một list các items)
    """
    transactions_dict = defaultdict(set)
    
    try:
        # Sử dụng 'utf-8-sig' để tự động loại bỏ BOM nếu có
        with open(filepath, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            # Debug: In ra tên các columns
            if reader.fieldnames:
                logger.info(f"Các cột trong CSV: {reader.fieldnames}")
            
            row_count = 0
            for row in reader:
                trip_id = row.get('trip_id', '').strip()
                item = row.get(column_name, '').strip()
                
                if trip_id and item:
                    # Normalize tên quận hoặc đường
                    if column_name == 'district':
                        item = normalize_district_name(item)
                    elif column_name == 'road_name':
                        item = normalize_road_name(item)
                    
                    transactions_dict[trip_id].add(item)
                    row_count += 1
            
            logger.info(f"Đã đọc {row_count} dòng dữ liệu")
            logger.info(f"Tạo được {len(transactions_dict)} transactions (trip_id unique)")
    except FileNotFoundError:
        logger.error(f"Không tìm thấy file '{filepath}'")
        return []
    except Exception as e:
        logger.error(f"Lỗi khi đọc file: {e}")
        return []
    
    # Chuyển đổi dict thành list of lists
    transactions = [list(items) for items in transactions_dict.values()]
    return transactions


def save_rules_to_csv(rules, filepath, config):
    """
    Lưu các rules vào file CSV với định dạng yêu cầu và thông tin bổ sung.
    
    Args:
        rules: List các rules
        filepath: Đường dẫn file CSV đầu ra
        config: Config để hiển thị thông tin
    """
    try:
        with open(filepath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            # Thêm cột quality_score để đánh giá chất lượng rule
            writer.writerow([
                'antecedents', 
                'consequents', 
                'support', 
                'confidence', 
                'lift', 
                'quality_score'
            ])
            
            for rule in rules:
                # Format sets
                antecedents_str = str(rule['antecedents'])
                consequents_str = str(rule['consequents'])
                quality_score = rule.get('quality_score', rule['confidence'] * rule['lift'])
                
                writer.writerow([
                    antecedents_str,
                    consequents_str,
                    f"{rule['support']:.4f}",
                    f"{rule['confidence']:.4f}",
                    f"{rule['lift']:.4f}",
                    f"{quality_score:.4f}"
                ])
        
        logger.info(f"Đã lưu {len(rules)} rules vào '{filepath}'")
    except Exception as e:
        logger.error(f"Lỗi khi lưu file: {e}")
