FROM nginx:stable

# Ten server mac dinh (ghi de bang bien moi truong trong docker-compose.yml)
ENV WEB_SERVER_ID=web-frontend-server \
    NGINX_ENVSUBST_FILTER=WEB_

RUN rm -f /etc/nginx/conf.d/default.conf
# Template -> entrypoint nginx tu dong envsubst thanh /etc/nginx/conf.d/default.conf
COPY conf.default /etc/nginx/templates/default.conf.template
COPY html/ /usr/share/nginx/html/
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
