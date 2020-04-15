from groupbuying.forms import LoginForm, RegistrationForm, ProductForm, VendorInfoForm, CustomerInfoForm
from groupbuying.models import Product, CustomerInfo, VendorInfo, Rating, UserProfile, OrderUnit, OrderBundle, Category


def create_profile(backend, user, response, *args, **kwargs):
    if len(CustomerInfo.objects.all()) > 0 and CustomerInfo.objects.get(customer_id=user.id):
        return

    new_customerInfo = CustomerInfo(name=response.get('name'),
                                    email=response.get('email'),
                                    description="",
                                    address=response.get('locale'),
                                    customer_id=user.id)
    new_customerInfo.save()

    new_vendorInfo = VendorInfo(name=response.get('name'),
                                email=response.get('email'),
                                description="",
                                address=response.get('locale'),
                                vendor_id=user.id)

    if backend.name == "google-oauth2":
        new_vendorInfo.image_url_OAuth = response.get('picture')

    new_vendorInfo.save()

    new_userProfile = UserProfile(user=user,
                                  CustomerInfo=new_customerInfo,
                                  VendorInfo=new_vendorInfo)
    new_userProfile.save()