# Stage 1: Build the application
FROM node:20 AS build
WORKDIR /app

# --- AÑADIR ESTO ---
# Definimos el argumento (lo recibiremos desde docker-compose)
ARG VITE_API_BASE_URL
# Lo convertimos en variable de entorno para el build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
# -------------------
    
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve the application
FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist /app
RUN npm install -g serve
EXPOSE 8080
CMD ["serve", "-s", "."]
