from django.test import TestCase


class ViewTestClass(TestCase):

    def test_error_page(self):
        """Страница по адресу /nonexist-page/ использует использует
        статус ответа 404."""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)

    def test_error_page_template(self):
        """Страница по адресу /nonexist-page/ использует шаблон
        'core/404.html'."""
        response = self.client.get('/nonexist-page/')
        self.assertTemplateUsed(response, 'core/404.html')
