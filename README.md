# РосОпрос
## Run
### Development
``` docker-compose up --build ```

### Production
``` docker-compose -f docker-compose.prod.yml up --build ```

* Configure keys.json (Change MongoDB password)
* Configure sets.py (Change server links)
* Run (``` gunicorn app:app -k eventlet -w 1 -b :5050 --reload ```)
* Configure NGINX (Routing)