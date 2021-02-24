curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.answer", "params": {"poll": 1, "question": 1, "answer": 1, "token": "test"}' https://rospoll.online/api/

curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.answer", "params": {"poll": 1, "question": 1, "answer": [1, 2]}, "token": "test"}' https://rospoll.online/api/

curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.answer", "params": {"poll": 1, "question": 1, "answer": "test"}, "token": "test"}' https://rospoll.online/api/