from django.test import TestCase
from django.utils.html import escape

from lists.models import Item, List
from lists.forms import ItemForm, EMPTY_ITEM_ERROR


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

    def post_invalid_input(self):
        """Отправляет недопустимы ввод."""
        list_ = List.objects.create()
        return self.client.post(f"/lists/{list_.id}/", data={"text": ""})

    def test_for_invalid_input_nothing_saved_to_db(self):
        """Тест на недопустимый ввод: ничего не сохраняется в БД."""
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        """Тест на недопустимый ввод: отображается шаблон списка."""
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "list.html")

    def test_for_invalid_input_passes_form_to_template(self):
        """Тест на недопустимый ввод: форма передается в шаблон."""
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        """Тест на недопустимый ввод: на странице показывается ошибка."""
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_displays_item_form(self):
        """Тест отображения формы для элемента."""
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertIsInstance(response.context["form"], ItemForm)
        self.assertContains(response, 'name="text"')


class NewListTest(TestCase):
    """Тест нового списка."""

    def test_invalid_list_items_arent_saved(self):
        """Тест: сохраняются недопустимые элементы списка."""
        self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_home_template(self):
        """Тест на недопустимый ввод: отображает домашний шаблон."""
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_validation_errors_are_show_on_home_page(self):
        """Тест: ошибки валидации выводятся на домашней странице."""
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_for_invalid_input_passes_form_to__template(self):
        """Тест на недопустимый ввод: форма передается в шаблон."""
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], ItemForm)
