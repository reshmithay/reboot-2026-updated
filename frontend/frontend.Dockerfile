# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Serve stage — nginx serves the static build and proxies /api/ to backend
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Use the nginx.conf from the frontend build context
COPY /nginx/nginx.conf /etc/nginx/conf.d/default.conf
# Remove default nginx config that conflicts on port 80
RUN rm -f /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
