import psycopg2

print("🚀 SmartMarket - Adding Categories")
print("="*50)

# Connect
conn = psycopg2.connect(
    host="switchback.proxy.rlwy.net",
    port=45220,
    database="railway",
    user="postgres",
    password="hNRPqAkvvnxRCrCEzJwnhZqExaxlCYcJ"
)

print("✅ Connected to DB\n")

cur = conn.cursor()

# 1. Create categories table
print("📊 Creating categories table...")
cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  name_he VARCHAR(100) NOT NULL,
  icon VARCHAR(50)
)
""")
print("✅ Categories table created\n")

# 2. Add column to products
print("📦 Adding category_id to products...")
cur.execute("""
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS category_id INT REFERENCES categories(id)
""")
print("✅ Column added\n")

# 3. Insert categories
print("📋 Inserting categories...")
cur.execute("""
INSERT INTO categories (name, name_he, icon) VALUES
  ('dairy', 'מוצרי חלב', '🥛'),
  ('bread', 'לחם ומאפים', '🍞'),
  ('drinks', 'משקאות', '🥤'),
  ('snacks', 'חטיפים וממתקים', '🍫'),
  ('vegetables', 'ירקות ופירות', '🥬'),
  ('cleaning', 'ניקיון', '🧹'),
  ('personal', 'טיפוח אישי', '🧴'),
  ('frozen', 'קפואים', '❄️'),
  ('meat', 'בשר ודגים', '🍖')
ON CONFLICT DO NOTHING
""")
print("✅ 9 categories inserted\n")

# 4. Auto-tag products
print("🏷️ Auto-tagging products...")

updates = [
    (1, ['חלב', 'גבינה', 'יוגורט', 'חמאה']),
    (2, ['לחם', 'חלה', 'פיתה', 'בגט']),
    (3, ['מיץ', 'קולה', 'משקה', 'שתיה']),
    (4, ['שוקולד', 'חטיף', 'ממתק', 'ביסקויט']),
    (5, ['עגבני', 'מלפפון', 'תפוח', 'בננה']),
    (6, ['ניקוי', 'סבון', 'אבקת']),
    (7, ['שמפו', 'קרם', 'מרכך']),
    (9, ['בשר', 'עוף', 'דג'])
]

for cat_id, keywords in updates:
    conditions = " OR ".join([f"name ILIKE '%{kw}%'" for kw in keywords])
    cur.execute(f"""
        UPDATE products 
        SET category_id = {cat_id} 
        WHERE category_id IS NULL AND ({conditions})
    """)

conn.commit()
print("✅ Products tagged\n")

# 5. Show results
print("="*50)
print("📊 Results:")
print("="*50)

cur.execute("""
SELECT c.name_he, COUNT(*) as count
FROM products p 
JOIN categories c ON p.category_id = c.id 
GROUP BY c.name_he
ORDER BY count DESC
""")

for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} products")

# Count uncategorized
cur.execute("SELECT COUNT(*) FROM products WHERE category_id IS NULL")
uncategorized = cur.fetchone()[0]
print(f"\n  (לא מסווג: {uncategorized})")

print("\n" + "="*50)
print("✅ Categories setup complete!")
print("="*50)

cur.close()
conn.close()