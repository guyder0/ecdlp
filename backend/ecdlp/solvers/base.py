import threading
from abc import ABC, abstractmethod
from typing import Optional
from fastecdsa.point import Point
from fastecdsa.curve import Curve
from ..exceptions import CalculationInterrupted

class BaseSolver(ABC):
    """
    Абстрактный базовый класс для всех реализаций атак на ECDLP.
    
    Обеспечивает унифицированный интерфейс и встроенную поддержку 
    кооперативной многозадачности (прерывание по требованию).
    """

    def __init__(self, cancel_token: Optional[threading.Event] = None):
        """
        Инициализация решателя.

        :param cancel_token: Событие threading.Event. Если установлено (.set()), 
                             решатель прервет вычисления при следующей проверке.
        """
        self._cancel_token = cancel_token

    def _check_interruption(self) -> None:
        """
        Внутренний метод для проверки флага прерывания.
        Должен вызываться внутри итерационных циклов тяжелых алгоритмов.
        
        :raises CalculationInterrupted: если сигнал отмены был получен.
        """
        if self._cancel_token and self._cancel_token.is_set():
            raise CalculationInterrupted(
                f"Алгоритм {self.__class__.__name__} был прерван внешним сигналом."
            )

    @abstractmethod
    def solve(self, P: Point, Q: Point, curve: Curve) -> int:
        """
        Основной метод решения задачи дискретного логарифма: Q = [x]P.

        :param P: Базовая точка (генератор группы или подгруппы).
        :param Q: Точка, результат скалярного умножения.
        :param curve: Объект кривой fastecdsa с параметрами.
        :return: Скаляр (инженерное решение x).
        :raises SolverError: если решение не может быть найдено.
        :raises CalculationInterrupted: если процесс был прерван.
        """
        pass