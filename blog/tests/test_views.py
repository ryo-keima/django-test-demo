from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from ..models import Category, Post
from ..forms import PostForm


class PostListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        number_of_posts = 5
        cls.test_category_name = "Test Category"
        category = Category.objects.create(name=cls.test_category_name)
        for post_num in range(number_of_posts):
            Post.objects.create(
                title=f"Post {post_num}",
                content=f"Test content {post_num}",
                category=category)

    def test_view_url_exists_at_desired_location(self):
        """ ビューのURLが正しく動作すること"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        """ ビューのURLが名前でアクセスできること """
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """ ビューが正しいテンプレートを使っていること """
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_list.html")

    def test_view_post_list(self):
        """ ビューにPostが5つ表示されていること """
        response = self.client.get(reverse("blog:post_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context["object_list"]) == 5)
        for post_num in range(5):
            self.assertEqual(
                response.context["object_list"][post_num].title,
                f"Post {post_num}")
            self.assertEqual(
                response.context["object_list"][post_num].category.name,
                self.test_category_name)


class PostDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_category_name = "TestCategory"
        cls.test_post_title = "Test Post"
        cls.test_post_content = "Test Content"

        category = Category.objects.create(name=cls.test_category_name)
        cls.test_post = Post.objects.create(
            title=cls.test_post_title,
            content=cls.test_post_content,
            category=category
        )

    def test_view_url_exists_at_desired_location(self):
        """ ビューのURLが正しく動作すること """
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(f"/post/{post_id}/")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """ ビューが正しいテンプレートを使っていること """
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(reverse("blog:post_detail", args=[post_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_detail.html")

    def test_context_data(self):
        """ テンプレートが正しいコンテキストデータを持っていること """
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(reverse("blog:post_detail", args=[post_id]))
        self.assertEqual(
            response.context["object"].title, self.test_post_title)
        self.assertEqual(
            response.context["object"].content, self.test_post_content)
        self.assertEqual(
            response.context["object"].category.name, self.test_category_name)
        self.assertEqual(
            response.context["object"].created_at, self.test_post.created_at)


class PostCreateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_category_name = "TestCategory"
        Category.objects.create(name=cls.test_category_name)
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass")

    def setUp(self):
        self.client.login(username="testuser", password="testpass")

    def test_view_url_exists_at_desired_location(self):

        response = self.client.get("/post/new/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_form.html")

    def test_form_display(self):
        """ フォームが適切に表示されることをテストする """
        response = self.client.get(reverse("blog:post_create"))
        self.assertIsInstance(response.context["form"], PostForm)

    def test_redirects_after_POST(self):
        """ 正しいデータをPOSTした後に適切なページにリダイレクトすること """
        category_id = Category.objects.get(name=self.test_category_name).id
        response = self.client.post(
            reverse("blog:post_create"), {
                "title": "New Post",
                "content": "New content",
                "category": category_id})
        self.assertRedirects(response, reverse("blog:post_list"))

    def test_create_post(self):
        """ POSTによって新しい投稿が作成されること """
        category_id = Category.objects.get(name=self.test_category_name).id
        self.client.post(
            reverse("blog:post_create"), {
                "title": "New Post",
                "content": "New content",
                "category": category_id})
        new_post = Post.objects.get(title="New Post")
        self.assertEqual(new_post.title, "New Post")
        self.assertEqual(new_post.content, "New content")
        self.assertEqual(new_post.category.id, category_id)

    def test_title_empty(self):
        """ タイトルが空の場合はwarningが表示されること """
        category_id = Category.objects.get(name=self.test_category_name).id
        response = self.client.post(
            reverse("blog:post_create"), {
                "title": "",
                "content": "New content",
                "category": category_id})
        self.assertFormError(
            response, "form", "title", "This field is required.")

    def test_content_empty(self):
        """ コンテンツが空の場合はwarningが表示されること """
        category_id = Category.objects.get(name=self.test_category_name).id
        response = self.client.post(
            reverse("blog:post_create"), {
                "title": "New Post",
                "content": "",
                "category": category_id})
        self.assertFormError(
            response, "form", "content", "This field is required.")

    def test_category_empty(self):
        """ カテゴリが空の場合でも登録できること """
        response = self.client.post(
            reverse("blog:post_create"), {
                "title": "New Post",
                "content": "New content",
                "category": ""})
        self.assertRedirects(response, reverse("blog:post_list"))
        new_post = Post.objects.get(title="New Post")
        self.assertEqual(new_post.title, "New Post")
        self.assertEqual(new_post.content, "New content")
        self.assertEqual(new_post.category, None)

    def test_not_authenticated_user(self):
        """ ログインしていないユーザーは投稿できず、ログインページにリダイレクトされること """
        self.client.logout()
        response = self.client.post(reverse("blog:post_create"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/post/new/")


class PostUpdateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_category_name = "TestCategory"
        test_category = Category.objects.create(name=cls.test_category_name)
        cls.test_original_title = "Original Title"
        cls.test_original_content = "Original Content"
        Post.objects.create(title=cls.test_original_title,
                            content=cls.test_original_content,
                            category=test_category)
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass")

    def setUp(self):
        self.client.login(username="testuser", password="testpass")

    def test_view_url_exists_at_desired_location(self):
        post_id = Post.objects.get(title=self.test_original_title).id
        response = self.client.get(f"/post/{post_id}/edit/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        post_id = Post.objects.get(title=self.test_original_title).id
        response = self.client.get(reverse("blog:post_update", args=[post_id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        post_id = Post.objects.get(title=self.test_original_title).id
        response = self.client.get(reverse("blog:post_update", args=[post_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_form.html")

    def test_form_display(self):
        """ フォームが適切に表示されること """
        post_id = Post.objects.get(title=self.test_original_title).id
        response = self.client.get(reverse("blog:post_update", args=[post_id]))
        self.assertIsInstance(response.context["form"], PostForm)

    def test_redirects_after_POST(self):
        """ 正しいデータをPOSTした後に適切なページにリダイレクトすること """
        post_id = Post.objects.get(title=self.test_original_title).id
        category_id = Category.objects.get(name="TestCategory").id
        response = self.client.post(
            reverse("blog:post_update", args=[post_id]), {
                "title": "Updated Title",
                "content": "Updated Content",
                "category": category_id})
        self.assertRedirects(response, reverse("blog:post_list"))

    def test_update_post(self):
        """ POSTによって投稿が適切に更新されること """
        post_id = Post.objects.get(title=self.test_original_title).id
        category_id = Category.objects.get(name="TestCategory").id
        self.client.post(reverse("blog:post_update", args=[post_id]), {
                         "title": "Updated Title",
                         "content": "Updated Content",
                         "category": category_id})
        updated_post = Post.objects.get(id=post_id)
        self.assertEqual(updated_post.title, "Updated Title")
        self.assertEqual(updated_post.content, "Updated Content")
        self.assertEqual(updated_post.category.id, category_id)

    def test_invalid_post_update(self):
        """ 無効なデータでPOSTした場合は更新されないこと """
        post_id = Post.objects.get(title=self.test_original_title).id
        category_id = Category.objects.get(name="TestCategory").id
        self.client.post(reverse("blog:post_update", args=[post_id]), {
                         "title": "",
                         "content": "Updated Content",
                         "category": category_id})
        updated_post = Post.objects.get(id=post_id)
        self.assertEqual(updated_post.title, self.test_original_title)
        self.assertEqual(updated_post.content, self.test_original_content)
        self.assertEqual(updated_post.category.id, category_id)

    def test_not_authenticated_user(self):
        """ ログインしていないユーザーは更新できず、ログインページにリダイレクトされること """
        self.client.logout()
        post_id = Post.objects.get(title=self.test_original_title).id
        response = self.client.post(
            reverse("blog:post_update", args=[post_id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/post/{post_id}/edit/")


class PostDeleteViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_post_title = "Test Post"
        test_category = Category.objects.create(name="TestCategory")
        Post.objects.create(
            title=cls.test_post_title,
            content="Content of the post",
            category=test_category)
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass")

    def setUp(self):
        self.client.login(username="testuser", password="testpass")

    def test_view_url_exists_at_desired_location(self):
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(f"/post/{post_id}/delete/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(reverse("blog:post_delete", args=[post_id]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.get(reverse("blog:post_delete", args=[post_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/post_confirm_delete.html")

    def test_redirects_after_delete_post(self):
        """ 投稿を削除した後に適切なページにリダイレクトすることï """
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.post(
            reverse("blog:post_delete", args=[post_id]))
        self.assertRedirects(response, reverse("blog:post_list"))

    def test_delete_post(self):
        """ 投稿が実際に削除されること """
        post_id = Post.objects.get(title=self.test_post_title).id
        self.client.post(reverse("blog:post_delete", args=[post_id]))
        self.assertFalse(Post.objects.filter(id=post_id).exists())

    def test_not_authenticated_user(self):
        """ ログインしていないユーザーは削除できず、ログインページにリダイレクトされることï """
        self.client.logout()
        post_id = Post.objects.get(title=self.test_post_title).id
        response = self.client.post(
            reverse("blog:post_delete", args=[post_id]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/post/{post_id}/delete/")
        self.assertTrue(Post.objects.filter(id=post_id).exists())
