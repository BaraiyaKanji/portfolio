import logging
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect


logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'autocomplete': 'name',
            'placeholder': 'Your name',
            'class': 'form-control contact-field',
            'maxlength': 100,
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'placeholder': 'you@example.com',
            'class': 'form-control contact-field',
        }),
    )
    message = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Tell me a little about your message',
            'class': 'form-control contact-field',
        }),
    )


def home(request):
    return render(request, 'pages/home.html', {'form': ContactForm()})

def about(request):
    return render(request, 'pages/about_page.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if not settings.EMAIL_HOST or not settings.CONTACT_EMAIL:
                logger.error('Contact email delivery is not configured.')
                messages.error(request, "Your message could not be sent. Please try again later.")
            else:
                try:
                    email = EmailMessage(
                        subject=f"Portfolio contact from {form.cleaned_data['name']}",
                        body=form.cleaned_data['message'],
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.CONTACT_EMAIL],
                        reply_to=[form.cleaned_data['email']],
                    )
                    sent = email.send(fail_silently=False)
                except (OSError, SMTPException, ValueError):
                    logger.exception('Failed to send portfolio contact email.')
                    messages.error(request, "Your message could not be sent. Please try again later.")
                else:
                    if sent:
                        messages.success(request, "Thanks for reaching out. Your message has been sent.")
                        return redirect('contact')
                    logger.error('Contact email backend did not send the message.')
                    messages.error(request, "Your message could not be sent. Please try again later.")
        else:
            messages.error(request, "Please review the highlighted fields and try again.")
    else:
        form = ContactForm()

    return render(request, 'pages/contact_page.html', {'form': form})