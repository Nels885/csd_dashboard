# csd_dashboard

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/Nels885/csd_dashboard/tree/dev-cla.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/Nels885/csd_dashboard/tree/dev-cla)

Dashboard create with Django 3.2.x

## Start guide

### Dependencies

- [Python 3.8 or more](https://www.python.org/) is required
- [PostgreSQL](https://www.postgresql.org/download/)

### Installing the Linux development environment

Install Python 3.8 or more, PostgreSQL and linux packages useful for the
proper functioning of the application.

```bash
$ sudo apt update
$ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib git redis-server
$ sudo pip3 install pipenv
```

Create a database and proprietary user account for this database.

```bash
$ sudo -i -u postgres psql
psql (9.6.10)
Type "help" for help.

postgres=# CREATE DATABASE csd_atelier;
CREATE DATABASE
postgres=# CREATE USER nels885 WITH PASSWORD 'kikoulol';
CREATE ROLE
postgres=# ALTER ROLE nels885 SET client_encoding TO 'utf8';
ALTER ROLE
postgres=# ALTER ROLE nels885 SET default_transaction_isolation TO 'read committed';
ALTER ROLE
postgres=# ALTER ROLE nels885 SET timezone TO 'Europe/Paris';
ALTER ROLE
postgres=# GRANT ALL PRIVILEGES ON DATABASE csd_atelier TO nels885;
GRANT
postgres=# \q 
```

Download the repository and create the virtual environment:

```bash
$ git clone https://github.com/Nels885/csd_dashboard
$ cd csd_dashboard
$ pipenv --python 3 
$ pipenv sync --dev
```

### Starting the server

To launch the application, simply execute the following commands

```bash
$ pipenv shell
$ ./manage.py runserver
```

You can now access your application from your browser at "localhost: 8000"

### Import data

```bash
$ pipenv shell
$ ./manage.py sqlflush | ./manage.py dbshell
$ ./manage.py loaddata <DATA_FILE>
```

### Celery server

```bash
$ pipenv run celery -A sbadmin purge
$ pipenv run celery -A sbadmin worker --beat --scheduler django --loglevel=info
```

### Email testing tool for developers

To test emails during development, we use the MailHog tool, [Github link](https://github.com/mailhog/MailHog/releases).

Installation on Linux:

```bash
$ wget <MailHog_linux_amd64 release link>
$ chmod u+x MailHog_linux_amd64
$ ./MailHog_linux_amd64
2023/08/25 15:52:51 Using in-memory storage
2023/08/25 15:52:51 [SMTP] Binding to address: 0.0.0.0:1025
[HTTP] Binding to address: 0.0.0.0:8025
2023/08/25 15:52:51 Serving under http://0.0.0.0:8025/
Creating API v1 with WebPath:
Creating API v2 with WebPath:
```

### Test application

```bash
$ sudo -i -u postgres psql
psql (9.6.10)
Type "help" for help.

postgres=# ALTER USER nels885 CREATEDB;
ALTER ROLE
postgres=# \q 
```

```bash
$ pipenv run coverage run --source="." manage.py test -v 2
$ pipenv run coverage html
````
