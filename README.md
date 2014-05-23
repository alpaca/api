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
source .secret
```

Deploy Dokku
-----------------------
```
git remote add api dokku@alpaca.io:api
git push api master

# log into dokku

sudo apt-get install postgresql-client-common postgresql-client-9.1

dokku postgresql:create api
dokku rabbitmq:create api
dokku config:set api C_FORCE_ROOT=True
dokku run api python manage.py db upgrade

wget https://dl.dropboxusercontent.com/u/2623300/alpaca_api_development.text.backup
dokku postgresql:restore api < alpaca_api_development.text.backup

dokku postgresql:info api
dokku run api psql db --host=172.17.42.1 --port=xxxx --username=root --password

dokku run api python manage.py shell


```

Backup Database
---------------
```
pg_dump alpaca_api_development --schema=public > alpaca_api_development.text.backup

pg_dump -a -inserts --table="facebook_pages" alpaca_api_development  --schema=public > facebook_pages.text.backup
pg_dump -a -inserts --table="facebook_users" alpaca_api_development  --schema=public > facebook_users.text.backup
pg_dump -a -inserts --table="facebook_pages_users" alpaca_api_development  --schema=public > facebook_pages_users.text.backup

```

Analyzing Stuff with iPython
-----------------------------
http://nbviewer.ipython.org/github/jrjohansson/scientific-python-lectures/blob/master/Lecture-4-Matplotlib.ipynb


Al Code (Don't touch)
---------------------

```
users = map(lambda (user, hometown): user, map(lambda (user, hometown): (user, eval(hometown)), filter(lambda (user, hometown): hometown[0] == "{", map(lambda user: (user, user.hometown), filter(lambda user: user.hometown, FacebookUser.query)))))
```

Places where Categories Are statically Defined
----------------------------------------------
channel_by_slice.py
jsonify.py
