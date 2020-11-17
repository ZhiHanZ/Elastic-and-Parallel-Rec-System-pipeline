import threading
import redis


class RedisClient(object):
    # singleton Redis
    _redisClient = None  # type in Java: Jedis
    _instance_lock = threading.Lock()  # lock for singleton mode
    REDIS_END_POINT = "localhost"
    REDIS_PORT = 6379

    @classmethod
    def get_instance(cls):
        if cls._redisClient is None:
            with cls._instance_lock:
                if cls._redisClient is None:
                    cls._redisClient = redis.Redis(
                        host=cls.REDIS_END_POINT,
                        port=cls.REDIS_PORT,
                        decode_responses=True
                    )
        return cls._redisClient
