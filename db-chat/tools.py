import logging
from database import DB_PATH, execute_query, init_db

logger = logging.getLogger(__name__)

# Pastikan database diinisialisasi saat alat dimuat
init_db()


def _format_rupiah(nilai):
    return f"Rp {nilai:,.0f}".replace(",", ".")


def get_sales_data(category=None, month=None):
    """Data penjualan per kategori dan bulan.

    Args:
        category: Nama kategori produk (contoh: "Elektronik").
        month: Bulan (contoh: "last" untuk bulan lalu, atau "YYYY-MM").
    """
    if category:
        sql = """
        SELECT p.nama AS produk, p.kategori, so.tanggal, so.total, so.status,
               c.nama AS pelanggan
        FROM Sales_Order so
        JOIN Sales_Order_Item soi ON soi.order_id = so.order_id
        JOIN Product p ON p.product_id = soi.product_id
        JOIN Customer c ON c.customer_id = so.customer_id
        WHERE p.kategori = ?
        """
        params = [category]
        if month == "last":
            sql += " AND strftime('%Y-%m', so.tanggal) = (SELECT MAX(strftime('%Y-%m', tanggal)) FROM Sales_Order)"
        elif month:
            sql += " AND strftime('%Y-%m', so.tanggal) = ?"
            params.append(month)
        sql += " ORDER BY so.tanggal DESC"
        rows = execute_query(sql, tuple(params))
        return rows
    # Tanpa filter kategori: semua penjualan
    sql = """
    SELECT so.order_id, so.tanggal, so.total, so.status, c.nama AS pelanggan
    FROM Sales_Order so
    JOIN Customer c ON c.customer_id = so.customer_id
    ORDER BY so.tanggal DESC
    LIMIT 20
    """
    return execute_query(sql, ())


def get_customer(customer_id=None, nama=None, kota=None):
    """Detail pelanggan berdasarkan ID, nama, atau kota."""
    if customer_id is not None:
        rows = execute_query(
            "SELECT * FROM Customer WHERE customer_id = ?", (customer_id,)
        )
        return rows[0] if rows else {}
    conditions = []
    params = []
    if nama:
        conditions.append("nama LIKE ?")
        params.append(f"%{nama}%")
    if kota:
        conditions.append("kota = ?")
        params.append(kota)
    if not conditions:
        return []
    sql = "SELECT * FROM Customer WHERE " + " AND ".join(conditions)
    return execute_query(sql, tuple(params))


def get_product(product_id=None, nama=None, kategori=None, stok_max=None, harga_max=None):
    """Detail produk dan stok berdasarkan ID, nama, kategori, stok maksimal, atau harga maksimal."""
    if product_id is not None:
        rows = execute_query(
            "SELECT * FROM Product WHERE product_id = ?", (product_id,)
        )
        return rows[0] if rows else {}
    conditions = []
    params = []
    if nama:
        conditions.append("nama LIKE ?")
        params.append(f"%{nama}%")
    if kategori:
        conditions.append("kategori = ?")
        params.append(kategori)
    if stok_max is not None:
        conditions.append("stok <= ?")
        params.append(stok_max)
    if harga_max is not None:
        conditions.append("harga <= ?")
        params.append(harga_max)
    if not conditions:
        return {}
    sql = "SELECT * FROM Product WHERE " + " AND ".join(conditions)
    return execute_query(sql, tuple(params))


def get_sales_order(order_id=None, customer_id=None, rentang_tanggal=None, status=None):
    """Pesanan penjualan berdasarkan ID order, ID pelanggan, rentang tanggal, atau status."""
    conditions = []
    params = []
    if order_id is not None:
        conditions.append("so.order_id = ?")
        params.append(order_id)
    if customer_id is not None:
        conditions.append("so.customer_id = ?")
        params.append(customer_id)
    if rentang_tanggal:
        # Format: "YYYY-MM-DD s.d. YYYY-MM-DD"
        parts = rentang_tanggal.split(" s.d. ")
        if len(parts) == 2:
            conditions.append("so.tanggal BETWEEN ? AND ?")
            params.extend(parts)
    if status:
        conditions.append("so.status = ?")
        params.append(status)
    if not conditions:
        return []
    sql = """
    SELECT so.order_id, so.tanggal, so.total, so.status, c.nama AS pelanggan
    FROM Sales_Order so
    JOIN Customer c ON c.customer_id = so.customer_id
    WHERE """ + " AND ".join(conditions) + """
    ORDER BY so.tanggal DESC
    """
    return execute_query(sql, tuple(params))


