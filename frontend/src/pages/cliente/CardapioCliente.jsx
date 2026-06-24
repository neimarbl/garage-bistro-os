// frontend/src/pages/cliente/CardapioCliente.jsx
import React, { useState, useEffect } from 'react';
import { useAtendimento } from '../../context/AtendimentoContext';

export const CardapioCliente = ({ onPedidoSucesso }) => {
    const { 
        mesaAtiva, 
        comandaAtiva, 
        cardapio, 
        carregandoCardapio, 
        carregarCardapio, 
        carrinho, 
        adicionarAoCarrinho, 
        removerDoCarrinho 
    } = useAtendimento();

    const [categoriaAtiva, setCategoriaAtiva] = useState('HAMBURGUER');
    const [obsCliente, setObsCliente] = useState({});
    const [enviandoPedido, setEnviandoPedido] = useState(false);

    // 1. Carrega o cardápio oficial ao abrir a tela de autoatendimento
    useEffect(() => {
        carregarCardapio();
    }, [carregarCardapio]);

    const categorias = [...new Set(cardapio.map(p => p.categoria))];

    // 2. Calcula subtotais e taxas de forma transparente para o cliente do bistrô
    const subtotal = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
    const taxaServico = subtotal * 0.10;
    const totalEstimado = subtotal + taxaServico;

    // 3. Finaliza a comanda enviando o payload casado com as regras antifraude do backend
    const handleFinalizarAutoatendimento = async () => {
        if (carrinho.length === 0) return;
        setEnviandoPedido(true);

        // Recupera o token de assinatura criptográfica validado no passo anterior
        const tokenHmac = localStorage.getItem('gb_token_hmac');

        const payload = {
            mesa_id: mesaAtiva,
            comanda_id: comandaAtiva, // Corresponde ao numero_pvc salvo no contexto
            token_hmac: tokenHmac,     # Elemento crucial exigido pela blindagem antifraude
            origem: "autoatendimento",
            itens: carrinho.map(item => ({
                produto_id: item.id,
                quantidade: item.quantidade,
                observacao: item.observacao || null
            }))
        };

        try {
            const response = await fetch('http://192.168.111', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                onPedidoSucesso(); // Redireciona para a tela de feedback de sucesso
            } else {
                const data = await response.json();
                alert(`🛑 Falha de Segurança: ${data.detail || 'Transação negada pelo servidor.'}`);
            }
        } catch (error) {
            alert('❌ Erro de conexão com o servidor local da garagem.');
        } finally {
            setEnviandoPedido(false);
        }
    };

    if (carregandoCardapio) {
        return (
            <div className="flex h-screen flex-col items-center justify-center bg-zinc-950 text-white">
                <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-t-emerald-500 border-zinc-800"></div>
                <p className="mt-3 text-xs text-zinc-400 font-medium">Montando cardápio digital...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-950 pb-40 text-white">
            {/* Header com Contexto Geográfico */}
            <header className="sticky top-0 z-10 border-b border-zinc-900 bg-zinc-950/90 p-4 backdrop-blur">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-lg font-black tracking-tight text-zinc-100">Garage Bistrô</h1>
                        <p className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">Mesa {mesaAtiva} • Comanda PVC {comandaAtiva}</p>
                    </div>
                    <div className="rounded-full bg-emerald-500/10 px-3 py-1 text-[11px] font-black uppercase text-emerald-400 border border-emerald-500/20">
                        📱 Autoatendimento
                    </div>
                </div>
            </header>

            {/* Categorias Roláveis (Touch Friendly) */}
            <nav className="flex gap-2 overflow-x-auto p-4 scrollbar-none bg-zinc-950 border-b border-zinc-900">
                {categorias.map((cat) => (
                    <button
                        key={cat}
                        onClick={() => setCategoriaAtiva(cat)}
                        className={`rounded-full px-5 py-2 text-xs font-black uppercase tracking-widest transition-all ${
                            categoriaAtiva === cat 
                                ? 'bg-emerald-500 text-zinc-950 shadow-md shadow-emerald-500/10' 
                                : 'bg-zinc-900 text-zinc-400 hover:bg-zinc-800'
                        }`}
                    >
                        {cat.toLowerCase()}
                    </button>
                ))}
            </nav>

            {/* Feed de Produtos */}
            <main className="space-y-4 p-4">
                {cardapio.filter(p => p.categoria === categoriaAtiva).map((produto) => {
                    const itemNoCarrinho = carrinho.find(i => i.id === produto.id && i.observacao === (obsCliente[produto.id] || ""));
                    
                    return (
                        <div key={produto.id} className="rounded-2xl border border-zinc-900 bg-zinc-900/40 p-4 transition-all">
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <h3 className="font-bold text-zinc-100 text-sm">{produto.nome}</h3>
                                    <p className="text-xs text-zinc-400 mt-1 leading-relaxed">Prepare-se para o sabor exclusivo da nossa garagem sobre rodas.</p>
                                    <p className="text-base font-black text-emerald-400 mt-2">R$ {parseFloat(produto.preco).toFixed(2)}</p>
                                </div>

                                {/* Controles de Volume Minimalistas */}
                                <div className="flex items-center gap-2 bg-zinc-950 rounded-xl p-1 border border-zinc-900 h-10">
                                    {itemNoCarrinho?.quantidade > 0 && (
                                        <>
                                            <button 
                                                onClick={() => removerDoCarrinho(produto.id, obsCliente[produto.id] || "")}
                                                className="h-8 w-8 rounded-lg bg-zinc-900 text-sm font-black text-zinc-400 active:bg-zinc-800"
                                            >
                                                -
                                            </button>
                                            <span className="w-5 text-center font-black text-xs text-zinc-200">
                                                {itemNoCarrinho.quantidade}
                                            </span>
                                        </>
                                    )}
                                    <button 
                                        onClick={() => adicionarAoCarrinho(produto, obsCliente[produto.id] || "")}
                                        className="h-8 w-8 rounded-lg bg-emerald-500 text-sm font-black text-zinc-950 active:bg-emerald-600"
                                    >
                                        +
                                    </button>
                                </div>
                            </div>

                            {/* Campo de Notas da Cozinha para o Cliente */}
                            <div className="mt-3 border-t border-zinc-950 pt-2.5">
                                <input 
                                    type="text"
                                    placeholder="🍳 Alguma observação? Ex: ponto da carne, sem gelo..."
                                    value={obsCliente[produto.id] || ""}
                                    onChange={(e) => setObsCliente({ ...obsCliente, [produto.id]: e.target.value })}
                                    className="w-full bg-zinc-950/80 px-3 py-2 rounded-xl text-xs border border-zinc-900 text-zinc-400 focus:outline-none focus:border-zinc-800 transition-colors"
                                />
                            </div>
                        </div>
                    );
                })}
            </main>

            {/* Checkout Suspenso do Autoatendimento */}
            {carrinho.length > 0 && (
                <footer className="fixed bottom-0 inset-x-0 border-t border-zinc-900 bg-zinc-950/95 p-4 backdrop-blur shadow-2xl animate-fade-in-up">
                    <div className="mx-auto max-w-sm space-y-3">
                        {/* Resumo de taxas preventivo */}
                        <div className="flex justify-between text-[11px] font-bold text-zinc-500 uppercase tracking-widest border-b border-zinc-900 pb-2">
                            <span>Subtotal: R$ {subtotal.toFixed(2)}</span>
                            <span>Taxa (10%): R$ {taxaServico.toFixed(2)}</span>
                        </div>
                        
                        <div className="flex items-center justify-between gap-4">
                            <div>
                                <p className="text-[9px] uppercase font-black tracking-widest text-zinc-500">Total do Pedido</p>
                                <p className="text-lg font-black text-emerald-400">R$ {totalEstimado.toFixed(2)}</p>
                            </div>
                            <button
                                onClick={handleFinalizarAutoatendimento}
                                disabled={enviandoPedido}
                                className="flex-1 rounded-xl bg-emerald-500 py-3.5 text-center text-xs font-black uppercase tracking-wider text-zinc-950 transition-all hover:bg-emerald-400 active:scale-95 disabled:bg-zinc-800 disabled:text-zinc-600"
                            >
                                {enviandoPedido ? 'Validando HMAC...' : '🍳 Enviar para Cozinha'}
                            </button>
                        </div>
                    </div>
                </footer>
            )}
        </div>
    );
};
