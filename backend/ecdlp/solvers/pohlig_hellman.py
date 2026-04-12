from fastecdsa.point import Point
from fastecdsa.curve import Curve
from .base import BaseSolver
from .pollard_rho import PollardRhoSolver
from ..utils.math_bridge import MathBridge
from ..exceptions import SolverError

class PohligHellmanSolver(BaseSolver):
    """
    Реализация алгоритма Похлига-Хеллмана.
    Разбивает задачу на подгруппы простых порядков.
    """

    def solve(self, P: Point, Q: Point, curve: Curve) -> int:
        n = curve.q
        factors = MathBridge.get_factorization(n)
        
        remainders = []
        moduli = []
        
        sub_solver = PollardRhoSolver(self._cancel_token)

        for p, e in factors.items():
            self._check_interruption()
            pe = p**e
            
            # Решение x mod p^e
            x_pe = 0
            # Накопленный p^i
            p_pow = 1
            
            # Базовая точка для подгруппы порядка p
            # P0 = [n/p]P
            P0 = P * (n // p)

            # sQ = Q - z0P - z1pP - ...
            sQ = Q
            zi = 0
            
            for _ in range(e):
                self._check_interruption()
                
                # Текущая точка для логарифмирования в подгруппе порядка p
                # Q_(i+1) = [n / p^(i+1)] * sQ
                exponent = n // (p_pow * p)
                sQ = sQ - zi * (p_pow // p) * P
                Qi = sQ * exponent
                
                # Решаем zi = log_{P0}(Qi) через Ро-алгоритм
                # x = z0 + z1*p + z2*p^2 + ...
                zi = sub_solver.solve(P0, Qi, curve, subgroup_order=p)
                
                x_pe += zi * p_pow
                p_pow *= p
                
            remainders.append(x_pe)
            moduli.append(pe)
            
        return MathBridge.solve_crt(remainders, moduli)