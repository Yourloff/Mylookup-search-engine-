from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import MyUser, FeaturedSite


class QueryForm(forms.Form):
    query = forms.CharField(label='', max_length=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class XmlForm(forms.Form):
    xmldom = forms.CharField(label='', max_length=2048)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class SitesForm(forms.ModelForm):
    class Meta:
        model = FeaturedSite
        fields = ('title_site', 'link_site')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class MyUserForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class AuthUserForm(AuthenticationForm, forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs[
                'class'] = 'form-control'


class RegisterUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        email = forms.EmailField(required=True, widget=forms.EmailInput
        (attrs={'autocomplete': 'email'}), label='Адрес электронной почты')
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1',
                  'password2')
        help_texts = {
            'password1': None,
        }

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        for fieldname in ['password1', 'password2']:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
