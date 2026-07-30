# ============================================================================
#  Frontend image - build the React app, then serve it with nginx (Module 13)
# ============================================================================
#  Two stages so the final image ships only static files + nginx, not Node and
#  node_modules:
#      stage 1 (build)  - npm ci + vite build  ->  /app/dist
#      stage 2 (serve)  - nginx serving dist/, proxying /api to the backend
#
#  The app calls the API with relative /api paths, so in production nginx is the
#  reverse proxy that forwards /api to the backend service (see nginx.conf) -
#  the same code that used Vite's dev proxy locally.
# ============================================================================

# --- stage 1: build -----------------------------------------------------------
FROM node:22-alpine AS build
WORKDIR /app

# Install deps first for layer caching.
COPY package*.json ./
RUN npm ci

# Build the production bundle.
COPY . .
RUN npm run build

# --- stage 2: serve -----------------------------------------------------------
FROM nginx:alpine

# Our server block: SPA fallback + /api reverse proxy.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# The static bundle from the build stage.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
