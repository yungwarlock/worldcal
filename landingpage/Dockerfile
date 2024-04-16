FROM node:lts-bullseye-slim as base

RUN apt update && \
	apt install -y ca-certificates && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

FROM base as builder

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn --frozen-lockfile

COPY . .

RUN yarn build


FROM base

WORKDIR /app

COPY --from=builder /app/.next /app/.next

COPY . .

WORKDIR /app

RUN yarn --production && \
  yarn cache clean --all

ENTRYPOINT [ "/app/start.sh" ]

CMD ["yarn", "start"]