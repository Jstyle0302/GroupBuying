"""
1. Delete the database (rm db.sqlite3)
2. Delete the migrations (rm -fr <appname>/migrations)
3. Make migrations (python manage.py makemigrations <appname>)
4. Migrate (python manage.py migrate)
"""
import os
import shutil

# # remove db.sqlite3
# if os.path.exists("db.sqlite3"):
#     os.remove("db.sqlite3")
# else:
#     print("db.sqlite3 does not exist")

# # remove directory groupbuying/migrations/
# if os.path.exists("./groupbuying/migrations"):
#     shutil.rmtree('./groupbuying/migrations')
# else:
#     print("groupbuying/migrations does not exist")

os.system("python manage.py makemigrations groupbuying")
os.system("python manage.py migrate")
