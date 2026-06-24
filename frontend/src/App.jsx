// frontend/src/App.jsx
import React, { useState, useEffect } from 'react';
import { SocketProvider } from './context/SocketContext';
import { AtendimentoProvider, useAtendimento } from './context/AtendimentoContext';

// Telas da Frente A (Garçom)
import { SelecaoMesa } from './pages/SelecaoMesa';
import { LancarPedido } from './pages/LancarPedido';
import { ResumoConta } from './pages/ResumoConta';

// Telas da Frente B (Cliente - Autoatendimento)
import { ValidacaoComanda } from './pages/cliente/ValidacaoComanda';
import { CardapioCliente } from './pages/cliente/CardapioCliente';
import { SucessoPedido } from './pages/cliente/SucessoPedido';

// Módulo KDS (TVs da Cozinha e do Bar)
import { PainelKDS } from './pages/kds/PainelKDS';

// 🆕 Módulo do Caixa (Terminal Administrativo e Financeiro)
import { PainelCaixa } from './pages/caixa/PainelCaixa';

const FluxoNavegacaoMaster = () => {
    const { abrirMesaTrabalho, setComandaAtiva } = useAtendimento();
    
    // Máquina de estados expandida para suportar os quatro perfis na mesma LAN
    const [perfil, setPerfil] = useState('DESCONHECIDO'); // GARCOM, CLIENTE, KDS ou CAIXA
    const [telaAtiva, setTelaAtiva] = useState('INICIAL');

    // 1. Interceptador Omnichannel de URL (Gatilho de Entrada de Perfil por Hardware/QR Code)
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const tokenHmac = params.get('token');
        const modoOperacao = params.get('modo');

        // 📊 1. Identifica se o dispositivo é o Terminal Desktop do Caixa
        if (modoOperacao === 'caixa') {
            setPerfil('CAIXA');
            setTelaAtiva('PAINEL_FINANCEIRO');
        }
        // 📺 2. Identifica se o dispositivo é uma TV de produção KDS
        else if (modoOperacao === 'kds') {
            setPerfil('KDS');
            setTelaAtiva('PAINEL_PRODUCAO');
        } 
        // 🛡️ 3. Identifica se o dispositivo é um smartphone de cliente via QR Code seguro
        else if (tokenHmac) {
            setPerfil('CLIENTE');
            setTelaAtiva('VALIDACAO_HMAC');
        } 
        // 💼 4. Se a URL estiver limpa, assume o perfil padrão do Garçom no salão
        else {
            setPerfil('GARCOM');
            setTelaAtiva('MAPA_MESAS');
        }
    }, []);

    // 2. Fluxo de Decisão do Garçom (Frente A)
    const handleMesaSelecionadaGarcom = (mesaId) => {
        abrirMesaTrabalho(mesaId);
        const comandaInput = prompt("Digite a comanda PVC física (ou deixe em branco para mesa pura):");
        if (comandaInput) setComandaAtiva(parseInt(comandaInput, 10));
        else setComandaAtiva(null);

        const irParaPedido = confirm("Clique em [OK] para LANÇAR PEDIDO ou [Cancelar] para VER CONTA:");
        setTelaAtiva(irParaPedido ? 'PEDIDO_GARCOM' : 'CONTA_GARCOM');
    };

    // 3. Orquestrador de Telas State-Driven (Clean Architecture)
    
    // Perfil Operacional: Garçom (Frente A)
    if (perfil === 'GARCOM') {
        switch (telaAtiva) {
            case 'MAPA_MESAS':
                return <SelecaoMesa onSelecionarMesa={handleMesaSelecionadaGarcom} />;
            case 'PEDIDO_GARCOM':
                return <LancarPedido onVoltar={() => setTelaAtiva('MAPA_MESAS')} />;
            case 'CONTA_GARCOM':
                return <ResumoConta onVoltar={() => setTelaAtiva('MAPA_MESAS')} />;
            default:
                return <SelecaoMesa onSelecionarMesa={handleMesaSelecionadaGarcom} />;
        }
    }

    // Perfil Operacional: Autoatendimento Cliente (Frente B)
    if (perfil === 'CLIENTE') {
        switch (telaAtiva) {
            case 'VALIDACAO_HMAC':
                return <ValidacaoComanda onValidado={() => setTelaAtiva('CARDAPIO_CLIENTE')} />;
            case 'CARDAPIO_CLIENTE':
                return <CardapioCliente onPedidoSucesso={() => setTelaAtiva('SUCESSO_KDS')} />;
            case 'SUCESSO_KDS':
                return <SucessoPedido onNovoPedido={() => setTelaAtiva('CARDAPIO_CLIENTE')} />;
            default:
                return <ValidacaoComanda onValidado={() => setTelaAtiva('CARDAPIO_CLIENTE')} />;
        }
    }

    // Perfil Operacional: Monitores KDS das TVs (Cozinha/Bar)
    if (perfil === 'KDS') {
        switch (telaAtiva) {
            case 'PAINEL_PRODUCAO':
                return <PainelKDS />;
            default:
                return <PainelKDS />;
        }
    }

    // 🆕 Perfil Operacional: Terminal Desktop do Caixa
    if (perfil === 'CAIXA') {
        switch (telaAtiva) {
            case 'PAINEL_FINANCEIRO':
                return <PainelCaixa />;
            default:
                return <PainelCaixa />;
        }
    }

    // Tela de transição rápida enquanto o useEffect processa as chaves da URL
    return (
        <div className="flex h-screen items-center justify-center bg-zinc-950 text-white text-xs font-mono tracking-widest uppercase">
            Sincronizando Ecossistema Garage...
        </div>
    );
};

export default function App() {
    return (
        <SocketProvider>
            <AtendimentoProvider>
                <div className="min-h-screen bg-zinc-900 font-sans antialiased text-white">
                    <FluxoNavegacaoMaster />
                </div>
            </AtendimentoProvider>
        </SocketProvider>
    );
}
