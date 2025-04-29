# Usa una imagen oficial de Node.js como base
FROM node:20

# Configura el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de tu proyecto al contenedor
# Es mejor copiar package.json primero para aprovechar el caché de Docker
COPY package*.json ./
RUN npm install

# Copia el resto de los archivos
COPY . .

# ¡¡QUITAMOS ESTA LÍNEA!! -> RUN npm run build

# Expone el puerto REAL en el que Vite sirve la app por defecto
EXPOSE 5173

# Comando para iniciar la app en modo desarrollo, escuchando en todas las interfaces
# El '--' es para pasar argumentos directamente a vite, no a npm
CMD ["npm", "run", "dev", "--", "--host"]
