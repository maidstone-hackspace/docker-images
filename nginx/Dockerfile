FROM olymk2/website_base

RUN apk add --no-cache --update nginx openssl

RUN mkdir -p /tmp/nginx/client-body
RUN mkdir -p /run/nginx/

COPY start_nginx.sh /
COPY nginx.conf /etc/nginx/

RUN chmod +x /start_nginx.sh
RUN python3 caretaker.py &

EXPOSE 80
RUN adduser nginx www-data

#CMD ["nginx", "-g", "daemon off;"]
ENTRYPOINT /start_nginx.sh

# docker build --no-cache -t olymk2/nginx .
# docker run -d -p 80:80 -p 443:443 -v /etc/nginx/sites-enabled/:/etc/nginx/sites-enabled/ --name=nginx olymk2/nginx

