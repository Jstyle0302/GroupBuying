from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from groupbuying.models import Product, CustomerInfo

MAX_UPLOAD_SIZE = 2500000

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'image']
        # widgets = {
        #     'description': Textarea(attrs={'cols': 80, 'rows': 20}),
        # }
    def clean_picture(self):
        image = self.cleaned_data['image']
        if not image:
            raise forms.ValidationError('You must upload a image')
        if not image.content_type or not image.content_type.startswith(
                'image'):
            raise forms.ValidationError('File type is not image')
        if image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(
                'File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return image

class VendorInfoForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'cols': 70, 'rows': 5})}

    def clean_picture(self):
        image = self.cleaned_data['image']
        if not image:
            raise forms.ValidationError('You must upload a image')
        if not image.content_type or not image.content_type.startswith(
                'image'):
            raise forms.ValidationError('File type is not image')
        if image.size > MAX_UPLOAD_SIZE:
            raise forms.ValidationError(
                'File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE))
        return image


class LoginForm(forms.Form):
    username = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username',
                'class': 'form-control',
                'id': 'id_username'}))  # id = id_username
    password = forms.CharField(
        label="",
        max_length=200,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control',
                'id': 'id_password'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Invalid username or password")

        # We must return the cleaned data we got from our parent.
        return cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(
        label="",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username',
                'class': 'form-control',
                'id': 'id_username'}))
    password = forms.CharField(
        label="",
        max_length=200,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password',
                'class': 'form-control',
                'id': 'id_password'}))
    confirm_password = forms.CharField(
        max_length=200,
        label="",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm password',
                'class': 'form-control',
                'id': 'id_password2'}))
    first_name = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'First name',
                'class': 'form-control',
                'id': 'id_firstname'}))
    last_name = forms.CharField(
        label="",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Last name',
                'class': 'form-control',
                'id': 'id_lastname'}))
    email = forms.CharField(
        label="",
        max_length=50,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'E-mail',
                'class': 'form-control',
                'id': 'id_email'}))
    cell_phone = forms.CharField(
        label="",
        max_length=16,
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Cell phone',
                'class': 'form-control',
                'id': 'id_phone'}))
    address = forms.CharField(
        label="",
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Address',
                'class': 'form-control',
                'id': 'id_address'}))

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super().clean()

        # Confirms that the two password fields match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords did not match.")

        # We must return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # We must return the cleaned data we got from the cleaned_data
        # dictionary
        return username
