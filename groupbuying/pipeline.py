from groupbuying.forms import LoginForm, RegistrationForm, ProductForm, VendorInfoForm, CustomerInfoForm
from groupbuying.models import Product, CustomerInfo, VendorInfo, Rating, UserProfile, OrderUnit, OrderBundle, Category


def create_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        pass
    if CustomerInfo.objects.get(customer_id=user.id):
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
                                image_url=response.get('picture'),
                                vendor_id=user.id)
    new_vendorInfo.save()

    new_userProfile = UserProfile(user=user,
                                  CustomerInfo=new_customerInfo,
                                  VendorInfo=new_vendorInfo)
    new_userProfile.save()