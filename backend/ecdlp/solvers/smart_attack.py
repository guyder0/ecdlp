from typing import Tuple, Optional
from fastecdsa.point import Point
from fastecdsa.curve import Curve
from .base import BaseSolver
from ..exceptions import SolverError

class SmartAttackSolver(BaseSolver):
    """
    Реализация атаки Смарта (SSAS) для аномальных кривых (#E(Fp) == p).
    """

    def _lift_point(self, pt: Point, curve: Curve, p2: int) -> Tuple[int, int, int]:
        """Поднятие точки в Z_{p^2} с использованием уточнения Гензеля."""
        x, y = pt.x, pt.y
        a, b = curve.a, curve.b
        p = curve.p

        # Проверяем y^2 = x^3 + ax + b mod p^2
        target = (pow(x, 3, p2) + a * x + b) % p2
        current_y_sq = pow(y, 2, p2)
        
        if (target - current_y_sq) % p == 0:
            # Находим дельту: (y + delta*p)^2 = target mod p^2
            # y^2 + 2*y*delta*p = target mod p^2
            # delta = (target - y^2) / (2*y*p) mod p
            diff = (target - current_y_sq) // p
            delta = (diff * pow(2 * y, -1, p)) % p
            new_y = (y + delta * p) % p2
            return (x, new_y, 1)
        
        raise SolverError("Не удалось поднять точку на кривую")

    def _add_homo(self, p1: Optional[Tuple], p2: Optional[Tuple], a: int, mod: int) -> Optional[Tuple]:
        """Сложение в стандартных проективных координатах (X:Y:Z) по модулю p^2."""
        if p1 is None: return p2
        if p2 is None: return p1
        
        x1, y1, z1 = p1
        x2, y2, z2 = p2

        # Упрощенные формулы сложения для проективных координат
        u1 = (y2 * z1) % mod
        u2 = (y1 * z2) % mod
        v1 = (x2 * z1) % mod
        v2 = (x1 * z2) % mod

        if v1 == v2:
            if u1 != u2: return None # Бесконечность
            # Удвоение
            w = (3 * x1 * x1 + a * z1 * z1) % mod
            s = (y1 * z1) % mod
            b_val = (x1 * y1 * s) % mod
            h = (w * w - 8 * b_val) % mod
            x3 = (2 * h * s) % mod
            y3 = (w * (4 * b_val - h) - 8 * y1 * y1 * s * s) % mod
            z3 = (8 * s * s * s) % mod
            return (x3, y3, z3)
        else:
            # Сложение
            u = (u1 - u2) % mod
            v = (v1 - v2) % mod
            v2 = (v * v) % mod
            v3 = (v2 * v) % mod
            v2_x1 = (v2 * x1 * z2) % mod
            
            a_res = (u * u * z1 * z2 - v3 - 2 * v2_x1) % mod
            x3 = (v * a_res) % mod
            y3 = (u * (v2_x1 - a_res) - v3 * y1 * z2) % mod
            z3 = (v3 * z1 * z2) % mod
            return (x3, y3, z3)

    def _mul_homo(self, pt: Tuple, scalar: int, a: int, mod: int) -> Optional[Tuple]:
        """Скалярное умножение (Double-and-Add) в проективных координатах."""
        res = None
        base = pt
        while scalar > 0:
            if scalar & 1:
                res = self._add_homo(res, base, a, mod)
            base = self._add_homo(base, base, a, mod)
            scalar >>= 1
        return res

    def _weight(self, pt: Point, curve: Curve) -> int:
        """Вычисляет логарифм точки через отображение в Fp."""
        p = curve.p
        p2 = p * p
        
        # 1. Lift
        P_tilde = self._lift_point(pt, curve, p2)
        
        # 2. Compute [p]P_tilde
        # Результат умножения на p в аномальной кривой всегда даст точку, 
        # где Z кратно p, а X, Y не кратны p.
        P_p = self._mul_homo(P_tilde, p, curve.a, p2)
        
        if P_p is None:
            return 0 # Теоретически не должно быть для Smart Attack
        
        x_p, y_p, z_p = P_p
        
        # 3. Эллиптический логарифм (формальный параметр z = -x/y)
        # В проективных координатах x/y = (X/Z) / (Y/Z) = X/Y
        # Нам нужно (X/Y mod p^2) // p
        
        # Y точно не кратно p, поэтому обратный элемент существует mod p^2
        inv_y = pow(y_p, -1, p2)
        val = (x_p * inv_y) % p2
        
        # Логарифм группы: L(P) = (x/y) / p mod p
        return (val // p) % p

    def solve(self, P: Point, Q: Point, curve: Curve) -> int:
        self._check_interruption()
        
        if curve.p != curve.q:
             raise SolverError("Кривая не аномальна (n != p)")

        p = curve.p
        
        wP = self._weight(P, curve)
        wQ = self._weight(Q, curve)
        
        if wP == 0:
            raise SolverError("Логарифм базовой точки P равен 0 (точка слишком малого порядка)")
            
        # k = wQ / wP mod p
        return (wQ * pow(wP, -1, p)) % p