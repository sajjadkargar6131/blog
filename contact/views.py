from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.shortcuts import render
from django.conf import settings

from .forms import ContactForm
from .models import ContactMessage


def contact_view(request):
    user_email = None
    if request.user.is_authenticated:
        verified_emails = request.user.emailaddress_set.filter(verified=True)
        if verified_emails.exists():
            user_email = verified_emails.first().email

    cooldown_period = timedelta(minutes=1)
    now = timezone.now()

    if request.method == 'POST':
        form = ContactForm(request.POST, user_email=user_email)
        if form.is_valid():
            email = user_email or form.cleaned_data.get('email')

            # بررسی آخرین پیام ارسالی در یک دقیقه اخیر
            last_message = None
            if request.user.is_authenticated:
                last_message = ContactMessage.objects.filter(
                    user=request.user,
                    created_at__gte=now - cooldown_period
                ).order_by('-created_at').first()
            else:
                last_message = ContactMessage.objects.filter(
                    email=email,
                    created_at__gte=now - cooldown_period
                ).order_by('-created_at').first()

            if last_message:
                messages.error(request, 'شما فقط می‌توانید هر دقیقه یک پیام ارسال کنید. لطفاً کمی صبر کنید.')
            else:
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']

                # ذخیره پیام در دیتابیس
                ContactMessage.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=email,
                    subject=subject,
                    message=message
                )

                # ارسال ایمیل به ادمین
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_RECEIVER_EMAIL], fail_silently=False)

                # ارسال ایمیل تاییدیه به کاربر
                context = {
                    'user_name': request.user.get_full_name() if request.user.is_authenticated else 'کاربر عزیز',
                    'subject': subject,
                    'site_name': getattr(settings, 'SITE_NAME', 'سایت ما'),
                }
                confirmation_subject = "پیام شما دریافت شد"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = [email]
                text_content = "پیام شما دریافت شد و در اسرع وقت با شما تماس خواهیم گرفت."
                html_content = render_to_string('email/confirmation_email.html', context)

                msg = EmailMultiAlternatives(confirmation_subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                messages.success(request, 'پیام شما با موفقیت ارسال شد.')
                form = ContactForm(user_email=user_email)  # پاک کردن فرم

    else:
        form = ContactForm(user_email=user_email)

    return render(request, 'contact/contact.html', {'form': form, 'user_email': user_email})
