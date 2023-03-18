FROM nginx

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY .htpasswd /etc/nginx/.htpasswd
RUN chmod 777 /etc/nginx/.htpasswd

RUN groupadd --gid 1000 "domainusers"
RUN useradd -l --uid 1000 --gid 1000 --shell /bin/bash --create-home ubuntu


## add permissions for nginx user
RUN chown -R 1000 /var/cache/nginx && \
        chown -R 1000 /var/log/nginx && \
        chown -R 1000 /etc/nginx/nginx.conf && \
        chown -R 1000 /etc/nginx/conf.d && \
        chown -R 1000 /etc/nginx/.htpasswd
RUN touch /var/run/nginx.pid && \
        chown -R 1000 /var/run/nginx.pid

USER ubuntu
