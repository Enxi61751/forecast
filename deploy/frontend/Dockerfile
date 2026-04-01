# ---- Stage 1: Build ----
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG SERVER_URL=http://localhost
RUN VITE_API_BASE_URL=${SERVER_URL} VITE_AGENT_BASE_URL="" VITE_API_MODE="real" npx vite build

# ---- Stage 2: Serve with Nginx ----
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
