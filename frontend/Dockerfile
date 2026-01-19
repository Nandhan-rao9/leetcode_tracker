# --- Stage 1: Build ---
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the code and build
COPY . .
RUN npm run build

# --- Stage 2: Serve ---
FROM nginx:stable-alpine

# Copy the build output from Stage 1 to Nginx's public folder
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]