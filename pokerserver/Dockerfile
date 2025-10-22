FROM node:18

WORKDIR /app

COPY package.json package-lock.json* /app/
RUN npm install

COPY . /app

EXPOSE 3000

ENV REACT_APP_API_BASE="http://localhost:8000"

CMD ["npm", "start"]