from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(required=False, label=_('Search'), widget=forms.TextInput(attrs={'type': 'search'}))

    def send_email(self):
        # send email using the self.cleaned_data dictionary
        pass

