# csd_dashboard

[![Build Status](https://travis-ci.org/Nels885/csd_dashboard.svg?branch=master)](https://travis-ci.org/Nels885/csd_dashboard)

Dashboard create with Django 3.1.1 or 3.x for the CSD service of the company Faurecia Clarion Electronics

## Start guide

### Dependencies

- [Python 3.6 or more](https://www.python.org/) is required
- [PostgreSQL](https://www.postgresql.org/download/)

### Installing the Linux development environment

Install Python 3.6 or more, PostgreSQL and linux packages useful for the
proper functioning of the application.

```bash
$ sudo apt update
$ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib git
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

### Environment variables

two variables must be created for the recovery of Corvet data from the
website, as below, and added to the file **/etc/environment/**

```bash
export USER_CORVET="<username>"
export PWD_CORVET="<password>"
```

### Starting the server

To launch the application, simply execute the following commands

```bash
$ pipenv shell
$ ./manage.py runserver
```

You can now access your application from your browser at "localhost: 8000"