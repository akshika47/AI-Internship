"""Make the Northwind Home sample data: shop.db (SQLite) and orders.csv.

Northwind Home is a FICTIONAL online homeware store. Run it from the project folder with:  uv run data/make_data.py
It uses a fixed random seed, so everyone gets exactly the same data.

The story hidden in the data: in Q3 2026 Lighting revenue holds up, but its return
rate jumps from about 5% to about 30%. Almost every return is "damaged", and almost
all of them are one product, the Aurora Glass Pendant (a new courier started in July;
the data only shows the date, the cause comes from outside). Everything else grows slowly.
"""

import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "shop.db"
CSV_PATH = HERE / "orders.csv"
SEED = 4
CATEGORIES = ["Kitchen", "Bedding", "Lighting", "Decor", "Bath"]

# (name, category, price)
PRODUCTS = [
    ("Ceramic Mixing Bowl Set", "Kitchen", 34.0),
    ("Cast Iron Skillet", "Kitchen", 48.0),
    ("Oak Chopping Board", "Kitchen", 29.0),
    ("Stoneware Dinner Set", "Kitchen", 89.0),
    ("Copper Measuring Cups", "Kitchen", 19.0),
    ("Linen Duvet Cover", "Bedding", 95.0),
    ("Cotton Sheet Set", "Bedding", 70.0),
    ("Wool Throw Blanket", "Bedding", 65.0),
    ("Memory Foam Pillow", "Bedding", 39.0),
    ("Quilted Bedspread", "Bedding", 110.0),
    ("Aurora Glass Pendant", "Lighting", 129.0),
    ("Oak Table Lamp", "Lighting", 79.0),
    ("Brass Desk Lamp", "Lighting", 59.0),
    ("Linen Floor Lamp", "Lighting", 99.0),
    ("Paper Lantern Shade", "Lighting", 24.0),
    ("LED Strip Kit", "Lighting", 32.0),
    ("Woven Wall Basket", "Decor", 36.0),
    ("Stoneware Vase", "Decor", 42.0),
    ("Framed Botanical Print", "Decor", 55.0),
    ("Round Wall Mirror", "Decor", 85.0),
    ("Scented Candle Trio", "Decor", 28.0),
    ("Turkish Cotton Towel Set", "Bath", 45.0),
    ("Bamboo Bath Mat", "Bath", 26.0),
    ("Ceramic Soap Dish", "Bath", 14.0),
    ("Waffle Bathrobe", "Bath", 58.0),
]
# popularity weight of each product in orders (same order as PRODUCTS)
WEIGHTS = [6, 4, 6, 3, 5, 4, 5, 4, 6, 2, 10, 5, 4, 4, 5, 5, 4, 4, 3, 3, 8, 6, 5, 5, 3]

FIRST_NAMES = """Aisha Alex Amelia Andre Anika Ben Bella Carlos Chloe Daniel Deepak Elena Emma Ethan
Farah Felix Fiona Grace Hana Hugo Ines Isla Jack Jada Jonas Kai Kemi Layla Leo Lena Liam Lucia Maja
Marco Maya Mei Mila Nadia Noah Nora Olga Omar Oscar Paula Priya Quinn Rafael Rosa Ruby Sam Sara Sofia
Tariq Theo Uma Vera Wei Yara Yusuf Zara Zoe Callum Imogen Harvey Freya Lachlan Matilda Hamish Poppy
Klaus Greta Lukas Anna Jonas Mattis Elif Sven Frida Lars Hannah Tobias Marta Wyatt Harper Mason Ella
Logan Avery Carter Lily Dylan Nina Ravi Tomas Jun Alice Rhys Cleo""".split()
COUNTRIES = ["UK", "US", "DE", "AU"]
COUNTRY_W = [40, 30, 15, 15]
CHANNELS = ["web", "mobile app", "marketplace"]
CHANNEL_W = [55, 30, 15]
REASONS = ["damaged", "wrong size", "not as described", "changed mind"]

# normal return rate per category, and the mix of reasons for normal returns
BASE_RATE = {"Kitchen": 0.04, "Bedding": 0.07, "Lighting": 0.05, "Decor": 0.06, "Bath": 0.03}
REASON_W = {
    "Kitchen": [25, 5, 30, 40],
    "Bedding": [10, 45, 15, 30],
    "Lighting": [25, 5, 30, 40],
    "Decor": [30, 5, 30, 35],
    "Bath": [15, 25, 20, 40],
}
# the story: Aurora lines ordered from 2026-07-01 come back damaged
STORY_PRODUCT = "Aurora Glass Pendant"
STORY_START = "2026-07-01"
STORY_RETURN_PROB = 0.80

