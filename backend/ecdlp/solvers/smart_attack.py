from typing import Tuple, Optional
from fastecdsa.point import Point
from fastecdsa.curve import Curve
from .base import BaseSolver
from ..utils.math_bridge import MathBridge
from ..exceptions import SolverError

class SmartAttackSolver(BaseSolver):
    """
    Реализация атаки Смарта для аномальных кривых (n == p).
    Сложность: O(log p).
    """

    def _lift_point(self, pt: Point, curve: Curve, p2: int) -> Tuple[int, int]:
        x, y = pt.x, pt.y
        a, b = curve.a, curve.b
        
        target = (x**3 + a*x + b) % p2
        k = ((target - pow(y, 2, p2)) // curve.p)
        k = (k * MathBridge.inverse(2 * y, curve.p)) % curve.p
        
        return x, (y + k * curve.p) % p2

    def _add_p2(self, p1: Tuple[int, int], p2: Tuple[int, int], a: int, mod: int) -> Tuple[int, int]:
        if p1 is None: return p2
        if p2 is None: return p1
        
        x1, y1 = p1
        x2, y2 = p2
        
        if x1 == x2 and y1 == y2:
            num = (3 * x1 * x1 + a) % mod
            den = MathBridge.inverse(2 * y1, mod)
        else:
            num = (y2 - y1) % mod
            den = MathBridge.inverse(x2 - x1, mod)
            
        m = (num * den) % mod
        x3 = (m * m - x1 - x2) % mod
        y3 = (m * (x1 - x3) - y1) % mod
        return x3, y3

    def _mul_p2(self, pt: Tuple[int, int], scalar: int, a: int, mod: int) -> Tuple[int, int]:
        res = None
        base = pt
        while scalar:
            self._check_interruption()
            if scalar & 1:
                res = self._add_p2(res, base, a, mod)
            base = self._add_p2(base, base, a, mod)
            scalar >>= 1
        return res

    def _weight(self, pt: Point, curve: Curve, p2: int) -> int:
        p = curve.p
        pt_lifted = self._lift_point(pt, curve, p2)
        pt_p = self._mul_p2(pt_lifted, p, curve.a, p2)
        
        # x/y в формальной группе
        x_p, y_p = pt_p
        # u = -x/y mod p^2. Так как pt_p в ядре редукции, x_p/y_p кратно p.
        u = (p2 - x_p) * MathBridge.inverse(y_p, p2) % p2
        return (u // p) % p

    def solve(self, P: Point, Q: Point, curve: Curve) -> int:
        self._check_interruption()
        
        if curve.p != curve.q:
            raise SolverError("Атака Смарта применима только для аномальных кривых (n=p)")

        p2 = curve.p ** 2
        
        wP = self._weight(P, curve, p2)
        wQ = self._weight(Q, curve, p2)
        
        if wP == 0:
            raise SolverError("Невозможно вычислить логарифм: вес базовой точки равен 0")
            
        return (wQ * MathBridge.inverse(wP, curve.p)) % curve.p