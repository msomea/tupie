from django import forms
from .models import Item, ItemImage, Region, District, Ward, Place, Street, Message, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, BaseModelFormSet, ValidationError

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
        fields = ['photo', 'phone_number', 'full_name', 'id_document', 'region', 'district', 'ward', 'place']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name as it appears on ID'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'photo': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Select Image'}),
            'region': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Region' }),
            'district': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select District'}),
            'ward': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Ward'}),
            'place': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Place'}),
            'id_document': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'Select your ID'}),
        }
    
    def clean_email(self):
        return self.instance.email  # Forces it to stay unchanged


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

# Item Form for creating and updating items
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'title', 'description', 'category', 'region', 'district', 'ward', 
            'place', 'street', 'image1', 'image2', 'image3'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item title', 'required': 'required'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the item', 'rows': 3, 'required': 'required'}),
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category', 'required': 'required'}),
            'region': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Region', 'required': 'required'}),
            'district': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select District', 'required': 'required'}),
            'ward': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Ward', 'required': 'required'}),
            'place': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Place', 'required': 'required'}),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image3': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['region'].queryset = Region.objects.all()
        self.fields['district'].queryset = District.objects.all()
        self.fields['ward'].queryset = Ward.objects.all()
        self.fields['place'].queryset = Place.objects.all()

        # Dynamic filtering
        if 'region' in self.data:
            try:
                region_id = int(self.data.get('region'))
                self.fields['district'].queryset = District.objects.filter(region_id=region_id).order_by('district_name')
            except (ValueError, TypeError):
                pass
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

        # Make location fields required
        for field in ['region', 'district', 'ward', 'place']:
            self.fields[field].required = True

# ItemImagesForm for handling multiple item images
class ItemImagesForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'required': 'required'}),
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            raise forms.ValidationError("Image is required.")
        return image

ItemImageFormSet = modelformset_factory(
    ItemImage,
    form=ItemImagesForm,
    extra=3,
    max_num=3,
    can_delete=True
)

class RequiredImageFormSet(BaseModelFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        has_image = False
        for form in self.forms:
            if form.cleaned_data and form.cleaned_data.get('image'):
                has_image = True
                break

        if not has_image:
            raise ValidationError("Please upload at least one image.")

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
