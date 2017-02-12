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
        now = int(time.time())
        self.redis.zadd(self.key, now + self.time, now) # score, value

    def request_available(self):
        self.__refresh()
        return self.redis.zcard(self.key) < self.max_requests

    def available_requests(self):
        self.__refresh()
        return self.max_requests - self.redis.zcard(self.key)

    def next_available_request(self):
        self.__refresh()
        res = self.redis.zrevrange(self.key, 0, 0, withscores=True)
        if len(res) != 1:
            return 0
        else:
            return res[0][1]