def get_purchase_order(order_id=None, supplier_id=None, rentang_tanggal=None):
    """Pesanan pembelian berdasarkan ID order, ID supplier, atau rentang tanggal."""
    conditions = []
    params = []
    if order_id is not None:
        conditions.append("po.order_id = ?")
        params.append(order_id)
    if supplier_id is not None:
        conditions.append("po.supplier_id = ?")
        params.append(supplier_id)
    if rentang_tanggal:
        parts = rentang_tanggal.split(" s.d. ")
        if len(parts) == 2:
            conditions.append("po.tanggal BETWEEN ? AND ?")
            params.extend(parts)
    if not conditions:
        return []
    sql = """
    SELECT po.order_id, po.tanggal, po.total, po.status, s.nama AS supplier
    FROM Purchase_Order po
    JOIN Supplier s ON s.supplier_id = po.supplier_id
    WHERE """ + " AND ".join(conditions) + """
    ORDER BY po.tanggal DESC
    """
    return execute_query(sql, tuple(params))


def get_supplier(supplier_id=None, nama=None):
    """Detail supplier berdasarkan ID atau nama."""
    if supplier_id is not None:
        rows = execute_query(
            "SELECT * FROM Supplier WHERE supplier_id = ?", (supplier_id,)
        )
        return rows[0] if rows else {}
    if nama:
        rows = execute_query(
            "SELECT * FROM Supplier WHERE nama LIKE ?", (f"%{nama}%",)
        )
        return rows[0] if rows else {}
    return {}


def list_customers():
    """Daftar semua pelanggan (ID, nama, kota, telepon, email)."""
    return execute_query(
        "SELECT customer_id, nama, kota, telepon, email FROM Customer ORDER BY nama"
    )


def list_sales_orders():
    """Daftar semua pesanan penjualan (ID, tanggal, total, status, pelanggan)."""
    return execute_query(
        """
        SELECT so.order_id, so.tanggal, so.total, so.status, c.nama AS pelanggan
        FROM Sales_Order so
        JOIN Customer c ON c.customer_id = so.customer_id
        ORDER BY so.tanggal DESC
        """
    )


def list_purchase_orders():
    """Daftar semua pesanan pembelian (ID, tanggal, total, status, supplier)."""
    return execute_query(
        """
        SELECT po.order_id, po.tanggal, po.total, po.status, s.nama AS supplier
        FROM Purchase_Order po
        JOIN Supplier s ON s.supplier_id = po.supplier_id
        ORDER BY po.tanggal DESC
        """
    )


def list_suppliers():
    """Daftar semua supplier (ID, nama, kontak, kota, telepon)."""
    return execute_query(
        "SELECT supplier_id, nama, kontak, kota, telepon FROM Supplier ORDER BY nama"
    )


def list_products():
    """Daftar semua produk (ID, nama, kategori, harga, stok)."""
    return execute_query(
        "SELECT product_id, nama, kategori, harga, stok FROM Product ORDER BY nama"
    )


def get_sales_order_items(order_id=None):
    """Detail item dalam pesanan penjualan (produk, kuantitas, harga satuan, subtotal)."""
    if order_id is not None:
        sql = """
        SELECT soi.item_id, p.nama AS produk, soi.kuantitas, soi.harga_satuan,
               (soi.kuantitas * soi.harga_satuan) AS subtotal
        FROM Sales_Order_Item soi
        JOIN Product p ON p.product_id = soi.product_id
        WHERE soi.order_id = ?
        ORDER BY soi.item_id
        """
        return execute_query(sql, (order_id,))
    sql = """
    SELECT soi.item_id, so.order_id, p.nama AS produk, soi.kuantitas, soi.harga_satuan,
           (soi.kuantitas * soi.harga_satuan) AS subtotal
    FROM Sales_Order_Item soi
    JOIN Sales_Order so ON so.order_id = soi.order_id
    JOIN Product p ON p.product_id = soi.product_id
    ORDER BY so.order_id DESC, soi.item_id
    LIMIT 50
    """
    return execute_query(sql, ())


def get_database_stats():
    """Statistik ringkasan database: jumlah baris per tabel."""
    tables = ["Customer", "Supplier", "Product", "Sales_Order", "Sales_Order_Item", "Purchase_Order"]
    stats = {}
    for table in tables:
        row = execute_query(f"SELECT COUNT(*) AS cnt FROM {table}")
        stats[table] = row[0]["cnt"] if row else 0
    return stats


