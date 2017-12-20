# Superset install

## Initial install

This document assumes you're using an Ubuntu/Debian build, and Aptitude as your package manager.

### Local DB installation and setup

 - It's important to create the local DB cluster before installing superset, so as to prevent mistakenly working on the sqlite installation (and having to painstakingly re-write everything: Superset [as of version 0.22.1] doesn't have a simple way to migrate all dashboards and slices)

    ```
    sudo apt-get install -y mysql-server
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
    sudo mkdir -p /opt/superset && sudo chown -r $USER:root /opt/superset && cd /opt/superset
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
    sed -i "/SECRET_KEY/d" superset_config.py
    sed -i "/Your App ssecretkey/a\\${SECRET_KEY}" superset_config.py
    ``` 

 - Create virtualenv and install superset
    
    It's highly recommended to run Superset with Python 2.7. Superset officially supports 3.2, 3.3, 3.4. Keep in mind that different distributions call the system-wide python 2 installation differently.

    ```
    python -m virtualenv venv && source venv/bin/activate
    pip install superset
    ```

    Install: database dependencies (mysql in this case, see: [here](https://superset.incubator.apache.org/installation.html#database-dependencies) (github.com) for more information on SqlAlchemy dependencies (github.com)), and others (caching, etc)

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
