from django import forms
from collections import OrderedDict


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, label='موضوع')
    message = forms.CharField(widget=forms.Textarea, label='پیام', max_length=2000)

    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super().__init__(*args, **kwargs)

        if not user_email:
            self.fields['email'] = forms.EmailField(label='ایمیل شما', required=True)
            # ترتیب فیلدها
            ordered_fields = ['email', 'subject', 'message']
            self.fields = OrderedDict((k, self.fields[k]) for k in ordered_fields)

    def clean_message(self):
        message = self.cleaned_data['message']
        if '<script' in message.lower():
            raise forms.ValidationError('استفاده از کدهای مخرب مجاز نیست.')
        return message
