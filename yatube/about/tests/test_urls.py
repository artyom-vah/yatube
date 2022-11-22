from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_about_author_url(self):
        """Проверка url about_author для любого пользователя."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech_url(self):
        """Проверка url about_tech для любого пользователя."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
