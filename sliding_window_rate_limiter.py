"""
Завдання 2. Rate Limiter на основі алгоритму Sliding Window
для обмеження частоти повідомлень у чаті.
"""

import random
import time
from collections import deque
from typing import Dict


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_messages: Dict[str, deque] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Видаляє з вікна користувача повідомлення, старші за window_size."""
        messages = self.user_messages.get(user_id)
        if messages is None:
            return

        window_start = current_time - self.window_size
        while messages and messages[0] <= window_start:
            messages.popleft()

        # Вікно порожнє — видаляємо запис про користувача
        if not messages:
            del self.user_messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id, time.time())
        messages = self.user_messages.get(user_id)
        return messages is None or len(messages) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if not self.can_send_message(user_id):
            return False
        self.user_messages.setdefault(user_id, deque()).append(time.time())
        return True

    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        messages = self.user_messages.get(user_id)
        if messages is None or len(messages) < self.max_requests:
            return 0.0
        # Чекаємо, поки найстаріше повідомлення вийде за межі вікна
        return max(0.0, messages[0] + self.window_size - current_time)


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
