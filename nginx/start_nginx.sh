if [ ! -f /etc/ssl/certs/dhparam.pem ]
then
  openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048
fi
python3 caretaker.py &
nginx -g 'daemon off;'
