// frontend/src/pages/cliente/ValidacaoComanda.jsx
import React, { useEffect, useState } from 'react';
import { useAtendimento } from '../../context/AtendimentoContext';

export const ValidacaoComanda = ({ onValidado }) => {
    const { setComandaAtiva, abrirMesaTrabalho } = useAtendimento();
    const [statusValidacao, setStatusValidacao] = useState('processando'); // processando, valido, erro
    const [erroMensagem, setErroMensagem] = useState('');

    useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const mesaId = params.get('mesa');
    const numeroPvc = params.get('pvc'); // 🟢 Casando com seu backend
    const tokenHmac = params.get('token');

    if (!mesaId || !numeroPvc || !tokenHmac) {
        setStatusValidacao('erro');
        setErroMensagem('QR Code inválido. Peça um cartão de PVC válido ao garçom.');
        return;
    }

    abrirMesaTrabalho(parseInt(mesaId, 10));
    setComandaAtiva(parseInt(numeroPvc, 10)); // Mantém o estado global ciente

    const verificarAssinaturaDigital = async () => {
        try {
            // 🟢 Chamando a rota enviando o parâmetro correto 'token' e 'pvc'
            const response = await fetch(`http://192.168.111{numeroPvc}/validar?token=${tokenHmac}`);
            
            if (response.ok) {
                setStatusValidacao('valido');
                localStorage.setItem('gb_token_hmac', tokenHmac);
                setTimeout(() => onValidado(), 1500);
            } else {
                const data = await response.json();
                setStatusValidacao('erro');
                setErroMensagem(data.detail || 'Assinatura digital inválida.');
            }
        } catch (error) {
            setStatusValidacao('erro');
            setErroMensagem('Erro de conexão com a rede Wi-Fi 5G da garagem.');
        }
    };

    verificarAssinaturaDigital();
}, [abrirMesaTrabalho, setComandaAtiva, onValidado]);

    return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-6 text-white">
            <div className="w-full max-w-sm rounded-2xl bg-zinc-900 border border-zinc-800 p-6 text-center shadow-2xl">
                {statusValidacao === 'processando' && (
                    <div className="space-y-4">
                        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-t-emerald-500 border-zinc-800"></div>
                        <h2 className="text-lg font-bold tracking-tight">Criptografia Baseada em HMAC</h2>
                        <p className="text-xs text-zinc-400">Validando autenticidade do cartão físico e localização geográfica da mesa...</p>
                    </div>
                )}

                {statusValidacao === 'valido' && (
                    <div className="space-y-3 animate-fade-in">
                        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/10 text-2xl text-emerald-400">
                            🛡️
                        </div>
                        <h2 className="text-lg font-black text-emerald-400 uppercase tracking-wide">Acesso Autorizado</h2>
                        <p className="text-xs text-zinc-300">Conexão criptográfica segura estabelecida com sucesso!</p>
                    </div>
                )}

                {statusValidacao === 'erro' && (
                    <div className="space-y-4 animate-shake">
                        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/10 text-2xl text-rose-400">
                            🛑
                        </div>
                        <h2 className="text-lg font-black text-rose-500 uppercase tracking-wide">Alerta de Fraude</h2>
                        <p className="text-xs text-zinc-300 font-medium leading-relaxed bg-zinc-950 p-3 rounded-xl border border-rose-950 text-left">
                            {erroMensagem}
                        </p>
                        <button 
                            onClick={() => window.location.reload()}
                            className="w-full rounded-xl bg-zinc-800 py-3 text-sm font-bold border border-zinc-700 hover:bg-zinc-700 active:scale-95 transition-all"
                        >
                            🔄 Tentar Novamente
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
