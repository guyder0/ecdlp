import React from 'react';
import { useCurves } from '@/hooks/useCurves';
import { useSolver } from '@/hooks/useSolver';
import { CurveCard } from './CurveCard';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

export const CurveGrid: React.FC = () => {
  const { curves, details, isLoading, error, fetchCurveDetail } = useCurves();
  const { tasks, solve, cancel } = useSolver();

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Skeleton key={i} className="h-[300px] w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Ошибка</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {curves.map((curve) => (
        <CurveCard
          key={curve.id}
          summary={curve}
          detail={details[curve.id]} // Может быть undefined, если еще не загрузили
          task={tasks[curve.id] || { taskId: null, status: 'idle' }}
          onClick={() => fetchCurveDetail(curve.id)}
          onSolve={(x) => solve(curve.id, x)}
          onCancel={() => cancel(curve.id)}
        />
      ))}
    </div>
  );
};