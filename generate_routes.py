"""
Generate Routes from Orders using Association Rules
Tạo tuyến đường từ orders dựa trên association rules đã train
"""

import pandas as pd
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Cấu hình
ORDERS_FILE = 'data/orders.csv'
DISTRICT_RULES_FILE = 'output/district_rules_trained.csv'
ROAD_RULES_FILE = 'output/road_rules_trained.csv'
OUTPUT_ROUTES = 'output/final_routes.csv'
MAX_ORDERS_PER_ROUTE = 8


def load_rules_from_csv(filepath):
    """Load rules từ CSV file"""
    import ast
    
    df = pd.read_csv(filepath)
    rules = []
    
    for _, row in df.iterrows():
        try:
            rules.append({
                'antecedents': ast.literal_eval(row['antecedents']) if isinstance(row['antecedents'], str) else set([row['antecedents']]),
                'consequents': ast.literal_eval(row['consequents']) if isinstance(row['consequents'], str) else set([row['consequents']]),
                'confidence': float(row['confidence']),
                'lift': float(row['lift']),
                'quality_score': float(row.get('quality_score', row['confidence'] * row['lift']))
            })
        except Exception as e:
            logger.warning(f"Bỏ qua rule không hợp lệ: {e}")
            continue
    
    return rules


def predict_next_locations(current_path, rules, top_k=5):
    """Dự đoán vị trí tiếp theo - ưu tiên rules khớp SEQUENCE"""
    if not current_path:
        return []
    
    candidates = {}
    current_set = set(current_path)
    
    for rule in rules:
        ant = rule['antecedents'] if isinstance(rule['antecedents'], set) else set(rule['antecedents'])
        cons = rule['consequents'] if isinstance(rule['consequents'], set) else set(rule['consequents'])
        
        # Kiểm tra rule có match không
        if not ant.issubset(current_set):
            continue
        
        # Tính score dựa trên độ gần với tail của current_path
        base_score = rule['confidence'] * rule.get('quality_score', rule['lift'])
        
        # Bonus nếu antecedents xuất hiện gần cuối path
        recent_items = set(current_path[-min(3, len(current_path)):])
        overlap = len(ant & recent_items) / len(ant) if ant else 0
        position_bonus = 1.0 + overlap  # Bonus 0-100%
        
        for location in cons:
            if location not in current_set:
                score = base_score * position_bonus
                candidates[location] = candidates.get(location, 0) + score
    
    return [loc for loc, _ in sorted(candidates.items(), key=lambda x: x[1], reverse=True)[:top_k]]


def optimize_route_order(districts, rules):
    """Tối ưu thứ tự các quận theo rules"""
    if not districts or not rules:
        return districts
    
    optimized = [districts[0]]
    remaining = set(districts[1:])
    
    while remaining:
        # Dự đoán quận tiếp theo dựa trên path hiện tại
        predictions = predict_next_locations(optimized, rules, top_k=3)
        best_next = next((p for p in predictions if p in remaining), None)
        
        if best_next:
            optimized.append(best_next)
            remaining.discard(best_next)
        else:
            # Nếu không có prediction, lấy ngẫu nhiên
            next_district = remaining.pop()
            optimized.append(next_district)
    
    return optimized


def create_initial_routes(orders_df, max_orders_per_route=MAX_ORDERS_PER_ROUTE):
    """Tạo routes sơ bộ theo quận"""
    district_groups = defaultdict(list)
    
    for idx, row in orders_df.iterrows():
        district_groups[row['district']].append(idx)
    
    routes = []
    current_route = []
    
    for order_indices in district_groups.values():
        for idx in order_indices:
            current_route.append(idx)
            if len(current_route) >= max_orders_per_route:
                routes.append(current_route)
                current_route = []
    
    if current_route:
        routes.append(current_route)
    
    return routes, len(district_groups)


def optimize_single_route(route_indices, orders_df, district_rules, road_rules):
    """Tối ưu thứ tự 1 route dựa trên rules quận và đường"""
    route_orders = orders_df.loc[route_indices]
    
    # Bước 1: Tối ưu thứ tự các QUẬN
    districts = route_orders['district'].tolist()
    optimized_districts = optimize_route_order(districts, district_rules)
    
    # Bước 2: Với mỗi quận, tối ưu thứ tự các ĐƯỜNG
    ordered_indices = []
    for district in optimized_districts:
        district_orders = route_orders[route_orders['district'] == district]
        
        if len(district_orders) > 1:
            # Có nhiều orders trong cùng quận → tối ưu thứ tự đường
            roads = district_orders['road_name'].tolist()
            optimized_roads = optimize_route_order(roads, road_rules)
            
            # Sắp xếp orders theo thứ tự đường đã tối ưu
            for road in optimized_roads:
                matching_orders = district_orders[district_orders['road_name'] == road].index.tolist()
                ordered_indices.extend(matching_orders)
        else:
            # Chỉ có 1 order trong quận
            ordered_indices.extend(district_orders.index.tolist())
    
    # Thêm các orders còn thiếu (nếu có)
    missing_indices = set(route_indices) - set(ordered_indices)
    ordered_indices.extend(missing_indices)
    
    return ordered_indices


