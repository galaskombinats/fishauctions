from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Auction, Bid, UserProfile, Fish
from django.utils.translation import gettext_lazy as _

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
        }

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('user_type',)
        labels = {
            'user_type': _('User Type'),
        }

class FishForm(forms.ModelForm):
    class Meta:
        model = Fish
        fields = ['name']
        labels = {
            'name': _('Name'),
        }

class AuctionForm(forms.ModelForm):
    duration_hours = forms.IntegerField(min_value=0, required=True, label=_("Duration (hours)"))
    duration_minutes = forms.IntegerField(min_value=0, max_value=59, required=True, label=_("Duration (minutes)"))

    class Meta:
        model = Auction
        fields = ['fish', 'duration_hours', 'duration_minutes', 'starting_bid', 'description', 'size_cm', 'weight_kg', 'image']
        labels = {
            'fish': _('Fish'),
            'starting_bid': _('Starting Bid'),
            'description': _('Description'),
            'size_cm': _('Size (cm)'),
            'weight_kg': _('Weight (kg)'),
            'image': _('Image'),
        }
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': True})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fish'].queryset = Fish.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        duration_hours = cleaned_data.get('duration_hours')
        duration_minutes = cleaned_data.get('duration_minutes')
        cleaned_data['duration_minutes'] = duration_hours * 60 + duration_minutes
        return cleaned_data

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        labels = {
            'amount': _('Amount'),
        }

    def __init__(self, *args, **kwargs):
        self.auction = kwargs.pop('auction', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        highest_bid = self.auction.bid_set.order_by('-amount').first()

        # Ensure the bid is higher than the starting bid
        if amount < self.auction.starting_bid:
            raise forms.ValidationError(_('Your bid must be higher than the starting bid.'))

        # Ensure the bid is higher than the current highest bid, if there is one
        if highest_bid and amount <= highest_bid.amount:
            raise forms.ValidationError(_('Your bid must be higher than the current highest bid.'))

        return amount

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('buyer', _('Buyer')), ('seller', _('Seller'))], label=_('User Type'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        labels = {
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if 'password' not in cd or 'password2' not in cd:
            raise forms.ValidationError(_('Please enter both password fields.'))
        if cd['password'] != cd['password2']:
            raise forms.ValidationError(_('Passwords don’t match.'))
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
