
# Installation  

```
python -m venv venv

# linux
source venv/bin/activate

#windows
venv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py runserver
```

# Usefull

Please always create new branch, and never push on main !!!

```
# new branch
git checkout -b {branch_name}

# change branch
git checkout {branch_name}

# pull from remote
git pull origin {branch_name}

# push to remote
git push origin {branch_name}

# delete branch
git branch -D {branch_name}

```