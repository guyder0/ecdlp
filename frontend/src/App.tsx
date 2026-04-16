import React, { useEffect, useState } from 'react';
import { CurveGrid } from './components/CurveGrid';
import { socket } from './services/socket';
import { Badge } from '@/components/ui/badge';
import { Cpu, Wifi, WifiOff } from 'lucide-react';

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
    };
  }, []);

  return (
    <div className="bg-background font-sans antialiased">
      {/* Навигационная панель / Хедер */}
      <header className="top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center justify-between">
          <div className="p-8 flex items-center gap-2 font-bold text-xl">
            <Cpu className="w-6 h-6 text-primary" />
            <span>ECDLP Solver</span>
          </div>

          <div className="p-8 flex items-center gap-4">
            {/* Индикатор статуса WebSocket */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50 gap-1">
                  <Wifi className="w-3 h-3" /> Connected
                </Badge>
              ) : (
                <Badge variant="outline" className="text-destructive border-destructive/20 bg-destructive/10 gap-1">
                  <WifiOff className="w-3 h-3" /> Disconnected
                </Badge>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="p-8">
        <div className="flex flex-col gap-2 mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight lg:text-4xl">
            Elliptic Curve Discrete Logarithm Problem
          </h1>
          <p className="text-muted-foreground max-w-[700px]">
            Выберите эллиптическую кривую, задайте секретный ключ и запустите процесс решения дискретного логарифма в реальном времени через распределенные задачи.
          </p>
        </div>

        {/* Сетка карточек */}
        <CurveGrid />
      </main>

      {/* Футер */}
      <footer className="border-t p-6 md:py-0">
        <div className="flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            <p>Web-development with FastAPI, Socket.io and Shadcn UI. </p>
            <p>ECDLP backend: fastecdsa, sympy </p>
            <p>Автор: Володченков Никита, А-05-22</p>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;