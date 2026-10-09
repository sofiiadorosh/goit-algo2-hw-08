"""
Завдання 1. Оптимізація доступу до даних за допомогою LRU-кешу.

Порівнює час обробки послідовності запитів Range/Update
без кешу та з LRU-кешем ємністю K = 1000.
"""

import random
import time
from collections import OrderedDict

ARRAY_SIZE = 100_000
QUERIES_COUNT = 50_000
CACHE_CAPACITY = 1000


class LRUCache:
    """LRU-кеш на основі OrderedDict: найсвіжіші ключі — в кінці."""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


cache = LRUCache(CACHE_CAPACITY)


def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])


def update_no_cache(array, index, value):
    array[index] = value


def range_sum_with_cache(array, left, right):
    key = (left, right)
    result = cache.get(key)
    if result == -1:
        result = sum(array[left:right + 1])
        cache.put(key, result)
    return result


def update_with_cache(array, index, value):
    array[index] = value
    # Лінійний прохід по ключах: видаляємо всі діапазони, що містять index
    stale_keys = [(left, right) for left, right in cache.cache
                  if left <= index <= right]
    for key in stale_keys:
        del cache.cache[key]


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


def run_queries(array, queries, range_func, update_func):
    """Виконує всі запити; повертає (час у секундах, список результатів Range)."""
    results = []
    start = time.perf_counter()
    for query_type, a, b in queries:
        if query_type == "Range":
            results.append(range_func(array, a, b))
        else:
            update_func(array, a, b)
    elapsed = time.perf_counter() - start
    return elapsed, results


def main():
    base_array = [random.randint(1, 100) for _ in range(ARRAY_SIZE)]
    queries = make_queries(ARRAY_SIZE, QUERIES_COUNT)

    updates = sum(1 for query in queries if query[0] == "Update")
    print(f"Масив: {ARRAY_SIZE:,} елементів | Запитів: {QUERIES_COUNT:,} "
          f"(Range: {QUERIES_COUNT - updates:,}, Update: {updates:,})\n")

    no_cache_time, no_cache_results = run_queries(
        base_array.copy(), queries, range_sum_no_cache, update_no_cache)
    cache_time, cache_results = run_queries(
        base_array.copy(), queries, range_sum_with_cache, update_with_cache)

    assert no_cache_results == cache_results, "Результати з кешем і без кешу відрізняються!"

    speedup = no_cache_time / cache_time
    print(f"Без кешу : {no_cache_time:6.2f} c")
    print(f"LRU-кеш  : {cache_time:6.2f} c  (прискорення ×{speedup:.1f})")


if __name__ == "__main__":
    main()
