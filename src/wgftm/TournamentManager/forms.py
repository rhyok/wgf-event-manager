from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)
    is_player = forms.BooleanField(label="Check this box if you will be participating in a tournament", required=False)
    is_ucsd = forms.BooleanField(label="Check this box if you are a UCSD student", required=False)
    is_sixth = forms.BooleanField(label="Check this box if you are from Sixth College", required=False)
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)

class EditForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), max_length=100)
    is_player = forms.BooleanField(label="Check this box if you will be participating in a tournament", required=False)
    is_ucsd = forms.BooleanField(label="Check this box if you are a UCSD student", required=False)
    is_sixth = forms.BooleanField(label="Check this box if you are from Sixth College", required=False)