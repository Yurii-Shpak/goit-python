from random import randint
import redis

CACHE_SIZE = 5
CALLS_NUMBER = 10

if __name__ == '__main__':

    conn = redis.Redis(host='127.0.0.1', port=6379)

    # Read cache of numbers from Redis
    cache = [int(n) for n in map(lambda x: x.decode(),
                                 conn.lrange('lru_values', 0, CACHE_SIZE - 1))]
    calls = [int(n) for n in map(lambda x: x.decode(),
                                 conn.lrange('lru_calls', 0, CACHE_SIZE - 1))]
    print(f'Cache: {cache}')
    print(f'Calls: {calls}')

    if len(calls):
        max_call = max(calls) + 1
    else:
        max_call = 1

    # Count cache calls starting from max call from script call
    for call in range(max_call, max_call + CALLS_NUMBER):
        # Put random numbers in the range 1..10 in the cache
        num = randint(1, 10)
        # Is the number in the cache?
        if num in cache:
            # Update the call number
            idx = cache.index(num)
            conn.lset('lru_calls', idx, call)
            calls[idx] = call
            print(f'Call {call}. Cached number {num}')
        # If the number is not in the cache and the cache is full
        elif conn.llen('lru_values') == CACHE_SIZE:
            # replace value with minimal call number
            idx = calls.index(min(calls))
            conn.lset('lru_values', idx, num)
            conn.lset('lru_calls', idx, call)
            prev_num = cache[idx]
            prev_call = calls[idx]
            cache[idx] = num
            calls[idx] = call
            print(
                f'Call {call}. Number {num} has replaced the number {prev_num} with call {prev_call}')
        else:  # If the number is not in the cache and the cache is NOT full
            conn.rpush('lru_values', num)
            conn.rpush('lru_calls', call)
            cache.append(num)
            calls.append(call)
            print(f'Call {call}. Added number {num}')

    print(f'Cache: {cache}')
    print(f'Calls: {calls}')
