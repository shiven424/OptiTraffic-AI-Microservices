FROM node:14
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ENV REACT_APP_API_URL=http://api_gateway
ENV REACT_APP_WS_URL=ws://api_gateway/ws
EXPOSE 3000
CMD ["npm", "start"]
