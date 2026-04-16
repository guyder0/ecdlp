import React, { useState } from 'react';
import { type CurveSummary, type CurveDetail } from '@/services/api';
import { type TaskState } from '@/hooks/useSolver';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle,
  CardFooter
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ChevronDown, ChevronUp, Activity } from 'lucide-react';
import { SolverPanel } from './SolverPanel';
import { DetailsPanel } from './DetailsPanel';

interface CurveCardProps {
  summary: CurveSummary;
  detail?: CurveDetail;
  task: TaskState;
  onFetchDetail: () => void;
  onSolve: (x: string) => void;
  onCancel: () => void;
}

export const CurveCard: React.FC<CurveCardProps> = ({
  summary,
  detail,
  task,
  onFetchDetail,
  onSolve,
  onCancel,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Определяем цвет и текст бейджа статуса
  const getStatusBadge = () => {
    switch (task.status) {
      case 'running':
        return <Badge variant="secondary" className="animate-pulse flex gap-1"><Activity className="w-3 h-3" /> Solving...</Badge>;
      case 'completed':
        return <Badge variant="default" className="bg-green-600">Completed</Badge>;
      case 'failed':
        return <Badge variant="destructive">Error</Badge>;
      case 'cancelled':
        return <Badge variant="outline">Cancelled</Badge>;
      default:
        return null;
    }
  };

  return (
    <Card className={`transition-all duration-300 ${isExpanded ? 'ring-2 ring-primary' : ''}`}>
      <CardHeader className="cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-xl font-bold">{summary.name}</CardTitle>
            <CardDescription className="text-xs font-mono uppercase mt-1">{summary.id}</CardDescription>
          </div>
          <div className="flex flex-col items-end gap-2">
            {getStatusBadge()}
            <Button variant="ghost" size="sm" className="p-0 h-6 w-6">
              {isExpanded ? <ChevronUp /> : <ChevronDown />}
            </Button>
          </div>
        </div>
        <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
          {summary.description}
        </p>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          <Tabs defaultValue="solver" className="w-full" onValueChange={(value) => {
            if (value === 'details') onFetchDetail();
          }}>
            <TabsList className="grid w-full grid-cols-2 mb-4">
              <TabsTrigger value="solver">Решатель</TabsTrigger>
              <TabsTrigger value="details">Параметры</TabsTrigger>
            </TabsList>

            <TabsContent value="solver" className="space-y-4">
              <SolverPanel 
                task={task} 
                curveOrder={detail?.q}
                onSolve={onSolve} 
                onCancel={onCancel} 
              />
            </TabsContent>

            <TabsContent value="details">
              <DetailsPanel detail={detail} />
            </TabsContent>
          </Tabs>
        </CardContent>
      )}

      {/* Если задача завершена, показываем краткий результат в футере, даже если карточка свернута */}
      {!isExpanded && task.status === 'completed' && (
        <CardFooter className="py-2 bg-muted/50 text-xs font-mono flex justify-between">
          <span>Result:</span>
          <span className="text-green-600 truncate ml-2">{task.result}</span>
        </CardFooter>
      )}
    </Card>
  );
};