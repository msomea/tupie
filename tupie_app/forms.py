from django import forms
from .models import Item, Region, District, Ward, Place, Street, Message, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

# SignUp form for new users
class SignUpForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'phone_number','email', 'password1', 'password2']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email is already in use.")
        return email

# UserProfile form for updating user details  
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo', 'phone_number', 'full_name', 'id_document', 'email', 'region', 'district', 'ward', 'place']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name as it appears on ID'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control'}),
            'ward': forms.Select(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initially empty queryset for dependent fields
        self.fields['district'].queryset = District.objects.none()
        self.fields['ward'].queryset = Ward.objects.none()
        self.fields['place'].queryset = Place.objects.none()

        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id).order_by('district_name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty
        elif self.instance.pk and self.instance.region:
            self.fields['district'].queryset = District.objects.filter(region=self.instance.region).order_by('district_name')

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['ward'].queryset = Ward.objects.filter(district_id=district_id).order_by('ward_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.district:
            self.fields['ward'].queryset = Ward.objects.filter(district=self.instance.district).order_by('ward_name')

        if 'ward' in self.data:
            try:
                ward_id = int(self.data.get('ward'))
                self.fields['place'].queryset = Place.objects.filter(ward_id=ward_id).order_by('place_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.ward:
            self.fields['place'].queryset = Place.objects.filter(ward=self.instance.ward).order_by('place_name')
    
# ItemForm for creating and updating items
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'image', 'region', 'district', 'ward', 'place', 'street']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the item'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control'}),
            'ward': forms.Select(attrs={'class': 'form-control'}),
            'place': forms.Select(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter street'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

# LocationDependentForm for dynamically updating location fields
class LocationDependentForm(forms.ModelForm):
    def update_dependent_fields(self, data, instance):
        # Districts
        self.fields['district'].queryset = District.objects.none()
        if 'region' in data:
            try:
                region_id = int(data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id).order_by('district_name')
            except (ValueError, TypeError):
                pass
        elif instance.pk and instance.region:
            self.fields['district'].queryset = District.objects.filter(region=instance.region).order_by('district_name')

        # Wards
        self.fields['ward'].queryset = Ward.objects.none()
        if 'district' in data:
            try:
                district_id = int(data.get('district'))
                self.fields['ward'].queryset = Ward.objects.filter(district_id=district_id).order_by('ward_name')
            except (ValueError, TypeError):
                pass
        elif instance.pk and instance.district:
            self.fields['ward'].queryset = Ward.objects.filter(district=instance.district).order_by('ward_name')

        # Places
        self.fields['place'].queryset = Place.objects.none()
        if 'ward' in data:
            try:
                ward_id = int(data.get('ward'))
                self.fields['place'].queryset = Place.objects.filter(ward_id=ward_id).order_by('place_name')
            except (ValueError, TypeError):
                pass
        elif instance.pk and instance.ward:
            self.fields['place'].queryset = Place.objects.filter(ward=instance.ward).order_by('place_name')


# MessageForm for sending messages
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your message...', 'class': 'form-control'}),
        }
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content.strip():
            raise forms.ValidationError("Message cannot be empty.")
        return content
