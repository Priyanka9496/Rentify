from django import forms
from .models import Property, Booking


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'address', 'price_per_night', 'available', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full mt-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full mt-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Enter description'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full mt-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter address'
            }),
            'price_per_night': forms.NumberInput(attrs={
                'class': 'w-full mt-1 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Enter price per night'
            }),
            'available': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-indigo-600 border-gray-300 rounded',
            }),
            'image': forms.FileInput(attrs={
                'class': 'mt-1 p-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500',
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract user from kwargs
        super(PropertyForm, self).__init__(*args, **kwargs)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'text',
                'id': 'start_date',
                'class': 'border border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-200',
                'placeholder': 'Select start date'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'text',
                'id': 'end_date',
                'class': 'border border-gray-300 rounded-lg p-2 w-full focus:ring focus:ring-indigo-200',
                'placeholder': 'Select end date'
            }),
        }