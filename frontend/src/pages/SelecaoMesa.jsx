// frontend/src/pages/SelecaoMesa.jsx
import React, { useState, useEffect } from 'react';
import { useSocket } from '../context/SocketContext';

// Cores semânticas mapeadas para os estados da regra de negócio
const ESTADOS_MESA = {
    livre: { bg: 'bg-emerald-500 hover:bg-emerald-600', texto: 'Livre', icone: '🟢' },
    ocupada: { bg: 'bg-amber-500 hover:bg-amber-600', texto: 'Em Uso', icone: '🟠' },
    reservada: { bg: 'bg-blue-500 hover:bg-blue-600', texto: 'Reservada', icone: '🔵' }
};

export const SelecaoMesa = ({ onSelecionarMesa }) => {
    const { notificacoes, online, limparNotificacao } = useSocket();
    const [mesas, setMesas] = useState([]);
    const [carregando, setCarregando] = useState(true);

    // 1. Busca o status inicial das mesas na API local da LAN (Porta 8080)
    useEffect(() => {
        const buscarMesas = async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_API_URL}/atendimento/mesas`);
                const data = await response.json();
                setMesas(data);
            } catch (error) {
                console.error("Erro ao conectar à API de mesas:", error);
            } finally {
                setCarregando(false);
            }
        };
        buscarMesas();
    }, []);

    // 2. Intercepta alertas do WebSocket em tempo real para pintar chamados de ajuda na tela
    useEffect(() => {
        if (notificacoes.length > 0) {
            const ultimaNotificacao = notificacoes[0];
            
            // Se for um chamado de atendimento, atualiza o estado visual da mesa imediatamente
            if (ultimaNotificacao.evento === "novo_chamado") {
                setMesas((mesasAtuais) =>
                    mesasAtuais.map((m) =>
                        m.id === ultimaNotificacao.mesa_id 
                            ? { ...m, temChamadoAtivo: true, chamadoTipo: ultimaNotificacao.tipo } 
                            : m
                    )
                );
            }
        }
    }, [notificacoes]);

    if (carregando) {
        return (
            <div className="flex h-screen items-center justify-center bg-zinc-900 text-white">
                <div className="animate-spin text-4xl">🔄</div>
                <span className="ml-2 font-medium">Carregando layout do salão...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-900 p-4 text-white">
            {/* Header Operacional Integrado */}
            <header className="mb-6 flex items-center justify-between border-b border-zinc-800 pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Garage Bistrô</h1>
                    <p className="text-xs text-zinc-400">Painel do Garçom • Salão Dinâmico</p>
                </div>
                <div className="flex items-center gap-2 rounded-full bg-zinc-800 px-3 py-1.5 text-xs font-semibold">
                    <span className={`h-2.5 w-2.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
                    {online ? 'Wi-Fi 5G Online' : 'Sem Sinal'}
                </div>
            </header>

            {/* Central de Notificações Ativas (Pop-ups rápidos no topo do celular) */}
            {notificacoes.length > 0 && (
                <div className="mb-6 space-y-2">
                    {notificacoes.slice(0, 2).map((notif, index) => (
                        <div key={index} className="flex items-center justify-between rounded-lg bg-rose-950/80 border border-rose-800 p-3 text-sm text-rose-200 animate-bounce">
                            <div className="flex items-center gap-2">
                                <span>⚠️</span>
                                <p className="font-medium">{notif.alerta || `Chamado na Mesa ${notif.mesa_id}`}</p>
                            </div>
                            <button 
                                onClick={() => limparNotificacao(index)}
                                className="rounded bg-rose-900 px-2 py-1 text-xs font-bold hover:bg-rose-800"
                            >
                                Atender
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Grid de Mesas Otimizado para Toque em Smartphone Corporativo */}
            <main className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
                {mesas.map((mesa) => {
                    const statusConfig = ESTADOS_MESA[mesa.status] || ESTADOS_MESA.livre;
                    
                    return (
                        <button
                            key={mesa.id}
                            onClick={() => onSelecionarMesa(mesa.id)}
                            className={`relative flex h-28 flex-col justify-between rounded-xl p-4 text-left shadow-lg transition-all active:scale-95 ${statusConfig.bg} ${mesa.temChamadoAtivo ? 'ring-4 ring-rose-500 animate-pulse' : ''}`}
                        >
                            {/* Linha Superior Card */}
                            <div className="flex w-full items-center justify-between">
                                <span className="text-xs font-bold uppercase tracking-wider bg-black/20 px-2 py-0.5 rounded">
                                    {statusConfig.texto}
                                </span>
                                <span className="text-lg">{statusConfig.icone}</span>
                            </div>

                            {/* Identificador da Mesa (Fonte Ampla) */}
                            <div className="mt-2">
                                <span className="text-3xl font-black tracking-tight">Mesa {mesa.numero_identificador}</span>
                                {mesa.mesa_pai_id && (
                                    <p className="text-[10px] font-medium text-white/80 mt-0.5">🔗 Agrupada à Mesa {mesa.mesa_pai_id}</p>
                                )}
                            </div>

                            {/* Alerta de SOS local no Card */}
                            {mesa.temChamadoAtivo && (
                                <div className="absolute inset-x-0 bottom-0 bg-rose-600 text-center py-1 rounded-b-xl text-[10px] font-black uppercase tracking-widest animate-pulse">
                                    🚨 SOS: {mesa.chamadoTipo || 'Apoio'}
                                </div>
                            )}
                        </button>
                    );
                })}
            </main>
        </div>
    );
};
