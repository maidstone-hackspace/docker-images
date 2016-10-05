#!/bin/python3
import pwd
import grp
import gzip
import glob
import time
from os import W_OK, makedirs, getenv, environ, chown, access
from os.path import exists
from subprocess import check_output, Popen, PIPE, STDOUT

def mysql_command_pipe(cmd1, cmd2, filename, stdin):
    print("\tProcessing %s" % filename)
    process1 = Popen(cmd1, stdin=stdin if stdin else PIPE, stdout=PIPE)
    process2 = Popen(cmd2, stdin=process1.stdout)
    process2.communicate()

def mysqld_command(cmd):
    try:
        print("Running %s" % ' '.join(cmd))
        process = Popen(cmd)
        time.sleep(4)
        return process
    except Exception as e:
        print('mysqld exception')
        print(e)
    return None

def mysql_command(cmd, sql=None, close=True, redirect_cmd=None):
    try:
        print("Running %s" % ' '.join(cmd))
        process = Popen(cmd, stdin=PIPE)

        if sql is None and close is True:
            process.wait()
            return process

        if sql:
            print(sql)
            process.communicate(bytes(sql, 'UTF-8'))
        return process
    except Exception as e:
        print(e)
    return None

# lets do some pre flight checks
if not exists('/run/mysqld'):
    makedirs('/run/mysqld')

if not exists('/var/lib/mysql'):
    makedirs('/var/lib/mysql')

chown('/run/mysqld', pwd.getpwnam("mysql").pw_uid, grp.getgrnam("mysql").gr_gid)
chown('/var/lib/mysql', pwd.getpwnam("mysql").pw_uid, grp.getgrnam("mysql").gr_gid)

if not access('/var/lib/mysql', W_OK):
    print('Permission denied on /var/lib/mysql, your mounted volume is probably not writable')

if not access('/run/mysqld', W_OK):
    print('Permission denied on /run/mysqld, your mounted volume is probably not writable')


db_root_passwd = getenv('MYSQL_ROOT_PASSWORD', check_output(['pwgen', '16', '1']))
db_passwd = getenv('MYSQL_PASSWORD', '')
db_user = getenv('MYSQL_USER', '')
db_database = getenv('MYSQL_DATABASE', '')
db_bulk = getenv('MYSQL_BULK', '')

sql_clean_db = [
    "DROP DATABASE test;",
    "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"]

sql_users = ["USE mysql;"]
if db_bulk:
    bulk_create = db_bulk.split('|')
    bulk_it = iter(bulk_create)
    for bulk_db, bulk_user, bulk_password in zip(bulk_it, bulk_it, bulk_it):
        sql_users.append("CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8 COLLATE utf8_general_ci;" % (bulk_db))
        sql_users.append("GRANT ALL ON `%s`.* to '%s'@'%%' IDENTIFIED BY '%s';" % (bulk_db, bulk_user, bulk_passwd))
        sql_users.append("GRANT ALL ON `%s`.* to '%s'@'localhost' IDENTIFIED BY '%s';" % (bulk_db, bulk_user, bulk_passwd))

if db_database:
    sql_users.append("CREATE DATABASE IF NOT EXISTS `%s` CHARACTER SET utf8 COLLATE utf8_general_ci;" % (db_database))
if db_user:
    sql_users.append("GRANT ALL ON `%s`.* to '%s'@'%%' IDENTIFIED BY '%s';" % (db_database, db_user, db_passwd))
    sql_users.append("GRANT ALL ON `%s`.* to '%s'@'localhost' IDENTIFIED BY '%s';" % (db_database, db_user, db_passwd))
sql_users.append("FLUSH PRIVILEGES;")
sql_users.append("EXIT")

sql_root_user = ["USE mysql;"]
sql_root_user.append("UPDATE user SET password=PASSWORD(\"%s\") WHERE user='root';" % db_root_passwd)
sql_root_user.append("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;")
sql_root_user.append("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'onmrcCMovW7Yo' WITH GRANT OPTION;")
sql_root_user.append("EXIT")

print('Initalising MariaDB.')
result = mysql_command(['mysql_install_db', '--user=mysql', '--console'])
print('MariaDB Initalised.')

print('Starting MariaDB temporarily to set root password')
mariadb = mysqld_command(['/usr/bin/mysqld', '--user=mysql', '--skip-grant-tables'])
mysql_command(['/usr/bin/mysql', '--user=root'], sql="\n".join(sql_root_user)+"\n")
mariadb.kill()

print('Starting MariaDB service')
mariadb = mysqld_command(['/usr/bin/mysqld', '--user=mysql'])
print('Setting up database and users.')
mysql_command(['/usr/bin/mysql', '--user=root', '--password=%s' % db_root_passwd], sql="\n".join(sql_users)+"\n")
mysql_command(['/usr/bin/mysql', '--user=root', '--password=%s' % db_root_passwd], sql="\n".join(sql_clean_db)+"\n")

print('Importing any .sql files in /docker-entrypoint-initdb.d/')
[mysql_command_pipe(['cat'], ['/usr/bin/mysql', '-uroot', '-p%s' % db_root_passwd, db_database], filename=filename, stdin = open(filename)) for filename in glob.glob('/docker-entrypoint-initdb.d/*.sql')]

print('Importing any .sql.gz files in /docker-entrypoint-initdb.d/')
[mysql_command_pipe(['/bin/gunzip'], ['/usr/bin/mysql', '-uroot', '-p%s' % db_root_passwd, db_database], filename=filename, stdin = open(filename)) for filename in glob.glob('/docker-entrypoint-initdb.d/*.sql.gz')]

if getenv('MYSQL_ROOT_PASSWORD') is None:
    print("Root password not supplied using %s" % db_root_passwd)

# lets clear out the passwords from the environment vars and memory now we are finished
db_root_passwd = db_database = db_user = db_passwd = None
environ['MYSQL_ROOT_PASSWORD'] = ''
environ['MYSQL_PASSWORD'] = ''
environ['MYSQL_USER'] = ''
environ['MYSQL_DATABASE'] = ''
environ['MYSQL_BULK'] = ''

print('MariaDB ready to rock and roll!')
mariadb.wait()
print('Launching MariaDB Failed, or process exited mysteriously :(')
