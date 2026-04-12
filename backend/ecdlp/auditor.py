"""
Модуль аудита криптографической стойкости кривых.
Проверяет применимость специфических атак (Smart, Pohlig-Hellman).
"""

from typing import Dict, Any, List
from fastecdsa.curve import Curve
from .utils.math_bridge import MathBridge
from .exceptions import AuditFailedError

class ECDLPAuditor:
    """
    Выполняет анализ параметров кривой для выбора стратегии решения ECDLP.
    """

    SMOOTHNESS_THRESHOLD = 2**40

    @staticmethod
    def analyze(curve: Curve) -> Dict[str, Any]:
        """
        Проводит аудит параметров кривой.
        
        :param curve: Объект кривой fastecdsa.
        :return: Словарь с результатами анализа и рекомендациями.
        """
        p = curve.p
        n = curve.q
        
        report = {
            "p": p,
            "n": n,
            "is_anomalous": False,
            "is_smooth": False,
            "factors": {},
            "recommended_solver": "PollardRhoSolver"
        }

        if p == n:
            report["is_anomalous"] = True
            report["recommended_solver"] = "SmartAttackSolver"
            return report

        try:
            factors = MathBridge.get_factorization(n)
            report["factors"] = factors
            
            max_factor = max(factor**factors[factor] for factor in factors)
            if max_factor < min(n, ECDLPAuditor.SMOOTHNESS_THRESHOLD):
                report["is_smooth"] = True
                report["recommended_solver"] = "PohligHellmanSolver"
        except Exception as e:
            report["is_smooth"] = False

        return report

    @staticmethod
    def check_feasibility(curve: Curve) -> None:
        """
        Проверяет, реально ли решить задачу для данной кривой.
        Выбрасывает исключение, если задача слишком сложна.
        """
        analysis = ECDLPAuditor.analyze(curve)
        
        if not analysis["is_anomalous"] and not analysis["is_smooth"]:
            if curve.q > 2**128:
                raise AuditFailedError(
                    f"Кривая признана стойкой. Порядок n ≈ 2^{curve.q.bit_length()}. "
                    "Решение задачи стандартными методами невозможно за разумное время."
                )

    @staticmethod
    def get_vulnerabilities(curve: Curve) -> List[str]:
        """Возвращает список обнаруженных уязвимостей в текстовом виде."""
        analysis = ECDLPAuditor.analyze(curve)
        vulnerabilities = []
        
        if analysis["is_anomalous"]:
            vulnerabilities.append("Аномальная кривая (n=p): уязвима к атаке Смарта.")
        if analysis["is_smooth"]:
            vulnerabilities.append("Гладкий порядок группы: уязвима к атаке Похлига-Хеллмана.")
            
        return vulnerabilities