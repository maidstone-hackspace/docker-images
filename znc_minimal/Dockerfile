FROM alpine:latest
MAINTAINER Oliver Marks

RUN apk add --update ca-certificates znc g++ git make openssl-dev znc-dev \
    && git clone https://github.com/jpnurmi/znc-clientbuffer.git /root/znc-clientbuffer \
    && git clone https://github.com/jreese/znc-push.git /root/znc-push \
    && cd /root/znc-push && make && cp push.so /usr/lib/znc \
    && cd /root/znc-clientbuffer && znc-buildmod clientbuffer.cpp \
    && cp clientbuffer.so /usr/lib/znc \
    && apk del --purge g++ git make openssl-dev \znc-dev \
    && rm -rf /var/cache/apk/* /root/znc-push /root/znc-clientbuffer

USER znc

CMD ["znc", "--foreground", "--datadir", "/etc/znc"]

#run the below to get going quickly selecting port 8000 when asked

# docker build -t olymk2/znc .
# docker run -it --rm -v /etc/znc:/etc/znc olymk2/znc znc --datadir=/etc/znc --makeconf
# docker run -d -p 8000:8000 -v /etc/znc:/etc/znc --name=znc olymk2/znc
