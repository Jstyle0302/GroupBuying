# team23
Website link: http://ec2-18-191-21-131.us-east-2.compute.amazonaws.com/groupbuying/

Final presentaion: https://docs.google.com/presentation/d/1BDxbyl8OHBT2B5KBGfb4mzyAbBk8woZhDKaLX5LLz2Y/edit?usp=sharing

Sprint #1 Presentation link: https://docs.google.com/presentation/d/1a4ASrTPqu-wAwuPuVu2xb9VW79v-2UeRojcAiPfRZDA/edit?usp=sharing

Proposal link: https://docs.google.com/document/d/1NdTe2fYgq8__nJ3FEP98KG_uEWeCL9cmPIb3NeHwVME/edit?usp=sharing


How to run groupbuying
1. pip install social-auth-app-django (OAuth libaray)
2. pip install jsonfield
3. python manage.py runserver

(Optional for https)
1. Install SSL server libaray: pip install django-sslserver
2. add 'sslserver' in INSTALLED_APPS in setting.py
3. Run: python manage.py runsslserver
