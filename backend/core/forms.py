from django import forms

from .models import SiteSettings

URL_WIDGET = forms.TextInput(
    attrs={
        'class': 'vTextField',
        'style': 'width: 100%; max-width: 42rem;',
        'placeholder': 'https://ornek.com',
    },
)


class SiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'
        widgets = {
            'canonical_url': URL_WIDGET,
            'site_url': URL_WIDGET,
            'og_image_url': URL_WIDGET,
            'logo_url': URL_WIDGET,
            'favicon_url': URL_WIDGET,
            'instagram_url': URL_WIDGET,
            'facebook_url': URL_WIDGET,
        }
        help_texts = {
            'canonical_url': 'Tam adres girin, örn: https://cekicipro.com/',
            'site_url': 'Tam adres girin, örn: https://cekicipro.com',
        }

    def _normalize_url(self, value: str) -> str:
        value = (value or '').strip()
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value

    def clean_canonical_url(self):
        return self._normalize_url(self.cleaned_data.get('canonical_url', ''))

    def clean_site_url(self):
        return self._normalize_url(self.cleaned_data.get('site_url', ''))

    def clean_og_image_url(self):
        value = self.cleaned_data.get('og_image_url', '')
        return self._normalize_url(value) if value else ''

    def clean_instagram_url(self):
        value = self.cleaned_data.get('instagram_url', '')
        return self._normalize_url(value) if value else ''

    def clean_facebook_url(self):
        value = self.cleaned_data.get('facebook_url', '')
        return self._normalize_url(value) if value else ''

    def clean_logo_url(self):
        value = self.cleaned_data.get('logo_url', '')
        return self._normalize_url(value) if value else ''

    def clean_favicon_url(self):
        value = self.cleaned_data.get('favicon_url', '')
        return self._normalize_url(value) if value else ''
