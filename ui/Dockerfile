# Builder stage
FROM node:20-slim AS builder
WORKDIR /app

ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN npm install -g pnpm

COPY package*.json ./
RUN pnpm install

COPY . .

RUN pnpm build

# Runner stage
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

# Install pnpm again for runner
RUN npm install -g pnpm

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["pnpm", "start"]