# Use Node.js as the base image
FROM node:18 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy the entire project
COPY . .

# Set API endpoint at build time
ARG BACKEND_API_ENDPOINT
ENV BACKEND_API_ENDPOINT=${BACKEND_API_ENDPOINT}

# Build the React app
RUN npm run build

# Use Nginx to serve the build files
FROM nginx:alpine

# Copy build output to Nginx serving directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
