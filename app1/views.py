from django import forms
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Contact


class ContactForm(forms.ModelForm):
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

    class Meta:
        model = Contact
        fields = ('name', 'email', 'message')


def home(request):
    return render(request, 'pages/home.html', {'form': ContactForm()})

def about(request):
    return render(request, 'pages/about_page.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out. Your message has been sent.")
            return redirect('contact')
        messages.error(request, "Please review the highlighted fields and try again.")
    else:
        form = ContactForm()

    return render(request, 'pages/contact_page.html', {'form': form})