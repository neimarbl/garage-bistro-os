// frontend/src/pages/ResumoConta.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useAtendimento } from '../context/AtendimentoContext';

export const ResumoConta = ({ onVoltar }) => {
    const { mesaAtiva, comandaAtiva } = useAtendimento();
    const [extrato, setExtrato] = useState(null);
    const [carregando, setCarregando] = useState(true);
    const [solicitandoMaquininha, setSolicitandoMaquininha] = useState(false);
    const [coverArtistico, setCoverArtistico] = useState(10.0); // Valor padrão configurado na garagem

    // 1. Busca os dados de agregação financeira e rateio B2B híbrido do backend
    const carregarExtrato = useCallback(async () => {
        setCarregando(true);
        try {
            // Se houver uma comanda ativa, busca por ela, caso contrário usa a mesa
            const idBusca = comandaAtiva || mesaAtiva;
            const response = await fetch(`${import.meta.env.VITE_API_URL}{idBusca}/extrato?cover=${coverArtistico}`);
            if (!response.ok) throw new Error("Falha ao computar extrato");
            const data = await response.json();
            setExtrato(data);
        } catch (error) {
            console.error("Erro na API financeira:", error);
        } finally {
            setCarregando(false);
        }
    }, [comandaAtiva, mesaAtiva, coverArtistico]);

    useEffect(() => {
        carregarExtrato();
    }, [carregarExtrato]);

    // 2. Dispara notificação WebSocket via API para chamar o garçom com a maquininha PagBank
    const handleChamarMaquininha = async (metodo) => {
        if (!comandaAtiva) return;
        setSolicitandoMaquininha(true);
        try {
            const payload = {
                comanda_id: comandaAtiva,
                valor: extrato?.responsabilidade_cliente || extrato?.saldo_restante || 0,
                metodo: metodo // "credito" ou "debito"
            };
            
            const response = await fetch('http://192.168.111', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert(`💳 Alerta enviado ao Caixa! Levar maquininha para receber R$ ${payload.valor.toFixed(2)}.`);
            }
        } catch (error) {
            console.error("Erro ao chamar maquininha:", error);
        } finally {
            setSolicitandoMaquininha(false);
        }
    };

    if (carregando) {
        return (
            <div className="flex h-screen items-center justify-center bg-zinc-900 text-white">
                <div className="animate-spin text-4xl">🔄</div>
                <span className="ml-2">Computando rateios e agregados...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-900 pb-36 text-white p-4">
            {/* Header Fixo de Navegação */}
            <header className="mb-6 flex items-center gap-3 border-b border-zinc-800 pb-4">
                <button onClick={onVoltar} className="rounded-lg bg-zinc-800 p-2 hover:bg-zinc-700 active:scale-95">
                    ⬅️
                </button>
                <div>
                    <h1 className="text-xl font-bold">Fechamento de Conta</h1>
                    <p className="text-xs text-zinc-400">Mesa {mesaAtiva} {comandaAtiva && `• Comanda PVC ${comandaAtiva}`}</p>
                </div>
            </header>

            {/* Controle de Parâmetro Operacional: Cover Artístico do Dia */}
            <div className="mb-6 rounded-xl bg-zinc-950 p-4 border border-zinc-800 flex items-center justify-between">
                <div>
                    <h3 className="font-bold text-sm text-zinc-300">Cover Artístico (Música ao Vivo)</h3>
                    <p className="text-xs text-zinc-500">Aplica taxa fixa se houver atração na garagem</p>
                </div>
                <select 
                    value={coverArtistico} 
                    onChange={(e) => setCoverArtistico(parseFloat(e.target.value))}
                    className="bg-zinc-900 text-sm font-bold text-emerald-400 border border-zinc-800 rounded-lg p-2 focus:outline-none"
                >
                    <option value={0.0}>Sem Cover</option>
                    <option value={5.0}>R$ 5,00</option>
                    <option value={10.0}>R$ 10,00</option>
                </select>
            </div>

            {/* CARD MASTER: Painel de Resultados do Strategy Pattern Financeiro */}
            <main className="space-y-4">
                <div className="rounded-2xl bg-zinc-950 border border-zinc-800 p-6 shadow-2xl">
                    <h2 className="text-xs uppercase font-black tracking-widest text-zinc-500 mb-4">Demonstrativo Financeiro</h2>
                    
                    <div className="space-y-3 border-b border-zinc-900 pb-4">
                        <div className="flex justify-between text-sm">
                            <span className="text-zinc-400">Subtotal Consumo</span>
                            <span className="font-medium text-zinc-200">R$ {extrato?.subtotal_consumo?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-zinc-400">Taxa de Serviço (10% Opcional)</span>
                            <span className="font-medium text-zinc-200">R$ {extrato?.taxa_servico_10?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-zinc-400">Cover Artístico</span>
                            <span className="font-medium text-zinc-200">R$ {extrato?.cover_artistico?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-zinc-900 pt-3">
                            <span className="font-bold text-zinc-300">Total Geral Acumulado</span>
                            <span className="font-black text-white">R$ {extrato?.total_geral?.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm text-emerald-500 font-semibold">
                            <span>Total já Pago/Abatido</span>
                            <span>- R$ {extrato?.total_pago?.toFixed(2)}</span>
                        </div>
                    </div>

                    {/* Bloco Dinâmico de Divisão B2B Corporativa */}
                    <div className="mt-4 pt-2">
                        <div className="flex items-center gap-2 mb-3">
                            <span className="text-xs font-black bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded">
                                {extrato?.regra_evento_aplicada || "Conta Individual Padrão"}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mt-2">
                            <div className="bg-zinc-900/60 p-3 rounded-xl border border-zinc-900">
                                <p className="text-[10px] uppercase font-bold text-zinc-500">Custo Empresa</p>
                                <p className="text-lg font-black text-blue-400">R$ {extrato?.responsabilidade_empresa?.toFixed(2) || "0.00"}</p>
                            </div>
                            <div className="bg-zinc-900/60 p-3 rounded-xl border border-zinc-900">
                                <p className="text-[10px] uppercase font-bold text-zinc-500">Saldo a Pagar Cliente</p>
                                <p className="text-lg font-black text-emerald-400">R$ {extrato?.responsabilidade_cliente?.toFixed(2) || extrato?.saldo_restante?.toFixed(2)}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            {/* Rodapé Operacional Integrado com Acionamento de Hardware LAN */}
            {comandaAtiva && (extrato?.responsabilidade_cliente > 0 || extrato?.saldo_restante > 0) && (
                <footer className="fixed bottom-0 inset-x-0 border-t border-zinc-800 bg-zinc-950/90 p-4 backdrop-blur shadow-2xl">
                    <div className="mx-auto max-w-md">
                        <p className="text-center text-xs font-bold text-zinc-400 mb-3">Chamar Maquininha PagBank na Mesa</p>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                onClick={() => handleChamarMaquininha('debito')}
                                disabled={solicitandoMaquininha}
                                className="rounded-xl bg-zinc-800 border border-zinc-700 py-3.5 text-center text-sm font-black uppercase tracking-wider text-zinc-200 transition-all hover:bg-zinc-700 active:scale-95 disabled:opacity-50"
                            >
                                💳 Débito
                            </button>
                            <button
                                onClick={() => handleChamarMaquininha('credito')}
                                disabled={solicitandoMaquininha}
                                className="rounded-xl bg-emerald-500 py-3.5 text-center text-sm font-black uppercase tracking-wider text-zinc-900 transition-all hover:bg-emerald-400 active:scale-95 disabled:opacity-50 shadow-xl shadow-emerald-500/10"
                            >
                                💳 Crédito
                            </button>
                        </div>
                    </div>
                </footer>
            )}
        </div>
    );
};