def generate_routes_from_orders(orders_file, district_rules_file, road_rules_file, output_file=OUTPUT_ROUTES, max_orders_per_route=MAX_ORDERS_PER_ROUTE):
    """
    Sinh tuyến đường từ orders sử dụng association rules (quận + đường)
    
    Args:
        orders_file: Path to orders CSV file
        district_rules_file: Path to district rules CSV file
        road_rules_file: Path to road rules CSV file
        output_file: Path to output routes CSV file
        max_orders_per_route: Maximum orders per route
    
    Returns:
        DataFrame containing optimized routes
    """
    logger.info("\n" + "="*70)
    logger.info("🚚 SINH TUYẾN ĐƯỜNG TỪ ORDERS")
    logger.info("="*70)
    
    # Load data
    logger.info(f"\n📥 Loading data...")
    orders_df = pd.read_csv(orders_file)
    district_rules = load_rules_from_csv(district_rules_file)
    road_rules = load_rules_from_csv(road_rules_file)
    
    logger.info(f"   ✓ Orders: {len(orders_df)}")
    logger.info(f"   ✓ District rules: {len(district_rules)}")
    logger.info(f"   ✓ Road rules: {len(road_rules)}")
    
    # Tạo routes sơ bộ
    logger.info(f"\n🔨 Creating initial routes...")
    routes, num_districts = create_initial_routes(orders_df, max_orders_per_route)
    logger.info(f"   ✓ Districts: {num_districts}")
    logger.info(f"   ✓ Initial routes: {len(routes)}")
    
    # Tối ưu routes
    logger.info(f"\n⚡ Optimizing routes using association rules...")
    logger.info(f"   • Step 1: Optimize district order")
    logger.info(f"   • Step 2: Optimize road order within each district")
    optimized_orders = []
    
    for route_id, route_indices in enumerate(routes, 1):
        if route_id % 5 == 0:
            logger.info(f"   Processing route {route_id}/{len(routes)}...")
        
        optimized_indices = optimize_single_route(route_indices, orders_df, district_rules, road_rules)
        
        for seq, idx in enumerate(optimized_indices, 1):
            order_data = orders_df.loc[idx].to_dict()
            order_data.update({
                'route_id': f"R{route_id:03d}",
                'sequence': seq
            })
            optimized_orders.append(order_data)
    
    # Tạo DataFrame và lưu
    result_df = pd.DataFrame(optimized_orders)
    result_df.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"\n✅ Hoàn thành!")
    logger.info(f"   ✓ Total routes: {result_df['route_id'].nunique()}")
    logger.info(f"   ✓ Total orders: {len(result_df)}")
    logger.info(f"   ✓ Avg orders/route: {len(result_df) / result_df['route_id'].nunique():.1f}")
    logger.info(f"   ✓ Output saved: {output_file}")
    logger.info("="*70 + "\n")
    
    return result_df


def main():
    """Main function - chạy standalone"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate optimized routes from orders')
    parser.add_argument('--orders', default=ORDERS_FILE, help='Path to orders CSV file')
    parser.add_argument('--district-rules', default=DISTRICT_RULES_FILE, help='Path to district rules CSV file')
    parser.add_argument('--road-rules', default=ROAD_RULES_FILE, help='Path to road rules CSV file')
    parser.add_argument('--output', default=OUTPUT_ROUTES, help='Path to output routes CSV file')
    parser.add_argument('--max-orders', type=int, default=MAX_ORDERS_PER_ROUTE, help='Max orders per route')
    
    args = parser.parse_args()
    
    try:
        result_df = generate_routes_from_orders(
            orders_file=args.orders,
            district_rules_file=args.district_rules,
            road_rules_file=args.road_rules,
            output_file=args.output,
            max_orders_per_route=args.max_orders
        )
        
        logger.info(f"✅ Success! Generated {result_df['route_id'].nunique()} routes")
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.error(f"\nMake sure you have:")
        logger.error(f"  1. Orders file: {args.orders}")
        logger.error(f"  2. District rules: {args.district_rules}")
        logger.error(f"  3. Road rules: {args.road_rules}")
        logger.error(f"\nRun 'python main.py' first to generate rules!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
