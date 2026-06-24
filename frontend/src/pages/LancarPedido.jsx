// frontend/src/pages/LancarPedido.jsx
import React, { useState, useEffect } from 'react';
import { useAtendimento } from '../context/AtendimentoContext';

export const LancarPedido = ({ onVoltar }) => {
    const { 
        mesaAtiva, 
        cardapio, 
        carregandoCardapio, 
        carregarCardapio, 
        carrinho, 
        adicionarAoCarrinho, 
        removerDoCarrinho,
        dispararPedidoCozinha 
    } = useAtendimento();

    const [categoriaAtiva, setCategoriaAtiva] = useState('HAMBURGUER');
    const [obsTexto, setObsTexto] = useState({});
    const [enviando, setEnviando] = useState(false);

    // 1. Carrega o cardápio da API local assim que a tela abre
    useEffect(() => {
        carregarCardapio();
    }, [carregarCardapio]);

    // 2. Extrai as categorias únicas dos produtos vindos da API
    const categorias = [...new Set(cardapio.map(p => p.categoria))];

    // 3. Processa o fechamento em bloco do carrinho para a Cozinha/Bar (KDS)
    const handleDispararPedido = async () => {
        if (carrinho.length === 0) return;
        setEnviando(true);
        const sucesso = await dispararPedidoCozinha();
        setEnviando(false);
        
        if (sucesso) {
            alert(`✅ Pedido enviado com sucesso para a Cozinha/Bar!`);
            onVoltar(); // Retorna para o mapa de mesas
        } else {
            alert(`❌ Falha ao enviar pedido. Verifique o Wi-Fi ou o estoque.`);
        }
    };

    // 4. Calcula o total em tempo real no rodapé do celular do garçom
    const totalCarrinho = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);

    if (carregandoCardapio) {
        return (
            <div className="flex h-screen items-center justify-center bg-zinc-900 text-white">
                <div className="animate-spin text-4xl">🔄</div>
                <span className="ml-2">Carregando cardápio operacional...</span>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-zinc-900 pb-32 text-white">
            {/* Header Fixo de Navegação */}
            <header className="sticky top-0 z-10 flex items-center justify-between border-b border-zinc-800 bg-zinc-900/90 p-4 backdrop-blur">
                <div className="flex items-center gap-3">
                    <button onClick={onVoltar} className="rounded-lg bg-zinc-800 p-2 hover:bg-zinc-700 active:scale-95">
                        ⬅️
                    </button>
                    <div>
                        <h1 className="text-xl font-bold">Lançar Pedido</h1>
                        <p className="text-xs text-emerald-400 font-semibold">Atendendo Mesa {mesaAtiva}</p>
                    </div>
                </div>
                <span className="rounded-full bg-zinc-800 px-3 py-1 text-xs font-bold text-zinc-400">
                    {carrinho.reduce((acc, i) => acc + i.quantidade, 0)} itens
                </span>
            </header>

            {/* Carrossel de Abas de Categorias (Largas e roláveis no touch) */}
            <nav className="flex gap-2 overflow-x-auto p-4 scrollbar-none border-b border-zinc-800 bg-zinc-900">
                {categorias.map((cat) => (
                    <button
                        key={cat}
                        onClick={() => setCategoriaAtiva(cat)}
                        className={`rounded-full px-5 py-2 text-xs font-black uppercase tracking-wider transition-all whitespace-nowrap active:scale-95 ${
                            categoriaAtiva === cat 
                                ? 'bg-emerald-500 text-zinc-900 shadow-lg shadow-emerald-500/20' 
                                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                        }`}
                    >
                        {cat.toLowerCase()}
                    </button>
                ))}
            </nav>

            {/* Listagem Dinâmica de Produtos Filtrados */}
            <main className="space-y-3 p-4">
                {cardapio.filter(p => p.categoria === categoriaAtiva).map((produto) => {
                    const itemNoCarrinho = carrinho.find(i => i.id === produto.id && i.observacao === (obsTexto[produto.id] || ""));
                    
                    return (
                        <div key={produto.id} className="rounded-xl border border-zinc-800 bg-zinc-950 p-4 transition-all hover:border-zinc-700">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="font-bold text-zinc-100 text-base">{produto.nome}</h3>
                                    <p className="text-sm font-black text-emerald-400 mt-1">R$ {parseFloat(produto.preco).toFixed(2)}</p>
                                </div>

                                {/* Controles Reativos de Quantidade */}
                                <div className="flex items-center gap-3 bg-zinc-900 rounded-lg p-1 border border-zinc-800">
                                    <button 
                                        onClick={() => removerDoCarrinho(produto.id, obsTexto[produto.id] || "")}
                                        className="h-8 w-8 rounded bg-zinc-800 text-sm font-black text-zinc-300 active:bg-zinc-700"
                                    >
                                        -
                                    </button>
                                    <span className="w-6 text-center font-bold text-sm text-zinc-100">
                                        {itemNoCarrinho ? itemNoCarrinho.quantidade : 0}
                                    </span>
                                    <button 
                                        onClick={() => adicionarAoCarrinho(produto, obsTexto[produto.id] || "")}
                                        className="h-8 w-8 rounded bg-emerald-500 text-sm font-black text-zinc-900 active:bg-emerald-600"
                                    >
                                        +
                                    </button>
                                </div>
                            </div>

                            {/* Input inline de Observação Rápida */}
                            <div className="mt-3 border-t border-zinc-900 pt-2">
                                <input 
                                    type="text"
                                    placeholder="⚠️ Adicionar obs: sem cebola, ponto da carne..."
                                    value={obsTexto[produto.id] || ""}
                                    onChange={(e) => setObsTexto({ ...obsTexto, [produto.id]: e.target.value })}
                                    className="w-full bg-zinc-900 px-3 py-2 rounded-lg text-xs border border-zinc-800 text-zinc-300 focus:outline-none focus:border-zinc-700 transition-colors"
                                />
                            </div>
                        </div>
                    );
                })}
            </main>

            {/* Rodapé Fixo de Fechamento de Comanda/Pedido */}
            {carrinho.length > 0 && (
                <footer className="fixed bottom-0 inset-x-0 border-t border-zinc-800 bg-zinc-950/90 p-4 backdrop-blur shadow-2xl animate-fade-in-up">
                    <div className="mx-auto flex max-w-md items-center justify-between gap-4">
                        <div className="min-w-[100px]">
                            <p className="text-[10px] uppercase font-bold tracking-widest text-zinc-500">Subtotal</p>
                            <p className="text-xl font-black text-emerald-400">R$ {totalCarrinho.toFixed(2)}</p>
                        </div>
                        <button
                            onClick={handleDispararPedido}
                            disabled={enviando}
                            className="flex-1 rounded-xl bg-emerald-500 py-3.5 text-center text-sm font-black uppercase tracking-wider text-zinc-900 transition-all hover:bg-emerald-400 active:scale-95 disabled:bg-zinc-700 disabled:text-zinc-500 shadow-xl shadow-emerald-500/10"
                        >
                            {enviando ? 'Enviando KDS...' : '🚀 Enviar para Cozinha'}
                        </button>
                    </div>
                </footer>
            )}
        </div>
    );
};
