FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application
COPY . .

# Build next.js
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
