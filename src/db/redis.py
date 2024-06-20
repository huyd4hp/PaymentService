import redis
from threading import Lock
import jwt
from core import ACCESS_KEY
class Redis:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Redis, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, host='localhost', port=6379, db=0):
        if not self._initialized:
            self._client = redis.Redis(host=host, port=port, db=db)
            self._initialized = True
    def get_session(self,token:str):
        Client_ID = Session_ID = None
        payload = jwt.decode(token,ACCESS_KEY,algorithms=['HS256'])
        Client_ID = payload.get("_id")
        Session_ID = self._client.get(Client_ID)
        return Client_ID,Session_ID
    def set(self,key,value):
        self._client.set(key,value)
    @property
    def client(self):
        return self._client
    
RedisSesion = Redis(port=8100)