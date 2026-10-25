from django.test import TestCase
from django.urls import reverse
from .models import Contact


class ContactViewTests(TestCase):
    def test_homepage_contact_form_posts_to_contact_route(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'action="{reverse("contact")}"')
        self.assertContains(response, 'mailto:kanjib808@gmail.com')
        self.assertContains(response, 'tel:+917859883156')

    def test_valid_contact_submission_is_saved_and_redirected(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Kanji Baraiya',
            'email': 'visitor@example.com',
            'message': 'I would like to discuss a developer role.',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 1)
        self.assertContains(response, 'Your message has been sent')

    def test_invalid_submission_is_not_saved_and_shows_errors(self):
        response = self.client.post(reverse('contact'), {
            'name': '',
            'email': 'not-an-email',
            'message': '',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contact.objects.count(), 0)
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
        self.assertEqual(Contact.objects.count(), 0)
