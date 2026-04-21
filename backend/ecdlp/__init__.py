import threading
from typing import Optional, Dict, Any

from fastecdsa.point import Point
from fastecdsa.curve import Curve

from .auditor import ECDLPAuditor
from .solvers.pollard_rho import PollardRhoSolver
from .solvers.pohlig_hellman import PohligHellmanSolver
from .solvers.smart_attack import SmartAttackSolver
from .utils.ecgen_loader import ECGenLoader
from .exceptions import (
    ECDLPError, 
    CalculationInterrupted, 
    SolverError, 
    InvalidCurveError, 
    AuditFailedError
)

__all__ = [
    'solve_ecdlp',
    'analyze_curve',
    'load_curve_from_params',
    'ECDLPError',
    'CalculationInterrupted'
]

def analyze_curve(curve: Curve) -> Dict[str, Any]:
    """Проводит криптоанализ кривой и возвращает отчет о применимости атак."""
    return ECDLPAuditor.analyze(curve)

def load_curve_from_params(params: Dict[str, Any]) -> tuple[Curve, Point]:
    """Создает объекты кривой и генератора из словаря параметров (формат ecgen)."""
    return ECGenLoader.create_curve_and_generator(params)

def solve_ecdlp(
    P: Point, 
    Q: Point, 
    curve: Curve, 
    cancel_token: Optional[threading.Event] = None
) -> int:
    """
    Автоматически выбирает и запускает наиболее эффективный метод решения ECDLP.
    
    :param P: Базовая точка (генератор).
    :param Q: Результат скалярного умножения (Q = xP).
    :param curve: Объект кривой fastecdsa.
    :param cancel_token: Токен для прерывания операции из другого потока.
    :return: Искомый скаляр x.
    :raises CalculationInterrupted: При получении сигнала отмены.
    :raises SolverError: Если решение не найдено.
    """

    if Q._is_identity: return 0

    analysis = ECDLPAuditor.analyze(curve)
    method = analysis["recommended_solver"]
    
    if method == "SmartAttackSolver":
        solver = SmartAttackSolver(cancel_token)
    elif method == "PohligHellmanSolver":
        solver = PohligHellmanSolver(cancel_token)
    else:
        solver = PollardRhoSolver(cancel_token)

    return solver.solve(P, Q, curve)