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
postgres=# ALTER ROLE nels885 SET default_transaction_isolation TO 'read commited';
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
$ pipenv install --dev
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

