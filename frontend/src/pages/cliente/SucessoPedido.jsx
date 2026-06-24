// frontend/src/pages/cliente/SucessoPedido.jsx
import React, { useEffect, useState } from 'react';
import { useAtendimento } from '../../context/AtendimentoContext';
import { useSocket } from '../../context/SocketContext';

export const SucessoPedido = ({ onNovoPedido }) => {
    const { mesaAtiva, comandaAtiva } = useAtendimento();
    const { notificacoes } = useSocket();
    const [statusPreparo, setStatusPreparo] = useState('Enviado'); // Enviado, Em Preparo, Pronto!

    // Intercepta atualizações do KDS via WebSocket para atualizar o progresso do prato na tela do cliente
    useEffect(() => {
        if (notificacoes.length > 0) {
            const ultimoAlerta = notificacoes[0];

            // Verifica se o alerta de avanço de estágio pertence à comanda/mesa deste cliente
            if (ultimoAlerta.comanda_id === comandaAtiva || ultimoAlerta.mesa_id === mesaAtiva) {
                if (ultimoAlerta.evento === "status_preparo_alterado") {
                    setStatusPreparo(ultimoAlerta.novo_status); // ex: "Em Preparo" ou "Pronto!"
                }
            }
        }
    }, [notificacoes, comandaAtiva, mesaAtiva]);

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-6 text-white">
            <div className="w-full max-w-sm rounded-2xl bg-zinc-900 border border-zinc-800 p-6 text-center shadow-2xl space-y-6">
                
                {/* Ícone Animado de Sucesso */}
                <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-emerald-500/10 text-4xl text-emerald-400 border border-emerald-500/20 animate-pulse">
                    🔥
                </div>

                {/* Bloco de Mensagem */}
                <div className="space-y-2">
                    <h2 className="text-2xl font-black tracking-tight text-zinc-100">Pedido na Grelha!</h2>
                    <p className="text-xs text-zinc-400 px-4">
                        O pedido da **Mesa {mesaAtiva}** (Comanda PVC #{comandaAtiva}) foi enviado direto para as telas da cozinha e do bar.
                    </p>
                </div>

                {/* Esteira de Status Real-Time (Alimentada pelo WebSocket do KDS) */}
                <div className="rounded-xl bg-zinc-950 p-4 border border-zinc-900 text-left space-y-3">
                    <div className="flex items-center justify-between text-xs font-bold text-zinc-500 uppercase tracking-wider border-b border-zinc-900 pb-2">
                        <span>Acompanhar Preparo</span>
                        <span className="text-emerald-400 animate-pulse">● Ao Vivo</span>
                    </div>
                    
                    <div className="flex items-center gap-3 pt-1">
                        <div className="h-2 w-2 rounded-full bg-emerald-500"></div>
                        <p className="text-sm font-medium text-zinc-300">
                            Status Atual: <span className="font-black text-white bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800">{statusPreparo}</span>
                        </p>
                    </div>

                    {statusPreparo === 'Pronto!' && (
                        <div className="mt-2 text-[11px] font-bold text-emerald-400 bg-emerald-950/40 border border-emerald-900/60 p-2 rounded-lg animate-bounce text-center">
                            🚀 Seu prato está saindo! O garçom já vai levar até você.
                        </div>
                    )}
                </div>

                {/* Botão de Retorno Seguro */}
                <div className="pt-2">
                    <button
                        onClick={onNovoPedido}
                        className="w-full rounded-xl bg-zinc-800 py-3.5 text-xs font-black uppercase tracking-widest border border-zinc-700 text-zinc-200 transition-all hover:bg-zinc-700 active:scale-95"
                    >
                        ➕ Pedir Mais Itens
                    </button>
                    <p className="text-[10px] text-zinc-500 font-medium mt-3">
                        Não feche esta página caso queira continuar acompanhando o KDS.
                    </p>
                </div>

            </div>
        </div>
    );
};
