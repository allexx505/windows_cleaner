"""检查索引数据库内容"""
import sqlite3
import os

db_path = os.path.join(os.environ['APPDATA'], 'WindowsCleaner', 'file_index.db')
print(f"Database: {db_path}")

conn = sqlite3.connect(db_path)

# Check table exists
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='file_index'")
tables = cursor.fetchall()
print(f"Tables: {tables}")

# Count records
cursor = conn.execute("SELECT COUNT(*) FROM file_index")
count = cursor.fetchone()[0]
print(f"Total records: {count}")

# Count large files >= 500MB
cursor = conn.execute("SELECT COUNT(*) FROM file_index WHERE size_bytes >= 524288000")
large_count = cursor.fetchone()[0]
print(f"Large files (>=500MB): {large_count}")

# Sample some large files
print("\nTop 10 large files:")
cursor = conn.execute("SELECT path, size_bytes FROM file_index WHERE size_bytes >= 524288000 ORDER BY size_bytes DESC LIMIT 10")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]/1024/1024:.2f} MB")

# Check by volume
print("\nRecords by volume:")
cursor = conn.execute("SELECT volume, COUNT(*) FROM file_index GROUP BY volume")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} files")

conn.close()
