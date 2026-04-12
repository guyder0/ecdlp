from typing import Tuple, Optional
from fastecdsa.point import Point
from fastecdsa.curve import Curve
import random

from .base import BaseSolver
from ..utils.math_bridge import MathBridge
from ..exceptions import SolverError

class PollardRhoSolver(BaseSolver):
    """
    Универсальный алгоритм Ро-Полланда.
    Сложность: O(sqrt(n)).
    """

    def _get_next_state(self, pt: Point, a: int, b: int, P: Point, Q: Point, n: int) -> Tuple[Point, int, int]:
        # Разбиение на 3 непересекающихся подмножества
        idx = pt.x % 3
        
        if idx == 0:
            return pt + Q, a, (b + 1) % n
        elif idx == 1:
            return pt + pt, (a * 2) % n, (b * 2) % n
        else:
            return pt + P, (a + 1) % n, b

    def solve(self, P: Point, Q: Point, curve: Curve, subgroup_order: Optional[int]=None) -> int:
        n = subgroup_order if subgroup_order else curve.q

        if Q == P * 0:
            return 0
        
        if n < 100:
            curr = P * 0
            for x in range(n):
                if curr == Q:
                    return x
                curr = curr + P
            raise SolverError(f"Логарифм не найден в группе порядка {n}")
        
        # Начальное состояние
        a_t = a_h = random.randint(1, n - 1)
        b_t = b_h = random.randint(1, n - 1)
        pt_t = a_t * P + b_t * Q
        pt_h = a_h * P + b_h * Q

        while True:
            self._check_interruption()
            
            # Шаг tortoise
            pt_t, a_t, b_t = self._get_next_state(pt_t, a_t, b_t, P, Q, n)
            
            # Шаги hare - дважды
            pt_h, a_h, b_h = self._get_next_state(pt_h, a_h, b_h, P, Q, n)
            pt_h, a_h, b_h = self._get_next_state(pt_h, a_h, b_h, P, Q, n)

            if pt_t == pt_h:
                # Найдена коллизия: a_t*P + b_t*Q = a_h*P + b_h*Q
                # (b_t - b_h) * x = (a_h - a_t) (mod n)
                res_a = (a_h - a_t) % n
                res_b = (b_t - b_h) % n
                
                if res_b == 0:
                    # Неудачная итерация (редкий случай), перезапуск с другими a, b
                    return self.solve(P, Q, curve, subgroup_order=subgroup_order)
                
                try:
                    return (res_a * MathBridge.inverse(res_b, n)) % n
                except SolverError:
                    raise SolverError("Не удалось вычислить обратный элемент при коллизии.")