# Peta nama alat ke fungsi, untuk dieksekusi oleh ollama_client
execute_tool_map = {
    "get_sales_data": get_sales_data,
    "get_customer": get_customer,
    "get_product": get_product,
    "get_sales_order": get_sales_order,
    "get_purchase_order": get_purchase_order,
    "get_supplier": get_supplier,
    "list_customers": list_customers,
    "list_sales_orders": list_sales_orders,
    "list_purchase_orders": list_purchase_orders,
    "list_suppliers": list_suppliers,
    "list_products": list_products,
    "get_sales_order_items": get_sales_order_items,
    "get_database_stats": get_database_stats,
}


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_sales_data",
            "description": "Ambil data penjualan per kategori produk dan bulan. Gunakan untuk pertanyaan tentang penjualan, omset, atau produk yang laku.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Kategori produk (contoh: Elektronik, Aksesori, Komputer)",
                    },
                    "month": {
                        "type": "string",
                        "description": "Bulan. Gunakan 'last' untuk bulan lalu, atau format 'YYYY-MM'",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "Ambil detail pelanggan berdasarkan ID, nama, atau kota.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {"type": "integer", "description": "ID pelanggan"},
                    "nama": {"type": "string", "description": "Nama pelanggan (parsial cocok)"},
                    "kota": {"type": "string", "description": "Kota pelanggan"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Ambil detail produk dan stok berdasarkan ID, nama, kategori, stok maksimal, atau harga maksimal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID produk"},
                    "nama": {"type": "string", "description": "Nama produk (parsial cocok)"},
                    "kategori": {"type": "string", "description": "Kategori produk"},
                    "stok_max": {"type": "integer", "description": "Stok maksimal (produk dengan stok <= nilai ini)"},
                    "harga_max": {"type": "integer", "description": "Harga maksimal (produk dengan harga <= nilai ini)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_order",
            "description": "Ambil pesanan penjualan berdasarkan ID order, ID pelanggan, rentang tanggal, atau status pembayaran.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "ID pesanan penjualan"},
                    "customer_id": {"type": "integer", "description": "ID pelanggan"},
                    "rentang_tanggal": {
                        "type": "string",
                        "description": "Rentang tanggal format 'YYYY-MM-DD s.d. YYYY-MM-DD'",
                    },
                    "status": {
                        "type": "string",
                        "description": "Status pembayaran (contoh: Lunas, Belum Lunas, Pending)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_purchase_order",
            "description": "Ambil pesanan pembelian berdasarkan ID order, ID supplier, atau rentang tanggal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "ID pesanan pembelian"},
                    "supplier_id": {"type": "integer", "description": "ID supplier"},
                    "rentang_tanggal": {
                        "type": "string",
                        "description": "Rentang tanggal format 'YYYY-MM-DD s.d. YYYY-MM-DD'",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_supplier",
            "description": "Ambil detail supplier berdasarkan ID atau nama.",
            "parameters": {
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "integer", "description": "ID supplier"},
                    "nama": {"type": "string", "description": "Nama supplier (parsial cocok)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_customers",
            "description": "Daftar semua pelanggan (ID, nama, kota, telepon, email). Gunakan untuk pertanyaan yang meminta daftar lengkap pelanggan.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_sales_orders",
            "description": "Daftar semua pesanan penjualan (ID, tanggal, total, status, pelanggan). Gunakan untuk pertanyaan tentang daftar atau jumlah pesanan penjualan.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_purchase_orders",
            "description": "Daftar semua pesanan pembelian (ID, tanggal, total, status, supplier). Gunakan untuk pertanyaan tentang daftar atau jumlah pesanan pembelian.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_suppliers",
            "description": "Daftar semua supplier (ID, nama, kontak, kota, telepon). Gunakan untuk pertanyaan yang meminta daftar lengkap supplier.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "Daftar semua produk (ID, nama, kategori, harga, stok). Gunakan untuk pertanyaan yang meminta daftar lengkap produk.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_order_items",
            "description": "Detail item dalam pesanan penjualan (produk, kuantitas, harga satuan, subtotal). Gunakan order_id untuk item dalam satu pesanan, atau tanpa argumen untuk daftar item terbaru.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer", "description": "ID pesanan penjualan"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_database_stats",
            "description": "Statistik ringkasan database: jumlah baris per tabel. Gunakan untuk mengetahui jumlah data di setiap tabel.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
