import React from 'react';
import { type CurveDetail } from '@/services/api';
import { Skeleton } from '@/components/ui/skeleton';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Copy, Check } from 'lucide-react';

interface DetailsPanelProps {
  detail: CurveDetail;
}

export const DetailsPanel: React.FC<DetailsPanelProps> = ({ detail }) => {
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null);

  if (!detail) {
    return (
      <div className="space-y-4 pt-2">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-10 w-full" />
          </div>
        ))}
      </div>
    );
  }

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Вспомогательный компонент для строки параметра
  const ParamRow = ({ label, value, id }: { label: string; value: string; id: string }) => (
    <div className="space-y-1.5 mb-4">
      <div className="flex justify-between items-center">
        <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {label}
        </Label>
        <Button 
          variant="ghost" 
          size="sm" 
          className="h-6 w-6 p-0" 
          onClick={() => copyToClipboard(value, id)}
        >
          {copiedKey === id ? <Check className="w-3 h-3 text-green-600" /> : <Copy className="w-3 h-3" />}
        </Button>
      </div>
      <div className="p-2 rounded bg-muted/50 border font-mono text-[11px] break-all leading-relaxed">
        {value}
      </div>
    </div>
  );

  return (
    <ScrollArea className="h-[350px] pr-4 pt-2">
      <div className="space-y-1">
        <ParamRow label="Порядок поля (p)" value={detail.p} id="p" />
        <ParamRow label="Коэффициент кривой (a)" value={detail.a} id="a" />
        <ParamRow label="Коэффициент кривой (b)" value={detail.b} id="b" />
        <ParamRow label="Генератор G (x)" value={detail.gx} id="gx" />
        <ParamRow label="Генератор G (y)" value={detail.gy} id="gy" />
        <ParamRow label="Порядок генератора (q)" value={detail.q} id="q" />
      </div>
    </ScrollArea>
  );
};