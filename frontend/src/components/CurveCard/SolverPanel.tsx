import React, { useState } from 'react';
import { type TaskState } from '@/hooks/useSolver';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Loader2, Play, Square, Copy, CheckCircle2 } from 'lucide-react';

import { toHex, toBigInt } from '@/lib/utils';

interface SolverPanelProps {
  task: TaskState;
  curveOrder: string;
  onSolve: (x: string) => void;
  onCancel: () => void;
}

export const SolverPanel: React.FC<SolverPanelProps> = ({
  task,
  curveOrder,
  onSolve,
  onCancel,
}) => {
  const [xValue, setXValue] = useState<string>("0x0");
  const [sValue, setSValue] = useState<number>(0)
  const [copied, setCopied] = useState(false);

  const handleInputChange = (e:any) => {
    let val = e.target.value.toLowerCase();
    if (val.length < 2) { setXValue("0x"); }
    else if (!val.startsWith("0x")) { val = "0x" + val; }
    else {
      const prefix = "0x";
      const hexPart = val.slice(2).replace(/[^0-9a-f]/g, '');
      setXValue(prefix + hexPart);
    }
  }

  // Обработка слайдера: вычисляем % от q
  const handleSliderChange = (percent: number[]) => {
    setSValue(percent[0])
    try {
      const q = toBigInt(curveOrder);
      const newValue = (q * BigInt(percent[0])) / 100n;
      setXValue(toHex(newValue));
    } catch (e) {
      console.error("BigInt conversion error", e);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isRunning = task.status === 'running';

  return (
    <div className="space-y-6 pt-2">
      {/* Поле ввода ключа */}
      <div className="space-y-2">
        <Label htmlFor="x-value">Секретный ключ (x)</Label>
        <div className="flex gap-2">
          <Input
            id="x-value"
            value={xValue}
            onChange={handleInputChange}
            disabled={isRunning || !curveOrder}
            placeholder="Введите число..."
            className="font-mono"
          />
        </div>
      </div>

      {/* Слайдер (доступен только если загружены параметры кривой, чтобы знать q) */}
      <div className="space-y-4">
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0</span>
          <span>Грубый выбор (0-100%)</span>
          <span>q</span>
        </div>
        <Slider
          disabled={isRunning || !curveOrder}
          value={[sValue]}
          min={0}
          max={100}
          step={1}
          onValueChange={handleSliderChange}
        />
      </div>

      {/* Кнопки управления */}
      <div className="flex gap-2 pt-2">
        {isRunning ? (
          <Button 
            variant="destructive" 
            className="w-full" 
            onClick={onCancel}
          >
            <Square className="w-4 h-4 mr-2 fill-current" /> Отменить задачу
          </Button>
        ) : (
          <Button 
            variant="default" 
            className="w-full" 
            onClick={() => onSolve(xValue)}
            disabled={!xValue}
          >
            <Play className="w-4 h-4 mr-2 fill-current" /> Запустить решение
          </Button>
        )}
      </div>

      {/* Результат */}
      {task.status === 'completed' && task.result && (
        <div className="mt-4 p-4 rounded-lg bg-green-50 border border-green-200 dark:bg-green-900/20 dark:border-green-900">
          <Label className="text-green-800 dark:text-green-300">Результат найден:</Label>
          <div className="flex items-center gap-2 mt-1">
            <code className="flex-1 block p-2 bg-white dark:bg-black/20 rounded border font-mono text-sm break-all">
              {task.result}
            </code>
            <Button size="icon" variant="ghost" onClick={() => copyToClipboard(task.result!)}>
              {copied ? <CheckCircle2 className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
            </Button>
          </div>
        </div>
      )}

      {/* Ошибка */}
      {task.status === 'failed' && (
        <div className="mt-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
          <strong>Ошибка:</strong> {task.error || "Неизвестная ошибка сервера"}
        </div>
      )}

      {/* Индикатор работы */}
      {isRunning && (
        <div className="flex items-center justify-center gap-3 text-sm text-muted-foreground animate-pulse">
          <Loader2 className="w-4 h-4 animate-spin" />
          Вычисляем дискретный логарифм...
        </div>
      )}
    </div>
  );
};