curl -X POST -H "Content-Type: application/json" -d '{"method": "users.notify", "params": {"text": "Тест\n\nтест"}}' https://rospoll.online/api/

curl -X POST -H "Content-Type: application/json" -d '{"method": "users.notify", "params": {"id": 1, "text": "Тест\n\nтест"}}' https://rospoll.online/api/