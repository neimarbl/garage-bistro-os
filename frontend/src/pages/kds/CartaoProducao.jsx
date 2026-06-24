// frontend/src/pages/kds/CartaoProducao.jsx
import React, { useState, useEffect } from 'react';

export const CartaoProducao = ({ pedido, index, onAvancarStatus }) => {
    const [tempoDecorrido, setTempoDecorrido] = useState(0);

    // Cronômetro em tempo real para controle de SLA da cozinha
    useEffect(() => {
        const criadoEm = new Date(pedido.criado_em).getTime();
        const interval = setInterval(() => {
            const agora = new Date().getTime();
            setTempoDecorrido(Math.floor((agora - criadoEm) / 1000));
        }, 1000);

        return () => clearInterval(interval);
    }, [pedido.criado_em]);

    const formatarTempo = (segundos) => {
        const mins = Math.floor(segundos / 60);
        const segs = segundos % 60;
        return `${mins.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
    };

    // Alerta visual de atraso após 15 minutos (900 segundos)
    const isAtrasado = tempoDecorrido > 900;

    return (
        <div className={`flex flex-col justify-between rounded-2xl border bg-zinc-950 p-4 shadow-xl transition-all ${
            isAtrasado ? 'border-rose-600 ring-2 ring-rose-600/20' : 'border-zinc-800'
        }`}>
            {/* Cabeçalho do Cartão */}
            <div>
                <div className="flex items-center justify-between border-b border-zinc-900 pb-2">
                    <div>
                        <span className="text-2xl font-black text-white">Mesa {pedido.mesa_id}</span>
                        <p className="text-[10px] text-zinc-500 font-bold uppercase mt-0.5">Comanda #{pedido.comanda_id}</p>
                    </div>
                    <div className={`rounded-lg px-2.5 py-1 text-xs font-black font-mono ${
                        isAtrasado ? 'bg-rose-500 text-zinc-950 animate-pulse' : 'bg-zinc-900 text-emerald-400'
                    }`}>
                        ⏱️ {formatarTempo(tempoDecorrido)}
                    </div>
                </div>

                {/* Listagem de Itens do Pedido */}
                <ul className="mt-3 space-y-2.5">
                    {pedido.itens.map((item) => (
                        <li key={item.id} className="border-b border-zinc-900/40 pb-2">
                            <div className="flex items-start gap-2">
                                <span className="text-lg font-black text-emerald-400 bg-emerald-500/10 px-2 rounded-md">
                                    {item.quantidade}x
                                </span>
                                <span className="font-bold text-zinc-200 text-sm">{item.produto_nome}</span>
                            </div>
                            {item.observacao && (
                                <p className="ml-9 mt-0.5 text-xs font-black text-rose-400 bg-rose-950/20 border border-rose-950/40 px-2 py-0.5 rounded-md w-fit">
                                    ⚠️ {item.observacao}
                                </p>
                            )}
                        </li>
                    ))}
                </ul>
            </div>

            {/* Rodapé Operacional com Atalho do Teclado USB */}
            <div className="mt-4 pt-3 border-t border-zinc-900 flex items-center justify-between">
                <span className="text-[10px] uppercase font-black text-zinc-500 tracking-wider">
                    Posição no Grid: <b className="text-zinc-300 font-mono bg-zinc-900 px-1.5 py-0.5 rounded text-xs">#{index + 1}</b>
                </span>
                <button
                    onClick={() => onAvancarStatus(pedido.id)}
                    className={`rounded-lg px-3 py-1.5 text-xs font-black uppercase tracking-wider transition-all active:scale-95 ${
                        pedido.status === 'PENDENTE'
                            ? 'bg-amber-500 text-zinc-950 hover:bg-amber-400'
                            : 'bg-emerald-500 text-zinc-950 hover:bg-emerald-400'
                    }`}
                >
                    {pedido.status === 'PENDENTE' ? '▶️ Preparar' : '✅ Despachar'}
                </button>
            </div>
        </div>
    );
};
