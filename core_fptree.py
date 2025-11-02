"""
Core FP-Tree Module
Chứa logic thuật toán FP-Growth thuần túy.
Module này không phụ thuộc vào bất kỳ module nào khác ngoài thư viện chuẩn.
"""

from collections import defaultdict


class FPNode:
    """
    Lớp đại diện cho một nút trong FP-Tree.
    """
    def __init__(self, item, count=0, parent=None):
        """
        Khởi tạo một FP-Tree node.
        
        Args:
            item: Item được lưu trữ tại node
            count: Số lần xuất hiện
            parent: Node cha
        """
        self.item = item
        self.count = count
        self.parent = parent
        self.children = {}
        self.link_node = None  # Link đến nút tiếp theo cùng item
    
    def increment(self, count=1):
        """
        Tăng số đếm của nút.
        
        Args:
            count: Số lượng cần tăng (mặc định là 1)
        """
        self.count += count


class FPTree:
    """
    Lớp triển khai FP-Tree (Frequent Pattern Tree).
    """
    def __init__(self, transactions, min_support_count):
        """
        Khởi tạo và xây dựng FP-Tree từ transactions.
        
        Args:
            transactions: Danh sách các transactions (mỗi transaction là một list)
            min_support_count: Ngưỡng support tối thiểu (số lần xuất hiện)
        """
        self.min_support_count = min_support_count
        self.header_table = {}
        self.root = FPNode(None, 0, None)
        
        # Scan 1: Tính tần suất của các items
        item_counts = defaultdict(int)
        for transaction in transactions:
            for item in transaction:
                item_counts[item] += 1
        
        # Lọc các items phổ biến
        frequent_items = {
            item: count for item, count in item_counts.items() 
            if count >= min_support_count
        }
        
        if not frequent_items:
            return
        
        # Sắp xếp items theo tần suất giảm dần
        self.freq_items = sorted(
            frequent_items.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        self.freq_item_order = {
            item: idx for idx, (item, _) in enumerate(self.freq_items)
        }
        
        # Scan 2: Xây dựng FP-Tree
        for transaction in transactions:
            # Lọc và sắp xếp transaction theo thứ tự tần suất
            sorted_items = sorted(
                [item for item in transaction if item in frequent_items],
                key=lambda x: self.freq_item_order[x]
            )
            self._insert_transaction(sorted_items)
    
    def _insert_transaction(self, sorted_items):
        """
        Chèn một transaction vào FP-Tree.
        
        Args:
            sorted_items: Transaction đã được sắp xếp theo tần suất
        """
        current_node = self.root
        
        for item in sorted_items:
            if item in current_node.children:
                # Nút đã tồn tại, tăng count
                current_node.children[item].increment()
            else:
                # Tạo nút mới
                new_node = FPNode(item, 1, current_node)
                current_node.children[item] = new_node
                
                # Cập nhật header table
                if item not in self.header_table:
                    self.header_table[item] = new_node
                else:
                    # Link đến nút cuối cùng trong chain
                    last_node = self.header_table[item]
                    while last_node.link_node is not None:
                        last_node = last_node.link_node
                    last_node.link_node = new_node
            
            current_node = current_node.children[item]
    
    def get_paths(self, item):
        """
        Lấy tất cả các paths kết thúc tại item.
        
        Args:
            item: Item cần lấy paths
        
        Returns:
            List các tuples (path, count) với path là list các items
        """
        paths = []
        node = self.header_table.get(item)
        
        while node is not None:
            path = []
            count = node.count
            parent = node.parent
            
            while parent.item is not None:
                path.append(parent.item)
                parent = parent.parent
            
            if path:
                paths.append((path[::-1], count))
            
            node = node.link_node
        
        return paths


def mine_fp_tree(transactions, min_support_count, prefix=None):
    """
    Khai phá FP-Tree để tìm các frequent itemsets.
    Sử dụng thuật toán FP-Growth với đệ quy.
    
    Args:
        transactions: Danh sách các transactions
        min_support_count: Ngưỡng support tối thiểu (số lần xuất hiện)
        prefix: Prefix hiện tại (cho đệ quy)
    
    Returns:
        Dictionary chứa các frequent itemsets (frozenset) và support counts (int)
    """
    if prefix is None:
        prefix = []
    
    frequent_itemsets = {}
    
    # Xây dựng FP-Tree
    tree = FPTree(transactions, min_support_count)
    
    if not tree.header_table:
        return frequent_itemsets
    
    # Duyệt các items từ ít phổ biến đến phổ biến nhất
    items = [item for item, _ in reversed(tree.freq_items)]
    
    for item in items:
        # Tạo frequent itemset mới
        new_itemset = prefix + [item]
        
        # Tính support count
        support_count = 0
        node = tree.header_table.get(item)
        while node is not None:
            support_count += node.count
            node = node.link_node
        
        # Lưu frequent itemset
        frequent_itemsets[frozenset(new_itemset)] = support_count
        
        # Tạo conditional pattern base
        conditional_patterns = tree.get_paths(item)
        conditional_transactions = []
        for path, count in conditional_patterns:
            conditional_transactions.extend([path] * count)
        
        # Đệ quy khai phá conditional FP-tree
        if conditional_transactions:
            conditional_itemsets = mine_fp_tree(
                conditional_transactions, 
                min_support_count, 
                new_itemset
            )
            frequent_itemsets.update(conditional_itemsets)
    
    return frequent_itemsets
