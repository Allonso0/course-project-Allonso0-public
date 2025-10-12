import time

import requests


def test_rate_limiting_fast():
    print("Testing Rate Limiting (Fast Version)")
    print("=" * 50)

    base_url = "http://localhost:8000/api/v1"

    # Тест 1: GET /entries (лимит: 5/минуту)
    print("\n1. Testing GET /entries (limit: 5 per minute)")
    success_count = 0

    for i in range(8):  # Делаем 8 запросов чтобы превысить лимит 5
        try:
            response = requests.get(f"{base_url}/entries")
            print(f"   Request {i+1}: Status {response.status_code}")

            if response.status_code == 429:
                print("   RATE LIMIT HIT! Working correctly!")
                print(f"   Message: {response.json()}")
                success_count += 1
                break
            elif response.status_code == 200:
                print("   Response: OK")
            else:
                print(f"   Unexpected: {response.status_code}")

        except Exception as e:
            print(f"   Error: {e}")

        time.sleep(0.5)  # Небольшая задержка

    # Тест 2: POST /entries (лимит: 3/минуту)
    print("\n2. Testing POST /entries (limit: 3 per minute)")
    for i in range(5):  # Делаем 5 POST запросов
        try:
            data = {
                "title": f"Test Book {i}",
                "kind": "book",
                "link": "https://example.com/book",
                "status": "planned",
            }
            response = requests.post(f"{base_url}/entries", json=data)
            print(f"   POST Request {i+1}: Status {response.status_code}")

            if response.status_code == 429:
                print("   POST RATE LIMIT HIT! Working correctly!")
                success_count += 1
                break
            elif response.status_code == 201:
                print("   Response: Entry created")

        except Exception as e:
            print(f"   Error: {e}")

        time.sleep(0.5)

    # Итоги
    print("\n" + "=" * 50)
    if success_count >= 1:
        print(f"SUCCESS: Rate limiting is working! ({success_count}/2 tests passed)")
        return True
    else:
        print("Rate limiting still not working")
        print("   Check: Are you using the updated security.py with lower limits?")
        return False


if __name__ == "__main__":
    test_rate_limiting_fast()
