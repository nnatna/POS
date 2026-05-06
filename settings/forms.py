from django import forms
from django.contrib.auth.models import User
from .models import OpeningHours

class PersonalInformationForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=32, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    position = forms.ChoiceField(
        required=False,
        choices=[('Owner', 'Owner'), ('Staff', 'Staff')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class EmployeeForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=32, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    dob = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    position = forms.ChoiceField(
        required=False,
        choices=[('Owner', 'Owner'), ('Staff', 'Staff')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('A user with this username already exists.')
        return username

class MyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].widget.attrs['readonly'] = True
        self.fields['position'].widget.attrs['class'] = 'form-control-plaintext'

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['day_of_week', 'open_time', 'close_time']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('Monday', 'Monday'),
                ('Tuesday', 'Tuesday'),
                ('Wednesday', 'Wednesday'),
                ('Thursday', 'Thursday'),
                ('Friday', 'Friday'),
                ('Saturday', 'Saturday'),
                ('Sunday', 'Sunday'),
            ]),
            'open_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        open_time = cleaned_data.get('open_time')
        close_time = cleaned_data.get('close_time')
        if open_time and close_time and open_time >= close_time:
            raise forms.ValidationError('Close time must be later than open time.')
        return cleaned_data