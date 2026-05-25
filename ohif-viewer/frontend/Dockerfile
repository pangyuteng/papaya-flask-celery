FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Install git first
RUN apk add --no-cache git

# Copy OHIF Viewers source
RUN git clone https://github.com/OHIF/Viewers.git .

# Install dependencies
RUN yarn config set workspaces-experimental true
RUN yarn install --frozen-lockfile

# Configure for our use case
COPY frontend/config.js ./platform/viewer/config/
COPY frontend/extensions.config.js ./

# Build the viewer
RUN yarn run build

# Production stage
FROM nginx:alpine

# Copy built frontend
COPY --from=frontend-builder /app/packages/app/dist /usr/share/nginx/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]