MONTHS = [(2025 + (6 + i) // 12, (6 + i) % 12 + 1) for i in range(15)]  # Jul 2025 .. Sep 2026


def build(seed=SEED):
    rnd = random.Random(seed)
    # customers: 120 signed up before July 2025, the rest spread over the 15 months
    customers = []
    for i in range(300):
        if i < 120:
            signup = date(2025, 1, 1) + timedelta(days=rnd.randint(0, 179))
        else:
            signup = date(2025, 7, 1) + timedelta(days=rnd.randint(0, 456))
        customers.append((FIRST_NAMES[i % len(FIRST_NAMES)], rnd.choices(COUNTRIES, COUNTRY_W)[0],
                          signup.isoformat()))
    rnd.shuffle(customers)
    customers.sort(key=lambda c: c[2])
    customers = [(i + 1, *c) for i, c in enumerate(customers)]

    orders, items, returns = [], [], []
    for idx, (year, month) in enumerate(MONTHS):
        n_orders = round(220 * (1 + 0.012 * idx) * (1.15 if (year, month) == (2025, 11) else 1.0))
        first = date(year, month, 1)
        last = date(year, month, 28)
        eligible = [c for c in customers if date.fromisoformat(c[3]) <= last]
        for _ in range(n_orders):
            cust = rnd.choice(eligible)
            lo = max(first, date.fromisoformat(cust[3]))
            d = lo + timedelta(days=rnd.randint(0, (last - lo).days))
            oid = len(orders) + 1
            status = "cancelled" if rnd.random() < 0.03 else "completed"
            orders.append((oid, d.isoformat(), cust[0], rnd.choices(CHANNELS, CHANNEL_W)[0], status))
            chosen = set()
            for _ in range(rnd.choices([1, 2, 3], [60, 28, 12])[0]):
                chosen.add(rnd.choices(range(len(PRODUCTS)), WEIGHTS)[0])
            for p in sorted(chosen):
                name, cat, price = PRODUCTS[p]
                qty = rnd.choices([1, 2], [85, 15])[0]
                iid = len(items) + 1
                items.append((iid, oid, p + 1, qty, price))
                if status == "cancelled":
                    continue
                story = name == STORY_PRODUCT and d.isoformat() >= STORY_START
                if story:
                    hit = rnd.random() < STORY_RETURN_PROB
                    reason = "damaged" if rnd.random() < 0.95 else rnd.choice(REASONS)
                else:
                    hit = rnd.random() < BASE_RATE[cat]
                    reason = rnd.choices(REASONS, REASON_W[cat])[0]
                if hit:
                    returns.append((len(returns) + 1, iid, (d + timedelta(days=rnd.randint(4, 18))).isoformat(), reason))
    return customers, orders, items, returns


def write(seed=SEED):
    customers, orders, items, returns = build(seed)
    if DB_PATH.exists():
        DB_PATH.unlink()
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE categories (category_id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE products (product_id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                               category_id INTEGER NOT NULL REFERENCES categories(category_id),
                               price REAL NOT NULL);
        CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, first_name TEXT NOT NULL,
                                country TEXT NOT NULL, signup_date TEXT NOT NULL);
        CREATE TABLE orders (order_id INTEGER PRIMARY KEY, order_date TEXT NOT NULL,
                             customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                             channel TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE order_items (order_item_id INTEGER PRIMARY KEY,
                                  order_id INTEGER NOT NULL REFERENCES orders(order_id),
                                  product_id INTEGER NOT NULL REFERENCES products(product_id),
                                  quantity INTEGER NOT NULL, price REAL NOT NULL);
        CREATE TABLE returns (return_id INTEGER PRIMARY KEY,
                              order_item_id INTEGER NOT NULL REFERENCES order_items(order_item_id),
                              return_date TEXT NOT NULL, reason TEXT NOT NULL);
        CREATE TABLE notes (note_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            title TEXT NOT NULL, text TEXT NOT NULL);
    """)
    db.executemany("INSERT INTO categories VALUES (?, ?)", list(enumerate(CATEGORIES, start=1)))
    db.executemany("INSERT INTO products VALUES (?, ?, ?, ?)",
                   [(i, n, CATEGORIES.index(c) + 1, p) for i, (n, c, p) in enumerate(PRODUCTS, start=1)])
    db.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    db.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)
    db.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items)
    db.executemany("INSERT INTO returns VALUES (?, ?, ?, ?)", returns)
    db.commit()

    with CSV_PATH.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_id", "order_date", "customer_id", "customer", "country", "channel", "status",
                    "product", "category", "quantity", "price", "line_total", "returned",
                    "return_date", "return_reason"])
        for r in db.execute("""
            SELECT o.order_id, o.order_date, o.customer_id, c.first_name, c.country, o.channel, o.status,
                   p.name, cat.name, i.quantity, i.price, ROUND(i.quantity * i.price, 2),
                   CASE WHEN r.return_id IS NULL THEN 'no' ELSE 'yes' END,
                   COALESCE(r.return_date, ''), COALESCE(r.reason, '')
            FROM order_items i JOIN orders o USING (order_id) JOIN customers c USING (customer_id)
            JOIN products p USING (product_id) JOIN categories cat USING (category_id)
            LEFT JOIN returns r USING (order_item_id)
            ORDER BY o.order_date, o.order_id, i.order_item_id"""):
            w.writerow(r)
    db.close()
    print(f"Wrote {DB_PATH.name} and {CSV_PATH.name}: {len(orders)} orders, {len(items)} order lines, "
          f"{len(returns)} returns, {len(customers)} customers.")


if __name__ == "__main__":
    write()
