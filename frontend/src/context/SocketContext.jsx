// src/context/SocketContext.jsx
import React, { createContext, useContext, useEffect, useState } from 'react';

const SocketContext = createContext(null);

export const SocketProvider = ({ children }) => {
    const [socket, setSocket] = useState(null);
    const [notificacoes, setNotificacoes] = useState([]);
    const [online, setOnline] = useState(false);

    useEffect(() => {
        // Conecta ao barramento global de upgrades de Sockets do seu FastAPI
        // Mudamos o subdomínio para o IP físico configurado na sua LAN (192.168.111.124:8080)
        const wsUrl = "ws://192.168.111.124:8080/pedidos/ws/garcons";
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            setOnline(true);
            console.log("⚡ Conectado ao Barramento WebSocket do Garage Bistrô");
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Empurra pop-ups visuais e sonoros instantaneamente na tela do garçom
            setNotificacoes((prev) => [data, ...prev]);
            
            // Toca um alerta sonoro discreto se o dispositivo permitir
            if (typeof Audio !== "undefined") {
                const audio = new Audio('/assets/notification.mp3');
                audio.play().catch(() => {});
            }
        };

        ws.onclose = () => {
            setOnline(false);
            console.log("❌ Conexão WebSocket perdida. Tentando reconectar...");
            // Lógica de reconexão automática após queda do sinal Wi-Fi 5G
            setTimeout(() => {
                setSocket(new WebSocket(wsUrl));
            }, 5000);
        };

        setSocket(ws);

        return () => ws.close();
    }, []);

    const limparNotificacao = (index) => {
        setNotificacoes((prev) => prev.filter((_, i) => i !== index));
    };

    return (
        <SocketContext.Provider value={{ socket, notificacoes, online, limparNotificacao }}>
            {children}
        </SocketContext.Provider>
    );
};

export const useSocket = () => useContext(SocketContext);
