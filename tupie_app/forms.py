from django import forms
from .models import Item, Region

class ItemForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        empty_label='Select Region',
        required=True
    )
    
    street = forms.CharField(
        required=False,
        max_length=100,
        label='Street (optional)',
        widget=forms.TextInput(attrs={'placeholder': 'Enter street'})
    )

    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'image', 'region', 'street']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the item'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].queryset = Region.objects.using('locations').all().order_by('region_name')
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('region'):
            raise forms.ValidationError("Please select a Region")
        return cleaned_data
