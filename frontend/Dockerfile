# Frontend Dockerfile
FROM node:20-bullseye

WORKDIR /app

# Set environment variables with default values
ENV VITE_API_BASE_URL=http://backend:8000
ENV VITE_DEFAULT_USER_ID=admin

COPY package.json /app/
RUN npm install

COPY ./ /app/

# Build command for production or development mode
CMD ["npm", "run", "dev", "--", "--host"]