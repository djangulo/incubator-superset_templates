# Superset deployment instructions

## Initial install

This document assumes you're using an Ubuntu/Debian build, and Aptitude as your package manager.

### Local DB installation and setup

 - It's important to create the local DB cluster before installing superset, so as to prevent mistakenly working on the sqlite installation (and having to painstakingly re-write everything: Superset [as of version 0.22.1] doesn't have a simple way to migrate all dashboards and slices)

    ```
    sudo apt-get install -y mysql-server libmysqlclient-dev
    ```
    It will ask you for a root password, set it accordingly, then run
    ```
    mysql_secure_installation
    ```
    Select:
    - Password validator plugin: Y
    - Password validator strength: 1
    - Change root password: Y if it doesn't meet it
    - Remove anonymous users: Y
    - Disallow root login remotely: Y
    - Remove test database: Y
    - Reload privileges: Y

    Next up:
    ```
    user@host:~$ sudo mysql -u root -p
    mysql> CREATE DATABASE superset;
    mysql> CREATE USER superset_admin IDENTIFIED BY 'password';
    mysql> GRANT ALL PRIVILEGES ON superset.* TO superset_admin;
    mysql> FLUSH PRIVILEGES;
    mysql> exit;
    ```

### Caching

 - Install redis for caching

    ```
    sudo apt-get install redis-server
    ```

    Test it:

    ```
    redis-cli ping
    PONG
    ```

    For a regular superset installation, defaults are fine.

### Installing superset

 - Create superset dir, change ownership and switch to it

    ```
    sudo mkdir -p /opt/superset && sudo chown -R $USER:root /opt/superset && cd /opt/superset
    ```

    The commands that follow assume you're in the /opt/superset directory

 - Create a config file for superset to run with. or simply download the raw template from [this link](https://github.com/djangulo/incubator-superset_templates/blob/master/superset_config.py) (github.com)

    ```
    wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/superset_config.py
    ```

- Generate a `secrets.py` file, with a `SECRET_KEY` (if doesn't already exist).
- [Generator file link](https://github.com/djangulo/incubator-superset_templates/blob/master/gen_secret_key.py) (github.com), and insert it into superset config

    ```
    touch __init__.py
    wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/gen_secret_key.py
    python gen_secret_key.py
    export SECRET_KEY_LINE=$(eval "cat secrets.py | grep SECRET_KEY")
    sed -i "s/SECRET_KEY/#SECRET_KEY/g" superset_config.py
    sed -i "/Your App secret key/a\\${SECRET_KEY_LINE}" superset_config.py
    ``` 

 - Create virtualenv and install superset
    
    It's highly recommended to run Superset with Python 2.7. Superset officially supports 3.2, 3.3, 3.4. Keep in mind that different distributions call the system-wide python 2 installation differently.

    ```
    python -m virtualenv venv && source venv/bin/activate
    pip install superset
    ```

    Install: database dependencies (mysql in this case, see: [here](https://superset.incubator.apache.org/installation.html#database-dependencies) (github.com) for more information on SqlAlchemy dependencies), and others (caching, etc)

    ```
    pip install mysqlclient redis gevent
    ```
    
    Modify `superset_config.py` with the uri created earlier

    ```
    sed -i '/SQLALCHEMY_DATABASE_URI/d' superset_config.py
    sed -i "/SQLALCHEMY_SED_HOOK/a \SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://superset_admin:password@localhost/superset'" superset_config.py
    ```

    Create and admin user:

    ```
    fabmanager create-admin --app superset
    ```

    Upgrade the superset db and initialize it

    ```
    superset db upgrade && superset init
    ```

    Optionally, load example dashboards into the db

    ```
    superset load_examples
    ```

### Upgrading superset

From the [docs](https://superset.incubator.apache.org/installation.html#upgrading): Upgrading should be as straightforward as running:

```
pip install superset --upgrade
superset db upgrade
superset init
```

## Server

Server runs with a systemd service for gunicorn, reverse-proxying to nginx. Use an environment variable to set SITENAME to the domain name.

### Set up gunicorn's systemd server
```
export SITENAME=superset.address.com
```

- Download the gunicorn-systemd template from [here](https://github.com/djangulo/incubator-superset_templates/blob/master/gunicorn-systemd.template.service) (github.com)

```
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/gunicorn-systemd.template.service
```

Rename the file, and modify it to contain the server address details and user

```
mv gunicorn-systemd.template.service gunicorn-$SITENAME.service
sed -i "s/SITENAME/$SITENAME/g" gunicorn-$SITENAME.service
sed -i "s/USERNAME/$USER/g" gunicorn-$SITENAME.service
```

Create log dir and files and change their ownership

```
sudo mkdir -p /var/log/superset
touch /var/log/superset/error.log
touch /var/log/superset/access.log
sudo chown -R $USER:root /var/log/superset
```

Move the systemd file to `/etc/systemd/system/`, reload daemon, enable and start the service

```
sudo mv gunicorn-$SITENAME.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn-$SITENAME.service
```

### Set up nginx's reverse proxy to gunicorn, and ssl

Replace proper values here, we'll use these environment variables extensively
```
export USEREMAIL=your.email@website.com
export SITENAME=superset.address.com
```

Download:
 - ssl-params [here](https://github.com/djangulo/incubator-superset_templates/blob/master/ssl-params.conf)
 - ssl-template template file [here](https://github.com/djangulo/incubator-superset_templates/blob/master/ssl-template.conf)
 - nginx template file [here](https://github.com/djangulo/incubator-superset_templates/blob/master/gunicorn-nginx.template.conf)
 - letsencrypt domain template file [here](https://github.com/djangulo/incubator-superset_templates/blob/master/letsencrypt-domain.template.conf)
 - letsencrypt cron job to renew certs [here](https://github.com/djangulo/incubator-superset_templates/blob/master/renew-letsencrypt-template.sh)

```
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/ssl-template.conf
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/ssl-params.conf
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/gunicorn-nginx.template.conf
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/letsencrypt-domain.template.conf
wget https://raw.githubusercontent.com/djangulo/incubator-superset_templates/master/renew-letsencrypt-template.sh
```

Build Diffie-Hellman key exchange parameters, if they don't already exist:

```
openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
```

The next block is a blast-through install of certbot and a lets-encrypt certificate:

```
sudo git clone https://github.com/certbot/certbot /opt/letsencrypt
sudo cd /opt/letsencrypt && git pull origin master
sudo mkdir -p /var/www/letsencrypt
sudo chgrp www-data /var/www/letsencrypt
sudo chmod -R 755 /var/www/letsencrypt
```

Install nginx and remove the default page
```
sudo apt-get install nginx
sudo rm /etc/nginx/sites-enables/default.conf
sudo mv /etc/nginx/sites-available/default.conf /etc/nginx/sites-available/default.bak
```

Modify, rename and move `gunicorn-nginx.template.conf` to it's new home:

```
sed "
```



