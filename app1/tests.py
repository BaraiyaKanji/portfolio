from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class ContactViewTests(TestCase):
    def test_homepage_contact_form_posts_to_contact_route(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'action="{reverse("contact")}"')
        self.assertContains(response, 'mailto:kanjib808@gmail.com')
        self.assertContains(response, 'tel:+917859883156')

    @override_settings(
        EMAIL_HOST='smtp.example.com',
        CONTACT_EMAIL='owner@example.com',
        DEFAULT_FROM_EMAIL='portfolio@example.com',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_valid_contact_submission_is_emailed_and_redirected(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'I would like to discuss a developer role.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['owner@example.com'])
        self.assertEqual(mail.outbox[0].reply_to, ['visitor@example.com'])
        self.assertEqual(mail.outbox[0].body, 'I would like to discuss a developer role.')
        self.assertContains(response, 'Your message has been sent')

    @override_settings(
        EMAIL_HOST='smtp.example.com',
        CONTACT_EMAIL='owner@example.com',
        DEFAULT_FROM_EMAIL='portfolio@example.com',
    )
    @patch('app1.views.EmailMessage.send', side_effect=SMTPException('SMTP unavailable'))
    def test_email_delivery_failure_does_not_crash(self, send_mock):
        response = self.client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'Hello.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your message could not be sent. Please try again later.')
        send_mock.assert_called_once()

    @override_settings(
        EMAIL_HOST='smtp.example.com',
        CONTACT_EMAIL='owner@example.com',
        DEFAULT_FROM_EMAIL='portfolio@example.com',
    )
    @patch('app1.views.EmailMessage.send', return_value=0)
    def test_zero_sent_email_count_is_reported_as_failure(self, send_mock):
        response = self.client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'Hello.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your message could not be sent. Please try again later.')
        send_mock.assert_called_once()

    @override_settings(EMAIL_HOST='', CONTACT_EMAIL='')
    def test_contact_submission_without_email_configuration_does_not_crash(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'Hello.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your message could not be sent. Please try again later.')

    def test_invalid_submission_is_not_saved_and_shows_errors(self):
        response = self.client.post(reverse('contact'), {
            'name': '',
            'email': 'not-an-email',
            'message': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please correct the errors below.')
        self.assertContains(response, 'Enter a valid email address.')

    def test_contact_submission_requires_csrf_token(self):
        csrf_client = self.client_class(enforce_csrf_checks=True)

        response = csrf_client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'Hello.',
        })

        self.assertEqual(response.status_code, 403)
