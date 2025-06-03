from django import forms
from collections import OrderedDict


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, label='موضوع')
    message = forms.CharField(widget=forms.Textarea, label='پیام')

    def __init__(self, *args, user_email=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not user_email:
            # ایمیل رو اجباری تعریف کن
            email_field = forms.EmailField(label='ایمیل شما', required=True)
            # ابتدا ایمیل رو اضافه کن
            self.fields['email'] = email_field

            # برای جابجایی ایمیل به اول، فیلدها رو مرتب کن
            fields_order = ['email', 'subject', 'message']
            self.fields = OrderedDict((k, self.fields[k]) for k in fields_order)
