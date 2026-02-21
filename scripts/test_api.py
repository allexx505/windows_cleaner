"""测试 API 端点"""
import requests

try:
    # Health check
    r = requests.get('http://127.0.0.1:8765/api/health', timeout=5)
    print('Health:', r.json())
    
    # Large files
    r = requests.get('http://127.0.0.1:8765/api/scan/large-files', params={'min_size_mb': 500, 'limit': 10}, timeout=10)
    print('Large files response:', r.status_code)
    data = r.json()
    print('Items count:', len(data.get('items', [])))
    for item in data.get('items', [])[:5]:
        print(f"  {item['path']}: {item['size_bytes']/1024/1024:.2f} MB")
except requests.exceptions.ConnectionError:
    print('Server not running')
except Exception as e:
    print('Error:', type(e).__name__, e)
