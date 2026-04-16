import { useState, useEffect, useCallback } from 'react';
import { curvesApi, type CurveSummary, type CurveDetail } from '@/services/api';

export const useCurves = () => {
  const [curves, setCurves] = useState<CurveSummary[]>([]);
  const [details, setDetails] = useState<Record<string, CurveDetail>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Загрузка общего списка при монтировании
  useEffect(() => {
    const loadCurves = async () => {
      try {
        setIsLoading(true);
        const data = await curvesApi.listCurves();
        setCurves(data);
      } catch (err) {
        setError('Не удалось загрузить список кривых');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadCurves();
  }, []);

  // 2. Функция для подгрузки деталей конкретной кривой (с кэшированием)
  const fetchCurveDetail = useCallback(async (curveId: string) => {
    // Если данные уже есть в кэше, ничего не делаем
    if (details[curveId]) return;

    try {
      const detail = await curvesApi.getCurve(curveId);
      setDetails((prev) => ({
        ...prev,
        [curveId]: detail,
      }));
    } catch (err) {
      console.error(`Ошибка при загрузке деталей кривой ${curveId}:`, err);
    }
  }, [details]);

  return {
    curves,          // Список всех кривых (id, name, desc)
    details,         // Объект с деталями: details['secp256k1']
    isLoading,       // Состояние первой загрузки
    error,           // Ошибка загрузки списка
    fetchCurveDetail // Функция для карточки
  };
};