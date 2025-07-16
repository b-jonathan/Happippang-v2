# syntax=docker.io/docker/dockerfile:1

#############################
# 1 ─── Dependencies (shared)
#############################
FROM node:20-alpine AS deps
WORKDIR /app
# Some native libs (e.g. Prisma, sharp) need glibc compatibility
RUN apk add --no-cache libc6-compat
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps

#############################
# 2 ─── Build (prod bundle)  
#############################
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run lint && npm run build          # creates .next/

###########################################
# 3 ─── Runtime (production, smallest img)
###########################################
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# copy exactly what Next.js needs at run-time
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]                       # ↔ `next start`

###########################################
# 4 ─── Dev (hot-reload, optional target)
###########################################
FROM node:20-alpine AS dev
WORKDIR /app
ENV WATCHPACK_POLLING=true               
COPY --from=deps /app/node_modules ./node_modules
COPY . .
CMD ["npm", "run", "dev"]                  # ↔ `next dev`
