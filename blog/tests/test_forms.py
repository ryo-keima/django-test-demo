from django.test import TestCase

from ..models import Category
from ..forms import PostForm


class PostFormTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="TestCategory")

    def test_form_has_fields(self):
        """ フォームがPostモデルのフィールドを持っていること """
        form = PostForm()
        self.assertIn("title", form.fields)
        self.assertIn("content", form.fields)
        self.assertIn("category", form.fields)

    def test_valid_data(self):
        """ フォームが有効なデータで正しく動作すること """
        form = PostForm(data={
            "title": "Test Post",
            "content": "Test Content",
            "category": self.category.id
        })
        self.assertTrue(form.is_valid())

    def test_title_blank(self):
        """ フォームがタイトルを空で受け付けないこと """
        form = PostForm(data={
            "title": None,
            "content": "Test Content",
            "category": self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_content_blank(self):
        """ 本文は空でもOKであること """
        form = PostForm(data={
            "title": "Test Post",
            "content": None,
            "category": self.category.id
        })
        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_category_blank(self):
        """ カテゴリは空でもOKであること """
        form = PostForm(data={
            "title": "Test Post",
            "content": "Test Content",
            "category": None
        })
        self.assertTrue(form.is_valid())

    def test_invalid_category(self):
        """ カテゴリに存在しないIDを指定した場合ValidationError """
        form = PostForm(data={
            "title": "Test Post",
            "content": "Test Content",
            "category": 999
        })
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)
