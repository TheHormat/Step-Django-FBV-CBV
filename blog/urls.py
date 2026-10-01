from django.urls import path

from . import views

app_name = "blog"       # ad sahəsi: reverse("blog:post_detail") — başqa app-ın adları ilə qarışmır

urlpatterns = [
    # [DƏRS 7]
    # path("", views.post_list, name="post_list"),
    path("", views.PostListView.as_view(), name="post_list"),  # [DƏRS 12] CBV
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("about/", views.about, name="about"),

    # [EV 7]
    path("contact/", views.contact, name="contact"),
    path("categories/", views.category_list, name="category_list"),
    # [EV 11] ⚠ "category/new/" slug-lı sətirdən ƏVVƏL durmalıdır — yoxsa Django "new"-nu slug sanır
    path("category/new/", views.category_create, name="category_create"),
    # path("category/<slug:slug>/", views.category_detail, name="category_detail"),
    path("category/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),  # [DƏRS 12] CBV
    path("author/<str:name>/", views.author_posts, name="author_posts"),
    path("stats/", views.stats, name="stats"),

    # [EV 8]
    path("latest/", views.latest, name="latest"),

    # [DƏRS 11] "post/new/" int deyil, ona görə post/<int:post_id>/ ilə qarışmır
    # path("post/new/", views.post_create, name="post_create"),
    path("post/new/", views.PostCreateView.as_view(), name="post_create"),  # [DƏRS 12] CBV
    path("post/<int:post_id>/edit/", views.PostEditView.as_view(), name="post_edit"),
    path("post/<int:post_id>/delete/", views.PostDeleteView.as_view(), name="post_delete"),

    # [PRAKTİKA 11]
    path("comment/<int:comment_id>/reply/", views.comment_reply, name="comment_reply"),

    # [EV 11]
    # path("post/<int:post_id>/delete/", views.post_delete, name="post_delete"),

    # [PRAKTİKA 12]
    path("my-posts/", views.my_posts, name="my_posts"),

    # [EV 12]
    path("comment/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),

    # [PRAKTİKA 10]
    path("tag/<slug:slug>/", views.tag_detail, name="tag_detail"),

    # [EV 10]
    path("tags/", views.tag_list, name="tag_list"),
    path("search/<str:word>/", views.search, name="search"),     # bonus
]
