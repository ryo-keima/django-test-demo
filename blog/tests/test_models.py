from django.test import TestCase
from django.core.exceptions import ValidationError

from ..models import Category, Post


class CategoryModelTest(TestCase):

    def test_name_field_max_length(self):
        """ nameフィールドの最大長が正しく設定されていること """
        category = Category(name="a" * 100)
        category.full_clean()
        self.assertEqual(len(category.name), 100)

    def test_name_field_max_length_exceeded(self):
        """ フィールドの最大長を超えた場合ValidationError """
        category = Category(name="a" * 101)
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_name_field_null(self):
        """ nameフィールドがnullの場合ValidationError """
        category = Category(name=None)
        with self.assertRaises(ValidationError):
            category.full_clean()

    def test_model_instance_creation(self):
        """ モデルインスタンスの作成に成功すること """
        category = Category(name="TestCategory")
        category.save()
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.get(id=1).name, "TestCategory")

    def test_model_instance_string_representation(self):
        """ モデルインスタンスの文字列表現テスト(__str__) """
        category = Category(name="TestCategory")
        self.assertEqual(str(category), "TestCategory")


class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="TestCategory")

    def test_title_field_max_length(self):
        """ titleフィールドの最大長が正しく設定されていること """
        post = Post(title="a" * 200, content="Test Content",
                    category=self.category)
        post.full_clean()
        self.assertEqual(len(post.title), 200)

    def test_title_field_max_length_exceeded(self):
        """ フィールドの最大長を超えた場合ValidationError """
        post = Post(title="a" * 201, content="Test Content",
                    category=self.category)
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_title_field_null(self):
        """ titleフィールドがnullの場合ValidationError """
        post = Post(title=None,
                    content="Test Content",
                    category=self.category)
        with self.assertRaises(ValidationError):
            post.full_clean()

    def test_model_instance_creation(self):
        """ モデルインスタンスの作成に成功すること """
        post = Post(title="Test Post",
                    content="Test Content",
                    category=self.category)
        post.save()
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get(id=1).title, "Test Post")

    def test_model_instance_string_representation(self):
        """ モデルインスタンスの文字列表現テスト(__str__) """
        post = Post(title="Test Post",
                    content="Test Content",
                    category=self.category)
        self.assertEqual(str(post), "Test Post")

    def test_post_category_relationship(self):
        """ PostとCategoryのリレーションテスト """
        post = Post(title="Test Post",
                    content="Test Content",
                    category=self.category)
        post.save()
        self.assertEqual(post.category, self.category)

    def test_category_null(self):
        """ categoryフィールドがnullの場合も登録できること """
        post = Post(title="Test Post",
                    content="Test Content",
                    category=None)
        post.save()
        self.assertEqual(post.category, None)

    def test_post_category_cascade_delete(self):
        """ Category削除時のカスケード削除テスト """
        post = Post(title="Test Post",
                    content="Test Content",
                    category=self.category)
        post.save()
        self.category.delete()
        self.assertEqual(Post.objects.count(), 0)
