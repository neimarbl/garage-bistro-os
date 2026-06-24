-- 1. Carga Inicial de Mesas (Layout Dinâmico do Salão)
INSERT INTO mesas (numero_identificador, status, mesa_pai_id) VALUES 
(1, 'livre', NULL),
(2, 'livre', NULL),
(3, 'ocupada', NULL),
(4, 'livre', NULL), -- Mesa base do nosso teste de Autoatendimento
(5, 'livre', NULL),
-- Simulação de Aniversário: Mesas 6 e 7 agrupadas logicamente sob a Mesa Pai 5
(6, 'ocupada', 5),
(7, 'ocupada', 5);

-- 2. Carga Inicial do Cardápio Dinâmico
INSERT INTO produtos (nome, preco, categoria, ativo) VALUES 
('Hambúrguer Garage Master', 45.00, 'HAMBURGUER', true),
('Espetinho de Alcatra Premium', 18.00, 'ESPETINHO', true),
('Chopp Artesanal Garage 500ml', 18.00, 'BEBIDA', true),
('Porção de Batata Rústica', 32.00, 'PORCAO', true),
('Água Mineral sem Gás', 5.00, 'BEBIDA', true);

-- 3. Carga Inicial de Insumos no Almoxarifado (Estoque Crítico)
INSERT INTO insumos (nome, quantidade_atual, quantidade_minima, data_validade, congelado) VALUES 
('Blend de Carne Bovino 150g', 50.00, 10.00, '2026-07-15 00:00:00', true),
('Pão de Hambúrguer Brioche', 40.00, 8.00, '2026-06-30 00:00:00', false),
('Barril de Chopp 50L', 2.00, 1.00, '2026-08-01 00:00:00', false);

-- 4. Vínculo de Ficha Técnica (Consumo de Receitas Invisível)
-- Hambúrguer Garage Master (ID 1) consome 1 Blend (ID 1) e 1 Pão (ID 2)
INSERT INTO fichas_tecnicas (produto_id, insumo_id, quantidade_gasta) VALUES 
(1, 1, 1.000),
(1, 2, 1.000),
-- Chopp Artesanal (ID 3) consome 0.5L do Barril (ID 3)
(3, 3, 0.500);

-- 5. Ativação de uma Comanda Física de PVC para Testes
-- Token SHA256 simulado baseado na chave secreta para a Comanda 15
INSERT INTO comandas (numero_pvc, status, token_sessao, criado_em) VALUES 
(15, 'ativa', 'f03da73117498c1170940bf7cb9ea9c37953cb7e9c90b8f05e4dfa9f7e34efee', NOW());
