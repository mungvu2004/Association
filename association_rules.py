from itertools import combinations


def filter_rules_by_quality(rules, config):
    """
    Lọc rules theo nhiều tiêu chí chất lượng.
    
    Args:
        rules: List các rules chưa lọc
        config: Dictionary chứa các ngưỡng lọc
            - min_lift: Ngưỡng lift tối thiểu
            - min_quality_score: Ngưỡng quality score tối thiểu
            - max_rules: Số lượng rules tối đa
    
    Returns:
        List các rules đã lọc và sắp xếp theo chất lượng
    """
    filtered_rules = []
    
    min_lift = config.get('min_lift', 1.0)
    min_quality_score = config.get('min_quality_score', 0.0)
    
    for rule in rules:
        if rule['lift'] < min_lift:
            continue
        quality_score = rule['confidence'] * rule['lift']
        if quality_score < min_quality_score:
            continue
        
        total_items = len(rule['antecedents']) + len(rule['consequents'])
        complexity = total_items
        
        filtered_rules.append({
            **rule,
            'quality_score': quality_score,
            'complexity': complexity
        })
    
    # Sắp xếp theo quality_score giảm dần, sau đó theo lift
    filtered_rules.sort(
        key=lambda x: (x['quality_score'], x['lift']), 
        reverse=True
    )
    
    # Giới hạn số lượng rules
    max_rules = config.get('max_rules', len(filtered_rules))
    return filtered_rules[:max_rules]


def generate_association_rules(frequent_itemsets, total_transactions, config):
    """
    Tạo các luật kết hợp từ frequent itemsets với lọc thông minh.
    
    Args:
        frequent_itemsets: Dictionary của frequent itemsets và support counts
        total_transactions: Tổng số transactions
        config: Dictionary chứa cấu hình
            - min_confidence: Ngưỡng confidence tối thiểu
            - min_lift: Ngưỡng lift tối thiểu
            - min_quality_score: Ngưỡng quality score tối thiểu
            - max_rules: Số lượng rules tối đa
    
    Returns:
        List các rules đã lọc và sắp xếp theo chất lượng
        Mỗi rule là một dictionary với keys:
            - antecedents: Set các items điều kiện
            - consequents: Set các items kết quả
            - support: Support của rule
            - confidence: Confidence của rule
            - lift: Lift của rule
            - quality_score: Quality score của rule
    """
    rules = []
    
    min_confidence = config['min_confidence']
    min_lift = config.get('min_lift', 1.0)
    
    # Tính support cho mỗi itemset
    itemset_support = {
        itemset: count / total_transactions 
        for itemset, count in frequent_itemsets.items()
    }
    
    # Tạo rules từ các itemsets có ít nhất 2 items
    for itemset in frequent_itemsets:
        if len(itemset) < 2:
            continue
        
        items = list(itemset)
        
        # Tạo tất cả các cách chia itemset thành antecedent và consequent
        for i in range(1, len(items)):
            for antecedent_items in combinations(items, i):
                antecedent = frozenset(antecedent_items)
                consequent = itemset - antecedent
                
                if not consequent:
                    continue
                
                # Tính các metrics
                support = itemset_support[itemset]
                
                # Antecedent phải có trong frequent_itemsets
                if antecedent not in itemset_support:
                    continue
                    
                antecedent_support = itemset_support[antecedent]
                
                if antecedent_support == 0:
                    continue
                
                confidence = support / antecedent_support
                
                # Confidence phải <= 1.0
                if confidence > 1.0:
                    continue
                
                if confidence < min_confidence:
                    continue
                
                # Consequent phải có trong frequent_itemsets
                if consequent not in itemset_support:
                    continue
                    
                consequent_support = itemset_support[consequent]
                
                if consequent_support == 0:
                    lift = 0
                else:
                    lift = confidence / consequent_support
                
                # Lọc theo lift ngay từ đầu
                if lift < min_lift:
                    continue
                
                rules.append({
                    'antecedents': set(antecedent),
                    'consequents': set(consequent),
                    'support': support,
                    'confidence': confidence,
                    'lift': lift
                })
    
    # Áp dụng lọc thông minh theo quality score
    filtered_rules = filter_rules_by_quality(rules, config)
    
    return filtered_rules
