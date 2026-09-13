import json
import os
from typing import List, Dict, Any
from datetime import datetime

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "raw-data")

# ---------------------------------------------------------------------------
# Tool #1: search_product_catalog
# ---------------------------------------------------------------------------

def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    """
    Tra cứu sản phẩm/dịch vụ Vingroup theo danh mục và giá tối đa.
    
    Args:
        category: Loại sản phẩm ('xe_dien' hoặc 'du_lich').
        max_price: Giá tối đa (VNĐ). Mặc định không giới hạn.
    
    Returns:
        Danh sách sản phẩm phù hợp điều kiện.
    """
    # Ghép đường dẫn đến file dữ liệu; trả danh sách rỗng nếu file chưa tồn tại.
    catalog_file = os.path.join(RAW_DATA_DIR, "product_catalog.json")
    if not os.path.isfile(catalog_file):
        return []

    # Đọc JSON thành danh sách các dict; UTF-8 giúp đọc đúng tiếng Việt.
    with open(catalog_file, "r", encoding="utf-8") as file:
        products = json.load(file)

    # List comprehension giữ lại sản phẩm thỏa cả danh mục và giá tối đa.
    return [
        product for product in products
        if product["category"] == category and product["price_vnd"] <= max_price
    ]


# ---------------------------------------------------------------------------
# Tool #2: submit_support_ticket
# ---------------------------------------------------------------------------

def submit_support_ticket(
    customer_name: str,
    issue_description: str,
    priority: str = "medium"
) -> Dict[str, Any]:
    """
    Ghi nhận yêu cầu hỗ trợ của khách hàng vào hệ thống ticket.
    
    Args:
        customer_name: Tên khách hàng.
        issue_description: Mô tả vấn đề cần hỗ trợ.
        priority: Mức độ ưu tiên ('low', 'medium', 'high'). Mặc định 'medium'.
    
    Returns:
        Thông tin ticket vừa tạo bao gồm ticket_id, status.
    """
    # Nạp các ticket cũ để giữ lại khi lưu; lần đầu chưa có file thì dùng danh sách rỗng.
    tickets_file = os.path.join(RAW_DATA_DIR, "support_tickets.json")
    if os.path.isfile(tickets_file):
        with open(tickets_file, "r", encoding="utf-8") as file:
            tickets = json.load(file)
    else:
        tickets = []

    # Lấy giờ địa phương kèm múi giờ; định dạng ngày YYYYMMDD để đưa vào mã ticket.
    now = datetime.now().astimezone()
    today = now.strftime("%Y%m%d")
    # Tách số thứ tự sau dấu '-' cuối cùng, lấy số lớn nhất rồi cộng 1.
    # Số thứ tự tăng xuyên suốt các ngày; default=0 giúp ticket đầu tiên có số 1.
    seq = max(
        (int(ticket["ticket_id"].rsplit("-", 1)[1]) for ticket in tickets),
        default=0,
    ) + 1
    # Tạo ticket ở trạng thái mới mở. :03d đệm số 0, ví dụ 1 thành 001.
    # isoformat() lưu thời điểm theo chuẩn ISO 8601; category mặc định là general.
    ticket = {
        "ticket_id": f"TK-{today}-{seq:03d}",
        "customer_name": customer_name,
        "issue_description": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": now.isoformat(),
        "category": "general",
    }
    # Thêm ticket mới vào danh sách và tạo thư mục dữ liệu nếu chưa có.
    tickets.append(ticket)
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    # Chế độ 'w' ghi lại toàn bộ danh sách, gồm cả ticket cũ và mới.
    # ensure_ascii=False giữ nguyên chữ tiếng Việt; indent=2 giúp JSON dễ đọc.
    with open(tickets_file, "w", encoding="utf-8") as file:
        json.dump(tickets, file, ensure_ascii=False, indent=2)
    # Trả thông tin ticket vừa lưu để bên gọi có thể hiển thị mã và trạng thái.
    return ticket


# ---------------------------------------------------------------------------
# TOOL_DEFINITIONS — JSON Schemas mô tả cho LLM
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "search_product_catalog",
        "description": "Find Vingroup products by category and price cap.",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["xe_dien", "du_lich"],
                    "description": "xe_dien: electric vehicles; du_lich: travel.",
                },
                "max_price": {
                    "type": "integer",
                    "description": "Inclusive VND cap; omit for no cap.",
                    "default": 999999999999,
                },
            },
            "required": ["category"],
        },
    },
    {
        "name": "submit_support_ticket",
        "description": "Create a support ticket; return its ID and status.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {
                    "type": "string",
                },
                "issue_description": {
                    "type": "string",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "default": "medium",
                },
            },
            "required": ["customer_name", "issue_description"],
        },
    },
]


# ---------------------------------------------------------------------------
# TOOL_MAP — Ánh xạ tên tool → hàm thực thi
# ---------------------------------------------------------------------------

TOOL_MAP = {
    "search_product_catalog": search_product_catalog,
    "submit_support_ticket": submit_support_ticket
}
