"""
2. Delete the database (rm db.sqlite3)
3. Delete the migrations (rm -fr <appname>/migrations)
4. Make migrations (python manage.py makemigrations <appname>)
5. Migrate (python manage.py migrate)
"""
import os
import shutil

# remove db.sqlite3
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
else:
    print("db.sqlite3 does not exist")

# remove directory groupbuying/migrations/
if os.path.exists("./groupbuying/migrations"):
    shutil.rmtree('./groupbuying/migrations')
else:
    print("groupbuying/migrations does not exist")

os.system("python manage.py makemigrations")
os.system("python manage.py migrate")