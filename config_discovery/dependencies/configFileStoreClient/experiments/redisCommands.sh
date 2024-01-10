# Redis server container
docker login -u <username> -p <password>
docker pull redis:6.0.5-alpine
docker run --name r1 -p 6379:6379 -d redis:6.0.5-alpine


# Redis client command line utility
sudo apt-get install redis-tools
redis -h 127.0.0.1 -p 6379


# Redis client python binding
pip3 install redis
python3
>>> import redis
>>> redis.__version__
'3.5.3'
>>> pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
>>> r = redis.Redis(connection_pool=pool)
>>> r.set("k","v")
True
>>> r.get("k")
b'v'
>>>
>>> with open("/home/suren/p/mimas/cms/config_manager/default_ops_config.ini", "r") as f:
...     d = f.read()
>>> r.set ("player",d)
True
>>>
>>> v = r.get("player").decode("utf-8")
>>> with open("player.cfg", "w") as f:
...     f.write(v)


# Some helper packages
pip3 install lorem
python3
>>> import lorem
>>> lorem.__version__
'0.1.1'


