from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item title'}),
            'descriptin': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the item'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }