# team23
Repository for team23

Sprint #1 Presentation link: https://docs.google.com/presentation/d/1a4ASrTPqu-wAwuPuVu2xb9VW79v-2UeRojcAiPfRZDA/edit?usp=sharing

Proposal link: https://docs.google.com/document/d/1NdTe2fYgq8__nJ3FEP98KG_uEWeCL9cmPIb3NeHwVME/edit?usp=sharing


How to run groupbuying
1. Install OAuth libaray: pip install social-auth-app-django
2. Run: python manage.py runserver

(Optional for https)
1. Install SSL server libaray: pip install django-sslserver
2. add 'sslserver' in INSTALLED_APPS in setting.py
3. Run: python manage.py runsslserver


To-do list:
1. Shop profile need to connect the shopping limit button with the model
2. Order page need to add link the description to the database and those message should be sent to shop owner
3. Shop profile page need to connect textarea input box to database.
4. Order mail page should check its css style
5. Link the data of review section in shop page with database. 
