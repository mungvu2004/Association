"""
Main Module
File thực thi chính, điều phối luồng làm việc.
"""

import logging
from collections import defaultdict

from config import (
    INPUT_FILE,
    OUTPUT_DISTRICT_RULES,
    OUTPUT_ROAD_RULES,
    DISTRICT_CONFIG,
    ROAD_CONFIG,
    LOG_LEVEL,
    LOG_FORMAT
)
from data_handler import load_transactions_from_csv, save_rules_to_csv
from core_fptree import mine_fp_tree
from association_rules import generate_association_rules


# Thiết lập logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


def run_analysis(transactions, config, analysis_name):
    """
    Chạy phân tích FP-Growth và tạo association rules.
    
    Args:
        transactions: List các transactions
        config: Dictionary chứa min_support, min_confidence và các tham số khác
        analysis_name: Tên loại phân tích (để hiển thị trong log)
    
    Returns:
        List các association rules
    """
    if not transactions:
        logger.warning(f"Không có transactions cho phân tích {analysis_name}")
        return []
    
    logger.info("=" * 60)
    logger.info(f"Bắt đầu phân tích {analysis_name}")
    logger.info("=" * 60)
    logger.info(f"Tổng số transactions: {len(transactions)}")
    
    # Thống kê độ dài transactions
    transaction_lengths = [len(t) for t in transactions]
    logger.info("\nThống kê độ dài transactions:")
    logger.info(f"  - Min: {min(transaction_lengths)}")
    logger.info(f"  - Max: {max(transaction_lengths)}")
    logger.info(f"  - Trung bình: {sum(transaction_lengths)/len(transaction_lengths):.2f}")
    logger.info(f"  - Số transactions có >= 2 items: {sum(1 for l in transaction_lengths if l >= 2)}")
    
    # Hiển thị vài transactions mẫu
    logger.info("\nVí dụ 5 transactions đầu:")
    for i, trans in enumerate(transactions[:5], 1):
        logger.info(f"  {i}. {trans} (độ dài: {len(trans)})")
    
    # Đếm tần suất các items
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1
    
    logger.info("\nTop 10 items phổ biến nhất:")
    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    for item, count in sorted_items[:10]:
        logger.info(f"  - '{item}': {count} lần ({count/len(transactions)*100:.1f}%)")
    
    logger.info(f"\nMin support: {config['min_support']}")
    logger.info(f"Min confidence: {config['min_confidence']}")
    
    # Đảm bảo min_support_count tối thiểu là 1
    min_support_count = max(1, int(config['min_support'] * len(transactions)))
    
    logger.info(f"Min support count: {min_support_count}")
    logger.info(f"Min lift: {config.get('min_lift', 1.0)}")
    logger.info(f"Min quality score: {config.get('min_quality_score', 0.0)}")
    logger.info("\nĐang khai phá frequent itemsets...")
    
    # Khai phá frequent itemsets
    frequent_itemsets = mine_fp_tree(transactions, min_support_count)
    
    logger.info(f"✓ Tìm thấy {len(frequent_itemsets)} frequent itemsets")
    
    # Hiển thị các frequent itemsets
    if frequent_itemsets:
        logger.info("\nCác frequent itemsets theo kích thước:")
        by_size = defaultdict(list)
        for itemset, count in frequent_itemsets.items():
            by_size[len(itemset)].append((itemset, count))
        
        for size in sorted(by_size.keys()):
            logger.info(f"  - Kích thước {size}: {len(by_size[size])} itemsets")
            if size <= 3:  # Chỉ hiển thị chi tiết cho itemsets nhỏ
                for itemset, count in sorted(by_size[size], key=lambda x: x[1], reverse=True)[:5]:
                    logger.info(f"    • {set(itemset)}: {count} lần")
    
    logger.info("\nĐang tạo association rules với lọc thông minh...")
    
    # Tạo association rules với config đầy đủ
    rules = generate_association_rules(
        frequent_itemsets, 
        len(transactions), 
        config
    )
    
    logger.info(f"✓ Tạo được {len(rules)} association rules (sau khi lọc)")
    
    # Hiển thị thống kê chất lượng
    if rules:
        lifts = [r['lift'] for r in rules]
        confidences = [r['confidence'] for r in rules]
        quality_scores = [r.get('quality_score', 0) for r in rules]
        
        logger.info("\n📊 Thống kê chất lượng rules:")
        logger.info(f"  - Lift: Min={min(lifts):.2f}, Max={max(lifts):.2f}, Avg={sum(lifts)/len(lifts):.2f}")
        logger.info(f"  - Confidence: Min={min(confidences):.2f}, Max={max(confidences):.2f}, Avg={sum(confidences)/len(confidences):.2f}")
        logger.info(f"  - Quality Score: Min={min(quality_scores):.2f}, Max={max(quality_scores):.2f}, Avg={sum(quality_scores)/len(quality_scores):.2f}")
    
    return rules


