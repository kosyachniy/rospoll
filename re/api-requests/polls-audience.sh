curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.audience"}' https://rospoll.online/api/

curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.audience", "params": {"poll": 5}}' https://rospoll.online/api/

curl -X POST -H "Content-Type: application/json" -d '{"method": "polls.audience", "params": {"poll": 5, "question": 1}}' https://rospoll.online/api/