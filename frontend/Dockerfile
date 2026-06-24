# Estágio 1: Build da aplicação React/Vite (Imagem de compilação)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Estágio 2: Ambiente de Produção Otimizado (Imagem final de execução)
FROM nginx:1.25-alpine
# Copia o build do estágio anterior direto para o diretório público do Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Sobrescreve a configuração padrão do Nginx pela nossa roteada
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
