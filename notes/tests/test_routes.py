from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username="Автор")
        cls.guest = User.objects.create(username="Гость")
        cls.note = Note.objects.create(
            title="Заголовок", text="Текст", author=cls.author
        )

    def test_pages_availability(self):
        """Проверка доступа к публичным страницам."""
        urls = (
            "notes:home",
            "users:login",
            "users:signup",
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes(self):
        """Проверка доступа к страницам автора."""

        urls = (
            ("notes:list", None),
            ("notes:add", None),
            ("notes:success", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
            ("users:logout", None),
        )

        # Логиним пользователя в клиенте.
        self.client.force_login(self.author)
        # Для каждой пары перебираем имена тестируемых страниц и slug.
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.client.get(url)
                if name == "users:logout":
                    response = self.client.post(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_guest(self):
        """Проверка редиректа"""
        urls = (
            ("notes:list", None),
            ("notes:add", None),
            ("notes:success", None),
            ("notes:detail", (self.note.slug,)),
            ("notes:edit", (self.note.slug,)),
            ("notes:delete", (self.note.slug,)),
        )
        # Сохраняем адрес страницы логина.
        login_url = reverse("users:login")
        # В цикле перебираем имена страниц, с которых ожидаем редирект
        for name, args in urls:
            with self.subTest(name=name, args=args):
                # Получаем адрес страницы редактирования или удаления комментария
                url = reverse(name, args=args)
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f"{login_url}?next={url}"
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)

    def test_logout(self):
        """Проверка логаута"""
        url = reverse("users:logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
