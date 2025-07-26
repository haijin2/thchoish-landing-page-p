# Use official NGINX image
FROM nginx:alpine

# Remove default nginx html
RUN rm -rf /usr/share/nginx/html/*

# Static files to nginx folder
COPY build/ /usr/share/nginx/html

#.exe file
# COPY CipherCap.exe /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
