import time

class RedisLimiter:
    def __init__(self, redis, max_requests, time, key):
        self.redis = redis
        self.max_requests = max_requests
        self.time = time
        self.key = key

    def __refresh(self):
        self.redis.zremrangebyscore(self.key, 0, time.time())

    def add(self):
        now = time.time()
        self.redis.zadd(self.key, now + self.time, now) # score, value

    def request_available(self):
        self.__refresh()
        return self.redis.zcard(self.key) < self.max_requests

    def available_requests(self):
        self.__refresh()
        return self.max_requests - self.redis.zcard(self.key)
