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
python manage.py db init
# go create a database and then
python manage.py db migrate
python manage.py db upgrade
cp .secret.example .secret
# go edit .secret
```
