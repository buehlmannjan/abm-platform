#Download base image node
FROM node

# install NPM dependencies
COPY package*.json ./
RUN npm install

# copy server
COPY server server

# expose port
EXPOSE 9000

# do not run as root
USER node

# launch server
CMD ["npm", "start"]

