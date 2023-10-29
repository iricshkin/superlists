from django.test import TestCase
from django.utils.html import escape

from lists.models import Item, List
from lists.forms import ItemForm


class HomePageTest(TestCase):
    """Тест домашней страницы."""

    def test_uses_home_template(self):
        """Тест: используется домашний шаблон."""
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self):
        """Тест: домашняя страница использует форму для элемента."""
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


class ListViewTest(TestCase):
    """Тест представления списка"""

    def test_user_list_template(self):
        """Тест: используется шаблон списка."""
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_displays_only_items_For_that_list(self):
        """Тест: отображаются только для этого списка."""
        correct_list = List.objects.create()
        Item.objects.create(text="itemey 1", list=correct_list)
        Item.objects.create(text="itemey 2", list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text="other item list 1", list=other_list)
        Item.objects.create(text="other item list 2", list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")

        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
        self.assertNotContains(response, "other item list 1")
        self.assertNotContains(response, "other item list 2")

    def test_passes_correct_list_to_template(self):
        """Тест: передается правильный шаблон списка."""
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertEqual(response.context["list"], correct_list)

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """Тест: можно сохранить post-запрос в существующий список."""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new list item for an existing list"},
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item for an existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        """Тест: post-запрос переадресуется в представление списка."""
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new list item for an existing list"},
        )

        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        """Тест: ошибки валидации отсылаются назад в шаблон домашней страницы."""
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        """Тест: сохраняются недопустимые элементы списка."""
        self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_validation_errors_end_up_on_lists_page(self):
        """Тест: ошибки валидации оканчиваются на странице списков."""
        list_ = List.objects.create()
        response = self.client.post(f"/lists/{list_.id}/", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")
        expected_error = escape("You can't have an empty list item")
        self.assertContains(response, expected_error)
