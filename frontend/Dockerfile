# Development stage
FROM node:18-alpine AS dev

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies
RUN npm ci

# Copy source code
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM node:18-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies
RUN npm ci --only=production && npm install --save-dev vite

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS prod

WORKDIR /app

# Install serve to serve the static files
RUN npm install -g serve

# Copy the build output from the build stage
COPY --from=build /app/dist /app/dist

EXPOSE 3000

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"]