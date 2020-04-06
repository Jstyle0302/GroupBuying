from django.db import models
from django.contrib.auth.models import User

'''
# install the following packages if compile error with PhoneNumberField
# pip install django-phonenumber-field
# pip install phonenumbers
from phonenumber_field.modelfields import PhoneNumberField
'''



class CustomerInfo(models.Model):
    # CustomerInfo.name is different from UserProefile.firstName or
    # UserProefile.lastName, can be user name or vendor name
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    address = models.CharField(max_length=100)
    phoneNum = models.CharField(max_length=16)
    picture = models.FileField(blank=False)

    def __str__(self):
        return 'id=' + str(self.id) + ',name=' + self.name + ',email=' + self.email + \
            ',address=' + str(self.address) + ',phoneNum=' + str(self.phoneNum)


class VendorInfo(models.Model):
    # VendorInfo.name is different from UserProefile.firstName or
    # UserProefile.lastName, can be user name or vendor name
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phoneNum = models.CharField(max_length=16)
    tagList = models.CharField(max_length=200)

    def __str__(self):
        return 'id=' + str(self.id) + ',name=' + self.name + ',email=' + self.email + \
            ',address=' + str(self.address) + ',phoneNum=' + str(self.phoneNum)

class Category(models.Model):
    name = models.CharField(max_length=50)
    vendor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    sellerId = models.CharField(max_length=10)  # Note: == vendor.id?
    isAvailable = models.BooleanField(default=True)
    saleVolume = models.IntegerField()
    image = models.FileField(blank=False, upload_to='img/') # Note: use ImageField?
    content_type = models.CharField(max_length=50, default="")
    vendor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)  # Note: use User instead?
    category = models.ForeignKey(Category, null=True, on_delete=models.CASCADE)  # Note: use User instead?

    def __str__(self):
        return 'id=' + str(self.id) + ',name=' + self.name + ',description=' + self.description +  \
            ',price=' + str(self.price) + ',seller_id=' + self.sellerId + ',isAvailable=' + str(self.isAvailable)


class Rating(models.Model):
    rating = models.FloatField()
    rater = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)
    ratedTarget = models.ForeignKey(VendorInfo, on_delete=models.CASCADE)


class UserProfile(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    CustomerInfo = models.OneToOneField(CustomerInfo, on_delete=models.CASCADE)
    VendorInfo = models.OneToOneField(VendorInfo, on_delete=models.CASCADE)

    def __str__(self):
        return 'id=' + str(self.id) +  \
            ', username="' + self.user.username + '"' \
            ', first_name="' + self.user.first_name + '"' \
            ', last_name="' + self.user.last_name + '"'


class OrderUnit(models.Model):
    buyer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=10)
    comment = models.CharField(max_length=100)
    orderTime = models.TimeField()
    orderDate = models.DateField()
    deliverTime = models.TimeField()
    deliverDate = models.DateField()
    isPaid = models.BooleanField(default=False)
    orderbundle = models.ForeignKey('OrderBundle',
                                    related_name='order_Unit',
                                    on_delete=models.CASCADE)

    def __str__(self):
        return 'id=' + str(self.id) + ',buyer=' + self.buyer + \
            ',num=' + self.num + ',comment=' + str(self.comment)


class OrderBundle(models.Model):
    holder = models.ForeignKey('CustomerInfo', on_delete=models.CASCADE)
    vendor = models.ForeignKey('VendorInfo', on_delete=models.CASCADE)

    def __str__(self):
        return 'id=' + str(self.id) + ',buyer=' + self.buyer + \
            ',num=' + self.num + ',comment=' + str(self.comment)

# class UserItem(models.Model):
#     text = models.CharField(max_length=200)
#     profile_picture = models.FileField(blank=True)
#     bio_input_text = models.TextField(max_length=500)
#     user_id = models.IntegerField()
#     user_name = models.CharField(max_length=50)
#     email = models.CharField(max_length=50)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     cell_phone = models.CharField(max_length=16)
#     address = models.CharField(max_length=200)
#     followers = models.ManyToManyField(User)

#     # content_type = models.CharField(max_length=50)
#     # ip_addr = models.GenericIPAddressField()
#     # storage_path = models.FileField()

#     def __str__(self):
#         return 'id=' + str(
#             self.id
#         ) + ',first_name="' + self.first_name + 'last_name' + self.last_name
