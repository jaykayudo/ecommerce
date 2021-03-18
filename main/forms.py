from django import forms
from django.core.mail import send_mail
import logging
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from . import models
from django.contrib.auth.forms import UsernameField
from django.contrib.auth import authenticate
from django.forms import inlineformset_factory
from .widgets import PlusMinusWidget

logger = logging.getLogger(__name__)
class ContactForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','max-length':'100','placeholder':'Name'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','max-length':'600','rows':'10','cols':'85'}))

    def send_mail(self):
        logger.info('Sending email to customer service')
        message = "From:{0}\n{1}".format(self.cleaned_data['name'],self.cleaned_data['message'])

        send_mail(
            "Site Message",
            message,
            "site@booktime.domain",
            ["customerservice@booktime.domain"],
            fail_silently=False
        )
    
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ['email']
        field_classes = {'email':UsernameField}

    def send_mail(self):
        logger.info('sending Mail to Customer')
        message = "Welcome {0}, ".format(self.cleaned_data['email'])

        send_mail(
            "Welcome to Booktime",
            message,
            "site@booktime.domain",
            [self.cleaned_data['email'],],
            fail_silently=True
        )

class AuthenticateForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(),strip=False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        email = self.cleaned_data.get('email')#they both do the same thing
        password = self.cleaned_data.get('password')#they both do the same thing

        if email is not None and password:
            self.user = authenticate(self.request,email=email,password=password)
        if self.user is None:
            raise forms.ValidationError('Incorrect Email/Password')
        logger.info('Authentication successful for email "%s"'%email)
        return self.cleaned_data
    def get_user(self):
        return self.user

BasketLineFormSet = inlineformset_factory(
models.Basket,
models.BasketLine,
fields=("quantity",),
extra=0,
# widgets={'quantity':PlusMinusWidget()}
)


class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)
    def __init__(self, user, *args, **kwargs):
        super(). __init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields['billing_address'].queryset = queryset
        self.fields['shipping_address'].queryset = queryset
