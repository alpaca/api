Setup
------
```
git clone git@github.com:alpaca/api.git
cd api
git submodule update --init
cd lib/socialscraper
git checkout master
cd ../identityresolver
git checkout master
cd ../..
pip install -r requirements.txt
# go create a database and then
python manage.py db upgrade
cp .secret.example .secret
# go edit .secret
```

Workon Alpaca
----------------------
```
workon alpaca
git pull 
git submodule update --recursive
```

Deploy Dokku
-----------------------
```
git remote add api dokku@alpaca.io:api
git push api master

dokku postgresql:create api
dokku rabbitmq:create api
dokku config:set api C_FORCE_ROOT=True
dokku run api python manage.py db upgrade
```

Backup Database
---------------
```
pg_dump -a -inserts alpaca_api_development  --schema=public > alpaca_api_development.text.backup

pg_dump -a -inserts --table="facebook_pages" alpaca_api_development  --schema=public > facebook_pages.text.backup
pg_dump -a -inserts --table="facebook_users" alpaca_api_development  --schema=public > facebook_users.text.backup
pg_dump -a -inserts --table="facebook_pages_users" alpaca_api_development  --schema=public > facebook_pages_users.text.backup

```