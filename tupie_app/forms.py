from django import forms
from .models import Item, Region, District, Ward, Place
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save phone number to UserProfile
            user.userprofile.phone_number = self.cleaned_data['phone_number']
            user.userprofile.save()
        return user