upstream app-gitea {
    server gitea:3000;
}

server {
    listen 80;
    server_name git.mydomain.com;
    root /var/www/sites/git/;

    location /.well-known/acme-challenge/ {
        alias /var/www/sites/git/.well-known/acme-challenge/;
    }

    location / {
        return 301 https://$host$request_uri;
    }

}

server {
    listen 443 ssl http2;
    server_name git.mydomain.com;
    root /var/www/site/;

    ssl_certificate /etc/letsencrypt/live/git.mydomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/git.mydomain.com/privkey.pem;

    #ssl_stapling on;
    #ssl_stapling_verify on;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA';
    ssl_prefer_server_ciphers on;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets on;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

    resolver 8.8.8.8;

    server_tokens off;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security max-age=15768000;

    error_page 404 = /404.htm;

    location / {
        proxy_set_header Host             $host;
        proxy_set_header X-Real-IP        $remote_addr;
        proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;

        #max_body_size will allow you to upload a large git repository
        client_max_body_size 100M;

        #to resolve err-content-length-mismatch also breaks http clone
        proxy_max_temp_file_size 0;
        proxy_pass http://app-gitea;
    }

}
