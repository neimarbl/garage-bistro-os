# Estágio 1: Build da aplicação React/Vite (Imagem de compilação)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Captura o argumento de build enviado pelo Docker Compose
ARG VITE_API_URL
# Converte o argumento em uma variável visível para o compilador do Vite
ENV VITE_API_URL=$VITE_API_URL

# Executa a compilação injetando a URL base correta no JavaScript estático
RUN npm run build

# Estágio 2: Ambiente de Produção Otimizado (Imagem final de execução)
FROM nginx:1.25-alpine
# Copia o build do estágio anterior direto para o diretório público do Nginx
COPY --from=build /app/dist /usr/share/nginx/html
# Sobrescreve a configuração padrão do Nginx pela nossa roteada
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
