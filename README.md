# team23
Repository for team23

Sprint #1 Presentation link: https://docs.google.com/presentation/d/1a4ASrTPqu-wAwuPuVu2xb9VW79v-2UeRojcAiPfRZDA/edit?usp=sharing

Proposal link: https://docs.google.com/document/d/1NdTe2fYgq8__nJ3FEP98KG_uEWeCL9cmPIb3NeHwVME/edit?usp=sharing


How to run groupbuying
1. pip install social-auth-app-django (OAuth libaray)
2. pip install jsonfield
3. Run: python manage.py runserver --insecure

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

Charles:
2020/4/14
1. order的summary現在每項單品都會有summary，最後再一個total price
2.現在要真的點checkout，order的東西才會出現在購物車
3.跟團的人現在可以下comment，comment會show在shopcart那邊的order page；holder也可以下comment，會在最後送給shopper的mail裡show出來
4.Search那邊現在會show真正的vendor img，但我用vendor.image.url 好像沒連到shop edit sumbit過後的image=>再麻煩Shine幫看一下那個field
5.現在寫了一個簡易版的rating，因為shop還沒傳id，沒辦法分現在是哪個vendor的shop，我是直接用current user的shop當rating target，直接在review那邊打分數後submit，現在search 可以看到update後的rating
