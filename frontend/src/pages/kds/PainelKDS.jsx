// frontend/src/pages/kds/PainelKDS.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useSocket } from '../../context/SocketContext';
import { CartaoProducao } from './CartaoProducao';

export const PainelKDS = () => {
    const { notificacoes, online } = useSocket();
    const [fila, setFila] = useState([]);
    const [setor, setSetor] = useState('COZINHA'); // COZINHA ou BAR
    const [carregando, setCarregando] = useState(true);

    // 1. Busca a fila cronológica de produção ativa do backend (Porta 8080 do Docker)
    const carregarFilaAtiva = useCallback(async () => {
        try {
            const response = await fetch(`http://192.168.111{setor}`);
            if (!response.ok) throw new Error("Erro ao buscar fila do KDS");
            const data = await response.json();
            setFila(data);
        } catch (error) {
            console.error("Falha na API do KDS:", error);
        } finally {
            setCarregando(false);
        }
    }, [setor]);

    useEffect(() => {
        carregarFilaAtiva();
    }, [carregarFilaAtiva]);

    // 2. Intercepta novos pedidos via WebSocket para empurrar os cartões em tempo real
    useEffect(() => {
        if (notificacoes.length > 0) {
            const ultimoAlerta = notificacoes;
            if (ultimoAlerta.evento == "novo_pedido_kds" && ultimoAlerta.setor == setor) {
                setFila((filaAtual) => [...filaAtual, ultimoAlerta.pedido]);
            }
        }
    }, [notificacoes, setor]);

    // 3. Função de avanço de estágio (POST para a API que dispara baixa de estoque FEFO)
    const handleAvancarStatus = async (pedidoId) => {
        try {
            const response = await fetch(`http://192.168.111{pedidoId}/avancar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            if (response.ok) {
                // Remove ou atualiza o cartão na tela reativamente
                setFila((filaAtual) => filaAtual.filter(p => p.id !== pedidoId));
            }
        } catch (error) {
            console.error("Erro ao avançar status do prato:", error);
        }
    };

    // 4. 🎛️ CAPTURA GLOBAL DO HARDWARE: Teclado Numérico USB
    useEffect(() => {
        const capturarInputTeclado = (event) => {
            const tecla = event.key;
            
            // Verifica se a tecla pressionada é um número entre 1 e 9
            if (tecla >= '1' && tecla <= '9') {
                const indexAlvo = parseInt(tecla, 10) - 1;
                const pedidoAlvo = fila[indexAlvo];
                
                if (pedidoAlvo) {
                    console.log(`⌨️ Teclado USB acionou a posição #${tecla}: Avançando Pedido ID ${pedidoAlvo.id}`);
                    handleAvancarStatus(pedidoAlvo.id);
                }
            }
        };

        window.addEventListener('keydown', capturarInputTeclado);
        return () => window.removeEventListener('keydown', capturarInputTeclado);
    }, [fila]);

    if (carregando) {
        return (
            <div className="flex h-screen items-center justify-center bg-zinc-950 text-white">
                <div className="h-10 w-10 animate-spin rounded-full border-4 border-t-emerald-500 border-zinc-800"></div>
                <span className="ml-3 font-medium text-zinc-400">Indexando monitores KDS...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 p-4 text-white font-sans selection:bg-emerald-500 selection:text-zinc-950">
            {/* Header de Monitoramento KDS */}
            <header className="mb-6 flex items-center justify-between border-b border-zinc-900 pb-4 bg-zinc-950">
                <div className="flex items-center gap-6">
                    <div>
                        <h1 className="text-xl font-black tracking-tight text-zinc-100">KDS Monitor</h1>
                        <p className="text-xs text-zinc-500 font-bold uppercase">Fila de Produção Ativa</p>
                    </div>
                    {/* Alternador de Setor Manual (Caso queira debugar Bar/Cozinha na mesma TV) */}
                    <div className="flex bg-zinc-900 p-1 rounded-xl border border-zinc-800">
                        <button 
                            onClick={() => { setSetor('COZINHA'); setCarregando(true); }}
                            className={`px-4 py-1.5 text-xs font-black uppercase rounded-lg transition-all ${setor === 'COZINHA' ? 'bg-emerald-500 text-zinc-950' : 'text-zinc-400 hover:text-zinc-200'}`}
                        >
                            🍳 Cozinha
                        </button>
                        <button 
                            onClick={() => { setSetor('BAR'); setCarregando(true); }}
                            className={`px-4 py-1.5 text-xs font-black uppercase rounded-lg transition-all ${setor === 'BAR' ? 'bg-emerald-500 text-zinc-950' : 'text-zinc-400 hover:text-zinc-200'}`}
                        >
                            🍺 Bar
                        </button>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <span className="text-xs font-bold text-zinc-500 bg-zinc-900 px-3 py-1.5 rounded-lg border border-zinc-800/60">
                        ⌨️ Teclado USB Ativo [1-9]
                    </span>
                    <div className="flex items-center gap-2 rounded-full bg-zinc-900 px-3 py-1.5 text-xs font-semibold border border-zinc-800">
                        <span className={`h-2.5 w-2.5 rounded-full ${online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`}></span>
                        {online ? 'KDS Sockets Online' : 'Sem Sinal'}
                    </div>
                </div>
            </header>

            {/* Grid de Cartões de Produção (Otimizado para Layout de TV 16:9) */}
            {fila.length === 0 ? (
                <div className="flex h-[70vh] flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-950 text-zinc-500">
                    <span className="text-4xl mb-2">🍽️</span>
                    <p className="text-sm font-black uppercase tracking-wider">Fila Limpa. Nenhum pedido pendente!</p>
                </div>
            ) : (
                <main className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                    {fila.map((pedido, index) => (
                        <CartaoProducao 
                            key={pedido.id} 
                            pedido={pedido} 
                            index={index} 
                            onAvancarStatus={handleAvancarStatus} 
                        />
                    ))}
                </main>
            )}
        </div>
    );
};
