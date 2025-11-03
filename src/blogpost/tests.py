from django.test import TestCase
from django.urls import reverse

from .models import CustomUser, BlogPost, Category


class DraftListViewTests(TestCase):
	def setUp(self):
		# users
		self.user1 = CustomUser.objects.create_user(username='author', password='pass')
		self.user2 = CustomUser.objects.create_user(username='other', password='pass')
		self.staff = CustomUser.objects.create_user(username='staff', password='pass', is_staff=True)

		# category
		self.cat = Category.objects.create(name='Test', slug='test')

		# drafts
		BlogPost.objects.create(title='Draft1', slug='draft1', content='c', author=self.user1, status='draft', category=self.cat)
		BlogPost.objects.create(title='Draft2', slug='draft2', content='c', author=self.user2, status='draft', category=self.cat)

	def test_anonymous_redirects_to_login(self):
		resp = self.client.get(reverse('blogpost_drafts'))
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(reverse('login') in resp.url)

	def test_author_sees_only_own_drafts(self):
		self.client.login(username='author', password='pass')
		resp = self.client.get(reverse('blogpost_drafts'))
		self.assertEqual(resp.status_code, 200)
		articles = resp.context['articles']
		self.assertEqual(len(articles), 1)
		self.assertEqual(articles[0].author, self.user1)

	def test_staff_sees_all_drafts(self):
		self.client.login(username='staff', password='pass')
		resp = self.client.get(reverse('blogpost_drafts'))
		self.assertEqual(resp.status_code, 200)
		articles = resp.context['articles']
		self.assertEqual(articles.count(), 2)


class NavCategoriesCacheTests(TestCase):
	def test_cache_cleared_on_category_create_and_delete(self):
		from django.core.cache import cache
		# prime cache
		cache.set('nav_categories', ['sentinel'], 3600)
		from .models import Category

		# create category -> should clear cache via signal
		Category.objects.create(name='New', slug='new')
		self.assertIsNone(cache.get('nav_categories'))

		# prime cache again, then delete a category
		cache.set('nav_categories', ['sentinel2'], 3600)
		c = Category.objects.create(name='ToDelete', slug='todelete')
		c.delete()
		self.assertIsNone(cache.get('nav_categories'))

	def test_cache_cleared_on_blogpost_create_update_delete(self):
		from django.core.cache import cache
		# prime cache
		cache.set('nav_categories', ['sentinel3'], 3600)
		from .models import BlogPost, Category
		user = CustomUser.objects.create_user(username='u1', password='p')
		cat = Category.objects.create(name='C1', slug='c1')
		# create blogpost -> should clear cache
		BlogPost.objects.create(title='B1', slug='b1', content='x', author=user, status='published', category=cat)
		self.assertIsNone(cache.get('nav_categories'))

		# prime and update blogpost category
		cache.set('nav_categories', ['sentinel4'], 3600)
		b = BlogPost.objects.create(title='B2', slug='b2', content='x', author=user, status='published', category=cat)

		# Updating a non-category field should NOT clear the cache
		cache.set('nav_categories', ['sentinel4'], 3600)
		b.title = 'B2 updated'
		b.save()
		self.assertEqual(cache.get('nav_categories'), ['sentinel4'])

		# Changing category should clear the cache
		new_cat = Category.objects.create(name='C2', slug='c2')
		b.category = new_cat
		b.save()
		self.assertIsNone(cache.get('nav_categories'))

		# prime and delete
		cache.set('nav_categories', ['sentinel5'], 3600)
		b3 = BlogPost.objects.create(title='B3', slug='b3', content='x', author=user, status='published', category=cat)
		b3.delete()
		self.assertIsNone(cache.get('nav_categories'))


class ContactFormTests(TestCase):
	def test_contact_post_creates_message_and_sends_email(self):
		from django.core import mail
		from django.urls import reverse
		from django.test import override_settings
		from .models import ContactMessage

		url = reverse('contact')
		data = {
			'name': 'Alice',
			'email': 'alice@example.com',
			'subject': 'Hello',
			'message': 'Bonjour, ceci est un message de test.'
		}

		# Use locmem backend during the test to capture outbox
		with override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
			resp = self.client.post(url, data)
			# should redirect to thanks
			self.assertEqual(resp.status_code, 302)
			self.assertIn(reverse('contact_thanks'), resp.url)

			# message saved
			msg = ContactMessage.objects.filter(email='alice@example.com').first()
			self.assertIsNotNone(msg)
			self.assertEqual(msg.name, 'Alice')

			# email sent
			self.assertEqual(len(mail.outbox), 1)
			sent = mail.outbox[0]
			self.assertIn('Bonjour', sent.body)


class AdminContactActionsTests(TestCase):
	def test_admin_toggle_read(self):
		from django.contrib.auth import get_user_model
		from django.urls import reverse
		# create superuser
		User = get_user_model()
		admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')
		# create message
		from .models import ContactMessage
		cm = ContactMessage.objects.create(name='Bob', email='bob@example.com', subject='Hi', message='Test', read=False)

		# login and call toggle URL
		self.client.force_login(admin)
		url = f'/admin/blogpost/contactmessage/{cm.pk}/toggle_read/'
		resp = self.client.get(url, follow=True)
		self.assertEqual(resp.status_code, 200)
		cm.refresh_from_db()
		self.assertTrue(cm.read)


class CaptchaContactTests(TestCase):
	def test_captcha_field_present_and_validates_when_keys_set(self):
		from django.test import override_settings
		from django.urls import reverse
		from unittest.mock import patch
		from .forms import ContactForm
		from .models import ContactMessage

		# simulate keys present
		with override_settings(RECAPTCHA_PUBLIC_KEY='pk', RECAPTCHA_PRIVATE_KEY='sk'):
			form = ContactForm()
			# captcha field should be present in form fields when recaptcha installed
			if 'captcha' not in form.fields:
				# If django-recaptcha isn't installed in the environment the field won't exist;
				# fail the test to indicate the environment needs the package.
				self.skipTest('django-recaptcha not installed; skipping captcha presence test')
			# Patch the ReCaptchaField.clean to accept the provided token
			with patch('captcha.fields.ReCaptchaField.clean', return_value='passed'):
				url = reverse('contact')
				data = {
					'name': 'CAP',
					'email': 'cap@example.com',
					'subject': 'CAP test',
					'message': 'Message with captcha',
					'captcha': 'dummy-token'
				}
				from django.core import mail
				from django.test import override_settings as override_email
				with override_email(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
					resp = self.client.post(url, data)
					self.assertEqual(resp.status_code, 302)
					self.assertTrue(ContactMessage.objects.filter(email='cap@example.com').exists())
					self.assertEqual(len(mail.outbox), 1)
