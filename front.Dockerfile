FROM node:latest

WORKDIR /app

COPY package.json .

RUN npm install

RUN npm i -g serve

COPY . .

RUN npm run build

EXPOSE 30000

CMD [ "serve", "-s", "dist" ]
