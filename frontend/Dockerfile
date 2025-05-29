FROM node:18-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install
COPY . .
VOLUME /dist-output
CMD ["sh", "-c", "pnpm build && cp -r /app/dist/* /dist-output"]