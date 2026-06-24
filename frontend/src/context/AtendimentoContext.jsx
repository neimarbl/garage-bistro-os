// frontend/src/context/AtendimentoContext.jsx
import React, { createContext, useContext, useState, useCallback } from 'react';

const AtendimentoContext = createContext(null);

export const AtendimentoProvider = ({ children }) => {
    const [mesaAtiva, setMesaAtiva] = useState(null);
    const [comandaAtiva, setComandaAtiva] = useState(null);
    const [carrinho, setCarrinho] = useState([]);
    const [cardapio, setCardapio] = useState([]);
    const [carregandoCardapio, setCarregandoCardapio] = useState(false);

    // 1. Carrega o cardápio dinâmico filtrando itens ativos da API local
    const carregarCardapio = useCallback(async () => {
        setCarregandoCardapio(true);
        try {
            const response = await fetch('http://192.168.111');
            if (!response.ok) throw new Error("Falha ao buscar cardápio");
            const data = await response.json();
            // Filtra apenas produtos ativos no cardápio
            setCardapio(data.filter(p => p.ativo));
        } catch (error) {
            console.error("Erro na API de cardápio:", error);
        } finally {
            setCarregandoCardapio(false);
        }
    }, []);

    // 2. Seleciona a mesa de trabalho no salão
    const abrirMesaTrabalho = (mesaId) => {
        setMesaAtiva(mesaId);
        setCarrinho([]); // Limpa o carrinho de transições anteriores
    };

    // 3. Adiciona item ao carrinho fracionado com observações rápidas de salão
    const adicionarAoCarrinho = (produto, observacao = "") => {
        setCarrinho((itensAtuais) => {
            const itemExistente = itensAtuais.find(
                (item) => item.id === produto.id && item.observacao === observacao
            );

            if (itemExistente) {
                return itensAtuais.map((item) =>
                    item.id === produto.id && item.observacao === observacao
                        ? { ...item, quantidade: item.quantidade + 1 }
                        : item
                );
            }

            return [...itensAtuais, { ...produto, quantidade: 1, observacao }];
        });
    };

    // 4. Remove ou decrementa a quantidade de um item de forma reativa
    const removerDoCarrinho = (produtoId, observacao = "") => {
        setCarrinho((itensAtuais) => {
            const item = itensAtuais.find(i => i.id === produtoId && i.observacao === observacao);
            if (!item) return itensAtuais;

            if (item.quantidade > 1) {
                return itensAtuais.map((i) =>
                    i.id === produtoId && i.observacao === observacao
                        ? { ...i, quantidade: i.quantidade - 1 }
                        : i
                );
            }

            return itensAtuais.filter((i) => !(i.id === produtoId && i.observacao === observacao));
        });
    };

    // 5. Envia o payload em bloco (POST) estruturado para o backend
    const dispararPedidoCozinha = async () => {
        if (carrinho.length === 0 || !mesaAtiva) return false;

        // Monta o contrato exato que a API do FastAPI espera
        const payload = {
            mesa_id: mesaAtiva,
            comanda_id: comandaAtiva || 0, // 0 indica pedido feito direto pelo Garçom sem PWA do cliente
            origem: "garcon",
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

            if (!response.ok) throw new Error("Erro ao lançar pedido no banco");
            
            setCarrinho([]); // Limpa o carrinho após o sucesso do disparo para o KDS
            return true;
        } catch (error) {
            console.error("Falha ao enviar pedido:", error);
            return false;
        }
    };

    return (
        <AtendimentoContext.Provider value={{
            mesaAtiva,
            comandaAtiva,
            setComandaAtiva,
            carrinho,
            cardapio,
            carregandoCardapio,
            carregarCardapio,
            abrirMesaTrabalho,
            adicionarAoCarrinho,
            removerDoCarrinho,
            dispararPedidoCozinha
        }}>
            {children}
        </AtendimentoContext.Provider>
    );
};

export const useAtendimento = () => useContext(AtendimentoContext);
