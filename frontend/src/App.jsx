// frontend/src/App.jsx
import React, { useState } from 'react';
import { SocketProvider } from './context/SocketContext';
import { AtendimentoProvider, useAtendimento } from './context/AtendimentoContext';
import { SelecaoMesa } from './pages/SelecaoMesa';
import { LancarPedido } from './pages/LancarPedido';
import { ResumoConta } from './pages/ResumoConta';

// Componente interno para isolar a máquina de estados de navegação
// Ele precisa estar abaixo dos Providers para consumir os Hooks com sucesso
const FluxoNavegacaoGarcom = () => {
    const { abrirMesaTrabalho, setComandaAtiva } = useAtendimento();
    const [telaAtiva, setTelaAtiva] = useState('MAPA_MESAS'); // MAPA_MESAS, PEDIDO, CONTA

    // Handler para quando o garçom toca em uma mesa no salão
    const handleMesaSelecionada = (mesaId) => {
        abrirMesaTrabalho(mesaId);
        
        // Pergunta rápida de fluxo (Opcional - Simula entrada de comanda PVC ou mesa pura)
        const comandaInput = prompt("Digite o número da comanda física PVC (ou deixe em branco para lançar na mesa):");
        if (comandaInput) {
            setComandaAtiva(parseInt(comandaInput, 10));
        } else {
            setComandaAtiva(null);
        }

        // Oferece a rota operacional baseada na intenção do garçom
        const acao = confirm("Clique em [OK] para LANÇAR PEDIDO ou [Cancelar] para VER CONTA/FECHAMENTO:");
        if (acao) {
            setTelaAtiva('PEDIDO');
        } else {
            setTelaAtiva('CONTA');
        }
    };

    // Máquina de estados de renderização de telas
    switch (telaAtiva) {
        case 'MAPA_MESAS':
            return <SelecaoMesa onSelecionarMesa={handleMesaSelecionada} />;
        case 'PEDIDO':
            return <LancarPedido onVoltar={() => setTelaAtiva('MAPA_MESAS')} />;
        case 'CONTA':
            return <ResumoConta onVoltar={() => setTelaAtiva('MAPA_MESAS')} />;
        default:
            return <SelecaoMesa onSelecionarMesa={handleMesaSelecionada} />;
    }
};

// Componente Raiz encapsulando a malha de Engenharia do Portfólio
export default function App() {
    return (
        <SocketProvider>
            <AtendimentoProvider>
                <div className="min-h-screen bg-zinc-900 font-sans antialiased selection:bg-emerald-500 selection:text-zinc-900">
                    <FluxoNavegacaoGarcom />
                </div>
            </AtendimentoProvider>
        </SocketProvider>
    );
}
