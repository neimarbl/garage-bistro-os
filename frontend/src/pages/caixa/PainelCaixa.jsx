// frontend/src/pages/caixa/PainelCaixa.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../../context/SocketContext';

export const PainelCaixa = () => {
    const { notificacoes, online, limparNotificacao } = useSocket();
    const [alertasEstoque, setAlertasEstoque] = useState([]);
    const [resumoFinanceiro, setResumoFinanceiro] = useState({ total_dia: 0.0, total_pix: 0.0, total_cartao: 0.0, total_dinheiro: 0.0 });
    const [comandasAbertas, setComandasAbertas] = useState([]);
    const [carregando, setCarregando] = useState(true);

    // 1. Busca os dados de auditoria financeira e alertas críticos de validade/lote (Porta 8080)
    const carregarDadosPainel = useCallback(async () => {
        try {
            // Busca alertas de estoque crítico e validades (< 5 dias)
            const resEstoque = await fetch('http://192.168.111');
            const dataEstoque = await resEstoque.json();
            setAlertasEstoque(dataEstoque);

            // Busca agregação matemática do fechamento do dia
            const resFinanceiro = await fetch('http://192.168.111');
            const dataFinanceiro = await resFinanceiro.json();
            setResumoFinanceiro(dataFinanceiro);

            // Busca comandas ativas na LAN para monitoramento de mesa
            const resComandas = await fetch('http://192.168.111');
            const dataComandas = await resComandas.json();
            setComandasAbertas(dataComandas);
        } catch (error) {
            console.error("Falha ao sincronizar dados do caixa:", error);
        } finally {
            setCarregando(false);
        }
    }, []);

    useEffect(() => {
        carregarDadosPainel();
    }, [carregarDadosPainel]);

    // 2. Escuta eventos assíncronos de conciliação de PIX em tempo real via WebSocket
    useEffect(() => {
        if (notificacoes.length > 0) {
            const ultimoAlerta = notificacoes[0];
            // Se um pagamento fracionado for feito via PIX ou maquineta, recarrega o balanço do caixa
            if (ultimoAlerta.evento === "pix_recebido" || ultimoAlerta.evento === "chamar_maquininha") {
                carregarDadosPainel();
            }
        }
    }, [notificacoes, carregarDadosPainel]);

    if (carregando) {
        return (
            <div className="flex h-screen items-center justify-center bg-zinc-950 text-white">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-t-emerald-500 border-zinc-800"></div>
                <span className="ml-3 font-medium text-zinc-400">Conciliando balanços operacionais...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 p-6 text-white font-sans">
            {/* Header de Gestão de Turno */}
            <header className="mb-6 flex items-center justify-between border-b border-zinc-900 pb-4">
                <div>
                    <h1 className="text-2xl font-black tracking-tight text-zinc-100">Terminal do Caixa</h1>
                    <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Gestão Financeira e Conciliação LAN</p>
                </div>
                <div className="flex items-center gap-3">
                    <button 
                        onClick={carregarDadosPainel}
                        className="rounded-xl bg-zinc-900 px-4 py-2 text-xs font-black uppercase border border-zinc-800 hover:bg-zinc-800 transition-all"
                    >
                        🔄 Atualizar Auditoria
                    </button>
                    <div className="rounded-xl bg-zinc-900 px-4 py-2 text-xs font-semibold border border-zinc-800 flex items-center gap-2">
                        <span className={`h-2.5 w-2.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
                        {online ? 'Conectado ao Barramento' : 'Offline'}
                    </div>
                </div>
            </header>

            {/* Central de Pop-ups de Conciliação em Tempo Real (PIX / Cartão) */}
            {notificacoes.length > 0 && (
                <div className="mb-6 space-y-2 animate-fade-in-up">
                    {notificacoes.slice(0, 3).map((notif, index) => (
                        <div key={index} className="flex items-center justify-between rounded-xl bg-zinc-900 border border-emerald-900/60 p-4 shadow-xl">
                            <div className="flex items-center gap-3">
                                <span className="text-xl">💰</span>
                                <div>
                                    <p className="text-sm font-black text-emerald-400">{notif.alerta || 'Pagamento Notificado'}</p>
                                    <p className="text-[10px] text-zinc-500 uppercase font-bold mt-0.5">Origem: Comanda PVC #{notif.comanda_id}</p>
                                </div>
                            </div>
                            <button 
                                onClick={() => limparNotificacao(index)}
                                className="rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-black text-zinc-950 hover:bg-emerald-400 active:scale-95 transition-all"
                            >
                                Confirmar Recebimento
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Grid Principal Layout Desktop */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                
                {/* COLUNA 1: Faturamento Consolidado do Turno */}
                <section className="space-y-4 lg:col-span-2">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="rounded-2xl border border-zinc-900 bg-zinc-900/40 p-5 shadow-lg">
                            <p className="text-[10px] uppercase font-black text-zinc-500 tracking-wider">Faturamento Bruto Total</p>
                            <p className="text-3xl font-black text-white mt-1">R$ {resumoFinanceiro.total_dia?.toFixed(2)}</p>
                        </div>
                        <div className="rounded-2xl border border-zinc-900 bg-zinc-900/40 p-5 shadow-lg">
                            <p className="text-[10px] uppercase font-black text-zinc-500 tracking-wider">Arrecadação PIX</p>
                            <p className="text-3xl font-black text-emerald-400 mt-1">R$ {resumoFinanceiro.total_pix?.toFixed(2)}</p>
                        </div>
                        <div className="rounded-2xl border border-zinc-900 bg-zinc-900/40 p-5 shadow-lg">
                            <p className="text-[10px] uppercase font-black text-zinc-500 tracking-wider">Cartão Crédito/Débito</p>
                            <p className="text-3xl font-black text-blue-400 mt-1">R$ {resumoFinanceiro.total_cartao?.toFixed(2)}</p>
                        </div>
                        <div className="rounded-2xl border border-zinc-900 bg-zinc-900/40 p-5 shadow-lg">
                            <p className="text-[10px] uppercase font-black text-zinc-500 tracking-wider">Espécie (Dinheiro físico)</p>
                            <p className="text-3xl font-black text-amber-500 mt-1">R$ {resumoFinanceiro.total_dinheiro?.toFixed(2)}</p>
                        </div>
                    </div>

                    {/* Monitor de Comandas em Aberto no Salão */}
                    <div className="rounded-2xl border border-zinc-900 bg-zinc-950 p-6 shadow-xl">
                        <h2 className="text-xs uppercase font-black tracking-widest text-zinc-500 mb-4">Comandas Ativas no Salão</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-zinc-900 text-[10px] font-black uppercase text-zinc-500 tracking-wider">
                                        <th className="pb-3">Cartão PVC</th>
                                        <th className="pb-3">Status Interno</th>
                                        <th className="pb-3">Ações Administrativas</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-zinc-900/40 text-sm">
                                    {comandasAbertas.map((comanda) => (
                                        <tr key={comanda.id} className="hover:bg-zinc-900/20">
                                            <td className="py-3 font-black text-zinc-200">💳 Comanda #{comanda.numero_pvc}</td>
                                            <td className="py-3">
                                                <span className="rounded bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 text-xs font-bold text-amber-400 uppercase">
                                                    {comanda.status}
                                                </span>
                                            </td>
                                            <td className="py-3">
                                                <button className="text-xs font-black text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-md border border-emerald-500/20 hover:bg-emerald-500 hover:text-zinc-950 transition-all">
                                                    🔎 Emitir Extrato Master
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                    {comandasAbertas.length === 0 && (
                                        <tr>
                                        <td colSpan="3" className="py-4 text-center text-xs text-zinc-600 font-bold uppercase tracking-wider">Nenhum cartão ativo em circulação.</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </section>

                {/* COLUNA 2: Central de Alertas Críticos (Almoxarifado e Validades) */}
                <section className="rounded-2xl border border-zinc-900 bg-zinc-950 p-6 shadow-xl h-fit">
                    <div className="flex items-center justify-between border-b border-zinc-900 pb-3 mb-4">
                        <h2 className="text-xs uppercase font-black tracking-widest text-zinc-500">Alertas de Estoque & Lote</h2>
                        <span className="rounded bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 text-[10px] font-black text-rose-400 uppercase animate-pulse">
                            ⚠️ Alerta de Perda
                        </span>
                    </div>

                    <div className="space-y-3">
                        {alertasEstoque.map((alerta, index) => (
                            <div 
                                key={index} 
                                className={`rounded-xl border p-4 space-y-1.5 ${
                                    alerta.tipo === 'VALIDADE' 
                                        ? 'bg-rose-950/20 border-rose-950 text-rose-200' 
                                        : 'bg-amber-950/20 border-amber-950 text-amber-200'
                                }`}
                            >
                                <div className="flex items-center justify-between">
                                    <h4 className="font-black text-sm">{alerta.insumo_nome}</h4>
                                    <span className="text-[10px] font-mono bg-black/30 px-1.5 py-0.5 rounded font-bold">
                                        {alerta.tipo}
                                    </span>
                                </div>
                                <p className="text-xs opacity-90">{alerta.mensagem}</p>
                                <div className="text-[10px] font-bold uppercase tracking-wider opacity-60 pt-1">
                                    {alerta.tipo === 'VALIDADE' 
                                        ? `Vencimento: ${new Date(alerta.data_validade).toLocaleDateString('pt-BR')}` 
                                        : `Saldo Atual: ${alerta.quantidade_atual} unidades`
                                    }
                                </div>
                            </div>
                        ))}
                        {alertasEstoque.length === 0 && (
                            <div className="text-center py-6 text-zinc-600 text-xs font-bold uppercase tracking-wider">
                                ✅ Almoxarifado em conformidade total. Nenhuma perda detectada.
                            </div>
                        )}
                    </div>
                </section>

            </div>
        </div>
    );
};
