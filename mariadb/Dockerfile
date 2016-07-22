FROM olymk2/website_base
MAINTAINER Oliver Marks

#RUN apk --update --no-cache add python3 mariadb mariadb-client pwgen
RUN apk --update --no-cache add mariadb mariadb-client pwgen

ADD scripts/ /scripts
ADD scripts/run_mariadb.py /sbin/run_mariadb.py
RUN mkdir /scripts/pre-exec.d && \
mkdir /scripts/pre-init.d && \
chmod -R 755 /scripts

EXPOSE 3306

VOLUME ["/var/lib/mysql"]

ENTRYPOINT ["python3", "/sbin/run_mariadb.py"]

# docker build -t olymk2/mariadb .
# docker run -d \ 
#    -e MYSQL_ROOT_PASSWORD=changemenow \ 
#    -v /mnt/sda1/var/mysql_data:/var/lib/mysql \ 
#    -e MYSQL_USER=test_user \ 
#    -e MYSQL_PASSWORD=test_pass \ 
#    -e MYSQL_DATABASE=test_db \ 
#    -p 3306:3306 \ 
#    --name mariadb olymk2/mariadb

