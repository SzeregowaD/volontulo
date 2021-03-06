# -*- coding: utf-8 -*-

"""
.. module:: forms
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from apps.volontulo.models import Offer
from apps.volontulo.models import OfferImage
from apps.volontulo.models import UserGallery
from apps.volontulo.utils import get_administrators_emails

ACCEPT_TERMS = """Wyrażam zgodę na przetwarzanie moich danych osobowych"""


class UserForm(forms.ModelForm):

    """Form reposponsible for authorization."""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    terms_acceptance = forms.BooleanField(label=ACCEPT_TERMS, required=True)

    class Meta(object):
        model = User
        fields = ['email']


class EditProfileForm(forms.Form):

    """Form reposponsible for edit user details on profile page."""
    first_name = forms.CharField(
        label="Imię",
        max_length=128,
        required=False
    )
    last_name = forms.CharField(
        label="Nazwisko",
        max_length=128,
        required=False
    )
    phone_no = forms.CharField(
        label="Numer telefonu",
        required=False
    )
    current_password = forms.CharField(
        widget=forms.PasswordInput(),
        label='Aktualne hasło',
        required=False
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Nowe hasło",
        required=False
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Powtórz nowe hasło",
        required=False
    )
    user = forms.CharField(widget=forms.HiddenInput())

    def is_valid(self):
        valid = super(EditProfileForm, self).is_valid()
        if not valid:
            return valid

        current_password = self.cleaned_data['current_password']
        new_password = self.cleaned_data['new_password']
        confirm_new_password = self.cleaned_data['confirm_new_password']
        user = User.objects.get(id=self.cleaned_data['user'])

        if (
                current_password and
                new_password and
                confirm_new_password
        ):
            if not user.check_password(current_password):
                raise ValidationError("Aktualne hasło jest błędne")

            if new_password != confirm_new_password:
                raise ValidationError("Wprowadzone hasła różnią się")

        return True


class CreateOfferForm(forms.ModelForm):

    """Form reposponsible for creating offer by organization."""

    start_finish_error = """Data rozpoczęcia akcji nie może być
        późniejsza, niż data zakończenia"""
    recruitment_error = """Data rozpoczęcia rekrutacji
        nie może być późniejsza, niż data zakończenia"""
    reserve_recruitment_error = """Data rozpoczęcia rekrutacji
        rezerwowej nie może być późniejsza, niż data zakończenia"""

    def __init__(self, *args, **kwargs):
        super(CreateOfferForm, self).__init__(*args, **kwargs)
        self.fields['status_old'].required = False

    class Meta(object):
        model = Offer
        fields = [
            'organization',
            'description',
            'requirements',
            'time_commitment',
            'benefits',
            'location',
            'title',
            'time_period',
            'status_old',
            'started_at',
            'finished_at',
            'recruitment_start_date',
            'recruitment_end_date',
            'reserve_recruitment',
            'reserve_recruitment_start_date',
            'reserve_recruitment_end_date',
            'action_ongoing',
            'constant_coop',
            'action_start_date',
            'action_end_date',
            'volunteers_limit',
            'reserve_volunteers_limit',
        ]

    def clean(self):
        super(CreateOfferForm, self).clean()
        self._clean_start_finish('started_at',
                                 'finished_at',
                                 self.start_finish_error)
        self._clean_start_finish('recruitment_start_date',
                                 'recruitment_end_date',
                                 self.recruitment_error)
        self._clean_start_finish('reserve_recruitment_start_date',
                                 'reserve_recruitment_end_date',
                                 self.reserve_recruitment_error)
        return self.cleaned_data

    def _clean_start_finish(self, start_slug, end_slug, error_desc):
        """Validation for date fields."""
        start_field_value = self.cleaned_data.get(start_slug)
        end_field_value = self.cleaned_data.get(end_slug)
        if start_field_value and end_field_value:
            if start_field_value > end_field_value:
                self.add_error(start_slug, error_desc)
                self.add_error(end_slug, error_desc)


class UserGalleryForm(forms.ModelForm):

    """Form used for changing user profile of user."""
    image = forms.ImageField(label="Wybierz grafikę")

    class Meta(object):
        model = UserGallery
        fields = [
            'image',
        ]


class OfferImageForm(forms.ModelForm):

    """Form used for upload offer image."""
    path = forms.ImageField(label="Dodaj zdjęcie")
    is_main = forms.BooleanField(
        label="Użyj jako zdjęcie główne? ",
        required=False,
    )

    class Meta(object):
        model = OfferImage
        fields = [
            'path',
        ]


class OfferApplyForm(forms.Form):

    """Form for applying for join to offer ."""
    email = forms.CharField(max_length=80)
    phone_no = forms.CharField(max_length=80)
    fullname = forms.CharField(max_length=80)
    comments = forms.CharField(required=False, widget=forms.Textarea)


class ContactForm(forms.Form):

    """Basic contact form."""
    email = forms.CharField(max_length=150)
    message = forms.CharField(widget=forms.Textarea())
    name = forms.CharField(max_length=150)
    phone_no = forms.CharField(max_length=150)


class VolounteerToOrganizationContactForm(ContactForm):

    """Contact form specified for volounteers to mail to organization."""
    organization = forms.CharField(widget=forms.HiddenInput())


class AdministratorContactForm(ContactForm):

    """Contact form specified for anyone to mail to administrator."""
    APPLICANTS = (
        ('VOLUNTEER', 'wolontariusz'),
        ('ORGANIZATION', 'organizacja'),
    )
    applicant = forms.Select(choices=APPLICANTS)

    def __init__(self, *args, **kwargs):
        """Administrator contant form initialization.

        Administrator choice need to be here, as new Django release tries to
        import this form during migrations, even if user table is not
        available.
        """
        super(AdministratorContactForm, self).__init__(*args, **kwargs)
        self.administrator = forms.Select(
            choices=get_administrators_emails().items(),
        )
