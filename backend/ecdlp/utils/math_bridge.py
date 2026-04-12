"""
Вспомогательный модуль для выполнения теоретико-числовых расчетов.
Использует SymPy для обеспечения точности и производительности.
"""

from typing import List, Tuple, Dict
from sympy.ntheory.modular import crt
from sympy.ntheory import factorint
from sympy.core.numbers import mod_inverse
from ..exceptions import SolverError

class MathBridge:
    """
    Инструментарий для операций над целыми числами в контексте криптоанализа.
    """

    @staticmethod
    def solve_crt(remainders: List[int], moduli: List[int]) -> int:
        """
        Решает систему сравнений через Китайскую теорему об остатках.
        Используется в алгоритме Похлига-Хеллмана.
        
        :param remainders: Список остатков.
        :param moduli: Список модулей (взаимно простых).
        :return: Решение системы x mod (m1 * m2 * ...).
        """
        result = crt(moduli, remainders)
        if result is None:
            raise SolverError("Не удалось найти решение через КТО. Модули могут быть не взаимно простыми.")
        return int(result[0])

    @staticmethod
    def get_factorization(n: int) -> Dict[int, int]:
        """
        Выполняет факторизацию целого числа.
        
        :param n: Число для факторизации (например, порядок группы).
        :return: Словарь вида {простой_множитель: степень}.
        """
        return factorint(n)

    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """
        Расширенный алгоритм Евклида.
        Возвращает (gcd, x, y), такие что ax + by = gcd.
        """
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = MathBridge.extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

    @staticmethod
    def inverse(a: int, m: int) -> int:
        """
        Вычисляет модульную инверсию.
        """
        try:
            return int(mod_inverse(a, m))
        except ValueError:
            raise SolverError(f"Инверсия для {a} mod {m} не существует.")

    @staticmethod
    def solve_linear_congruence(a: int, b: int, m: int) -> int:
        """
        Решает линейное сравнение ax ≡ b (mod m).
        """
        g, x, _ = MathBridge.extended_gcd(a, m)
        if b % g != 0:
            raise SolverError("Линейное сравнение не имеет решений.")
        return (x * (b // g)) % (m // g)