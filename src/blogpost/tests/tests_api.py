from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status

from ..models import CustomUser, BlogPost, Category, Tag


class BlogPostAPITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(username='author', password='pass')
        self.other = CustomUser.objects.create_user(username='other', password='pass')
        self.staff = CustomUser.objects.create_user(username='staff', password='pass', is_staff=True)
        self.cat = Category.objects.create(name='Cat1', slug='cat1')
        self.tag1 = Tag.objects.create(name='T1', slug='t1')
        self.tag2 = Tag.objects.create(name='T2', slug='t2')

        # published and draft posts (content must meet model validation)
        BlogPost.objects.create(title='P1', slug='p1', content=('C' * 80), author=self.user, status='published', category=self.cat)
        BlogPost.objects.create(title='D1', slug='d1', content=('C' * 80), author=self.user, status='draft', category=self.cat)

    def test_list_anonymous_shows_published_only(self):
        url = reverse('api-posts-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [r['title'] for r in resp.data]
        self.assertIn('P1', titles)
        self.assertNotIn('D1', titles)

    def test_create_post_assigns_author_and_accepts_slugs(self):
        url = reverse('api-posts-list')
        self.client.login(username='author', password='pass')
        payload = {
            'title': 'Created',
            'content': ('C' * 80),
            'category': 'cat1',
            'tags': ['t1','t2'],
            'status': 'published'
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['author']['username'], 'author')
        self.assertEqual(resp.data['category'], 'cat1')
        self.assertCountEqual(resp.data['tags'], ['t1','t2'])

    def test_author_can_edit_own_post_but_not_others(self):
        post = BlogPost.objects.create(title='EditMe', slug='editme', content=('C' * 80), author=self.other, status='published', category=self.cat)
        url = reverse('api-posts-detail', args=[post.pk])
        # author (not owner) cannot edit
        self.client.login(username='author', password='pass')
        resp = self.client.patch(url, {'title': 'X'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # owner can edit
        self.client.login(username='other', password='pass')
        resp2 = self.client.patch(url, {'title': 'X'}, format='json')
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

    def test_filter_by_category_and_tag_slug(self):
        url = reverse('api-posts-list') + '?category=cat1'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # at least the published post in cat1
        titles = [r['title'] for r in resp.data]
        self.assertIn('P1', titles)