def main():
    """Hàm chính thực thi luồng phân tích."""
    logger.info("=" * 60)
    logger.info("FP-GROWTH ASSOCIATION RULES MINING")
    logger.info("Triển khai từ đầu (from scratch) với Lọc Thông Minh")
    logger.info("=" * 60)
    logger.info(f"\n📁 File đầu vào: {INPUT_FILE}")
    logger.info("\n🔧 CẢI TIẾN MỚI:")
    logger.info("   ✅ Lọc theo Lift (patterns có ý nghĩa)")
    logger.info("   ✅ Quality Score = Confidence × Lift")
    logger.info("   ✅ Giới hạn số lượng rules tối ưu")
    logger.info("   ✅ Normalize tên quận và đường")
    
    # PHÂN TÍCH QUẬN (DISTRICT)
    logger.info("\n" + "=" * 60)
    logger.info("1. PHÂN TÍCH QUẬN (DISTRICT)")
    logger.info("=" * 60)
    logger.info(f"⚙️  Config: support={DISTRICT_CONFIG['min_support']}, "
                f"confidence={DISTRICT_CONFIG['min_confidence']}, "
                f"lift>={DISTRICT_CONFIG['min_lift']}")
    
    district_transactions = load_transactions_from_csv(INPUT_FILE, 'district')
    district_rules = run_analysis(district_transactions, DISTRICT_CONFIG, "Quận")
    
    if district_rules:
        save_rules_to_csv(district_rules, OUTPUT_DISTRICT_RULES, DISTRICT_CONFIG)
        
        # Hiển thị một vài rules mẫu
        logger.info("\n🏆 Top 10 rules (theo Quality Score):")
        for i, rule in enumerate(district_rules[:10], 1):
            quality = rule.get('quality_score', 0)
            logger.info(f"\n{i}. {rule['antecedents']} => {rule['consequents']}")
            logger.info(f"   📊 Support: {rule['support']:.4f}, "
                       f"Confidence: {rule['confidence']:.4f}, "
                       f"Lift: {rule['lift']:.4f}, "
                       f"Quality: {quality:.4f}")
    
    # PHÂN TÍCH ĐƯỜNG (ROAD)
    logger.info("\n" + "=" * 60)
    logger.info("2. PHÂN TÍCH ĐƯỜNG (ROAD)")
    logger.info("=" * 60)
    logger.info(f"⚙️  Config: support={ROAD_CONFIG['min_support']}, "
                f"confidence={ROAD_CONFIG['min_confidence']}, "
                f"lift>={ROAD_CONFIG['min_lift']}")
    
    road_transactions = load_transactions_from_csv(INPUT_FILE, 'road_name')
    road_rules = run_analysis(road_transactions, ROAD_CONFIG, "Đường")
    
    if road_rules:
        save_rules_to_csv(road_rules, OUTPUT_ROAD_RULES, ROAD_CONFIG)
        
        # Hiển thị một vài rules mẫu
        logger.info("\n🏆 Top 10 rules (theo Quality Score):")
        for i, rule in enumerate(road_rules[:10], 1):
            quality = rule.get('quality_score', 0)
            logger.info(f"\n{i}. {rule['antecedents']} => {rule['consequents']}")
            logger.info(f"   📊 Support: {rule['support']:.4f}, "
                       f"Confidence: {rule['confidence']:.4f}, "
                       f"Lift: {rule['lift']:.4f}, "
                       f"Quality: {quality:.4f}")
    
    # KẾT QUẢ TỔNG KẾT
    logger.info("\n" + "=" * 60)
    logger.info("✅ KẾT QUẢ TỔNG KẾT")
    logger.info("=" * 60)
    logger.info(f"📈 Phân tích Quận: {len(district_rules)} rules "
                f"(max: {DISTRICT_CONFIG['max_rules']}) -> {OUTPUT_DISTRICT_RULES}")
    logger.info(f"📈 Phân tích Đường: {len(road_rules)} rules "
                f"(max: {ROAD_CONFIG['max_rules']}) -> {OUTPUT_ROAD_RULES}")
    logger.info("\n💡 Lưu ý: Tất cả rules có Lift >= min_lift và Quality Score cao")
    logger.info("💡 Quality Score = Confidence × Lift (đánh giá tổng hợp)")
    logger.info("\n🎉 Hoàn thành!")


if __name__ == "__main__":
    main()
