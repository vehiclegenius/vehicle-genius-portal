# Setup instructions for server

Assumptions:

- Running on a DigitalOcean Ubuntu droplet
- Using supervisorctl for managing the process
- All is running on `dimo` user

## Dependencies

- Python 3+

## Nginx

```shell
sudo apt-get update
sudo apt-get install nginx
sudo cp nginx.conf /etc/nginx/sites-available/vehicle-genius-portal
sudo ln -s /etc/nginx/sites-available/vehicle-genius-portal /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## Virtualenv

```shell
pip3 install virtualenv
virtualenv .pyenv
```

## supervisorctl

```shell
sudo apt-get update
sudo apt-get install supervisor
sudo cp supervisorctl.conf /etc/supervisor/conf.d/vehicle-genius-portal.conf
```

## Configuration

```shell
cp .env.example .env
```

Configure as appropriate.

## portal access

```shell
python3 manage.py createsuperuser
```
