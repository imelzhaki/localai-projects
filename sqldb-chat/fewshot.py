"""Contoh pertanyaan/SQL bilingual (Bahasa Indonesia + Inggris) untuk few-shot prompting.

Setiap contoh berisi: question_id, question (pertanyaan bahasa alami), sql (kueri SQL),
dan language ("id" untuk Bahasa Indonesia, "en" untuk Inggris).

Contoh dirancang untuk mengajari model 3B pola domain ERP:
- pemilihan tabel yang benar
- penggunaan kolom yang sesuai
- join antar tabel
- value legend (kategori, status)
"""

_EXAMPLES = [
    # --- Customer: sederhana, satu tabel ---
    {
        "question_id": "cust_001",
        "question": "Tampilkan semua pelanggan.",
        "sql": "SELECT * FROM Customer;",
        "language": "id",
    },
    {
        "question_id": "cust_002",
        "question": "Show all customers.",
        "sql": "SELECT * FROM Customer;",
        "language": "en",
    },
    # --- Customer: filter kota ---
    {
        "question_id": "cust_003",
        "question": "Tampilkan pelanggan yang tinggal di Jakarta.",
        "sql": "SELECT * FROM Customer WHERE kota = 'Jakarta';",
        "language": "id",
    },
    {
        "question_id": "cust_004",
        "question": "Show customers in Jakarta.",
        "sql": "SELECT * FROM Customer WHERE kota = 'Jakarta';",
        "language": "en",
    },
    # --- Customer: hitung jumlah ---
    {
        "question_id": "cust_005",
        "question": "Berapa jumlah pelanggan?",
        "sql": "SELECT COUNT(*) AS jumlah_pelanggan FROM Customer;",
        "language": "id",
    },
    {
        "question_id": "cust_006",
        "question": "Count all customers.",
        "sql": "SELECT COUNT(*) AS jumlah_pelanggan FROM Customer;",
        "language": "en",
    },
    # --- Product: filter kategori ---
    {
        "question_id": "prod_001",
        "question": "Tampilkan produk dalam kategori Elektronik.",
        "sql": "SELECT * FROM Product WHERE kategori = 'Elektronik';",
        "language": "id",
    },
    {
        "question_id": "prod_002",
        "question": "Show products in the Elektronik category.",
        "sql": "SELECT * FROM Product WHERE kategori = 'Elektronik';",
        "language": "en",
    },
    # --- Product: produk dengan stok rendah ---
    {
        "question_id": "prod_003",
        "question": "Tampilkan produk yang stoknya di bawah 20.",
        "sql": "SELECT * FROM Product WHERE stok < 20;",
        "language": "id",
    },
    {
        "question_id": "prod_004",
        "question": "Show products with stock below 20.",
        "sql": "SELECT * FROM Product WHERE stok < 20;",
        "language": "en",
    },
    # --- Sales_Order: pesanan pelanggan tertentu ---
    {
        "question_id": "so_001",
        "question": "Tampilkan pesanan penjualan untuk pelanggan Budi Santoso.",
        "sql": "SELECT so.* FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id WHERE c.nama = 'Budi Santoso';",
        "language": "id",
    },
    {
        "question_id": "so_002",
        "question": "Show sales orders for customer Budi Santoso.",
        "sql": "SELECT so.* FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id WHERE c.nama = 'Budi Santoso';",
        "language": "en",
    },
    # --- Sales_Order: total penjualan per pelanggan ---
    {
        "question_id": "so_003",
        "question": "Tampilkan total penjualan per pelanggan.",
        "sql": "SELECT c.nama, SUM(so.total) AS total_penjualan FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id GROUP BY c.customer_id, c.nama;",
        "language": "id",
    },
    {
        "question_id": "so_004",
        "question": "Show total sales per customer.",
        "sql": "SELECT c.nama, SUM(so.total) AS total_penjualan FROM Sales_Order so JOIN Customer c ON so.customer_id = c.customer_id GROUP BY c.customer_id, c.nama;",
        "language": "en",
    },
    # --- Sales_Order_Item: item dalam pesanan ---
    {
        "question_id": "soi_001",
        "question": "Tampilkan item pesanan untuk pesanan nomor 1.",
        "sql": "SELECT soi.*, p.nama AS nama_produk FROM Sales_Order_Item soi JOIN Product p ON soi.product_id = p.product_id WHERE soi.order_id = 1;",
        "language": "id",
    },
    {
        "question_id": "soi_002",
        "question": "Show order items for order number 1.",
        "sql": "SELECT soi.*, p.nama AS nama_produk FROM Sales_Order_Item soi JOIN Product p ON soi.product_id = p.product_id WHERE soi.order_id = 1;",
        "language": "en",
    },
    # --- Purchase_Order: pesanan pembelian ---
    {
        "question_id": "po_001",
        "question": "Tampilkan semua pesanan pembelian yang statusnya Lunas.",
        "sql": "SELECT * FROM Purchase_Order WHERE status = 'Lunas';",
        "language": "id",
    },
    {
        "question_id": "po_002",
        "question": "Show all purchase orders with status Lunas.",
        "sql": "SELECT * FROM Purchase_Order WHERE status = 'Lunas';",
        "language": "en",
    },
    # --- Supplier: produk per supplier ---
    {
        "question_id": "sup_001",
        "question": "Tampilkan produk yang disuplai oleh setiap supplier.",
        "sql": "SELECT s.nama AS nama_supplier, p.nama AS nama_produk FROM Product p JOIN Supplier s ON p.supplier_id = s.supplier_id;",
        "language": "id",
    },
    {
        "question_id": "sup_002",
        "question": "Show products supplied by each supplier.",
        "sql": "SELECT s.nama AS nama_supplier, p.nama AS nama_produk FROM Product p JOIN Supplier s ON p.supplier_id = s.supplier_id;",
        "language": "en",
    },
]


def get_fewshot_examples():
    """Kembalikan daftar contoh pertanyaan/SQL bilingual.

    Setiap item adalah dict dengan kunci: question_id, question, sql, language.
    """
    return list(_EXAMPLES)


def get_fewshot_examples_by_language(language):
    """Kembalikan contoh hanya untuk bahasa tertentu ("id" atau "en")."""
    return [ex for ex in _EXAMPLES if ex["language"] == language]


def format_fewshot(examples=None, max_examples=6):
    """Format contoh few-shot sebagai teks prompt untuk model.

    Args:
        examples: daftar contoh (default: semua contoh).
        max_examples: jumlah contoh maksimum yang disertakan.

    Returns:
        String berisi contoh Q/SQL yang diformat untuk prompt.
    """
    if examples is None:
        examples = _EXAMPLES
    examples = examples[:max_examples]
    lines = ["Contoh pertanyaan dan kueri SQL:"]
    for ex in examples:
        lines.append(f"Pertanyaan ({ex['language']}): {ex['question']}")
        lines.append(f"SQL: {ex['sql']}")
        lines.append("")
    return "\n".join(lines)