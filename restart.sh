uwsgi --http :9090 --wsgi-file main.py --honour-stdin --threads 10
uwsgi --http :9091 --wsgi-file main.py --honour-stdin --threads 10