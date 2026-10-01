from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CommentForm, PostForm, CategoryForm, ContactForm
from .models import Post, Category, Tag, Comment, ContactMessage

# CBV (Class Based View) ilə işləmək üçün:
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin  

# Nişanlar:
#   [DƏRS 12]     — müəllim I hissədə canlı yazır
#   [PRAKTİKA 12] — tələbə II hissədə yazır
#   [EV 12]       — ev tapşırığının həlli
# Köhnə nişanlar ([DƏRS 11], [EV 11] …) həmin sətrin hansı dərsdə yarandığını göstərir.
#
# Form view-unun qəlibi (hər yerdə eynidir):
#   POST gəldi  → formu məlumatla doldur → is_valid() → save() → redirect
#   GET gəldi   → boş form göstər
#   səhvdirsə   → eyni formu xətaları ilə yenidən göstər


# ─────────────────────────── postlar ───────────────────────────

# def post_list(request):                                           # [DƏRS 9]
#     posts = Post.objects.filter(is_published=True)
#     return render(request, "blog/post_list.html", {"posts": posts})

class PostListView(ListView):                                      # [DƏRS 12] CBV
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    queryset = Post.objects.filter(is_published=True)
    paginate_by = 4


def post_detail(request, post_id):                                # [DƏRS 9]
    post = get_object_or_404(Post, id=post_id)

    # [EV 12] tapşırıq 6 — qaralamanı yalnız öz müəllifi aça bilər, başqaları üçün 404
    if not post.is_published and post.author != request.user:
        raise Http404("Post tapılmadı")

    # [DƏRS 11] şərh formu — eyni view həm göstərir (GET), həm qəbul edir (POST)
    if request.method == "POST":
        if not request.user.is_authenticated:                     # [EV 12] tapşırıq 1 — şərhi yalnız giriş edən yazır
            return redirect("accounts:login")
        form = CommentForm(request.POST)                          # formu gələn məlumatla doldur
        if form.is_valid():                                       # bütün yoxlamalar keçdi?
            comment = form.save(commit=False)                     # obyekt yarat, amma bazaya HƏLƏ yazma
            comment.post = post                                   # formda olmayan sahəni özümüz doldururuq
            comment.author = request.user                         # [EV 12] tapşırıq 1
            comment.save()                                        # indi yaz
            messages.success(request, "Şərhin əlavə olundu.")
            return redirect(post)                                 # POST-dan sonra HƏMİŞƏ redirect
    else:
        form = CommentForm()                                      # GET → boş form

    # [EV 9] baxış sayı
    post.views += 1
    post.save()

    # [PRAKTİKA 11] parent=None → yalnız əsas şərhlər. Cavablar template-də comment.replies ilə gəlir
    comments = post.comments.filter(is_active=True, parent=None)

    # [EV 10] oxşar postlar
    similar = Post.objects.filter(category=post.category, is_published=True)
    similar = similar.exclude(id=post.id)[:3]

    context = {"post": post, "comments": comments, "similar": similar, "form": form}
    return render(request, "blog/post_detail.html", context)


# @login_required                                                   # [DƏRS 12] giriş etməyən → LOGIN_URL-ə gedir
# def post_create(request):                                         # [DƏRS 11]
#     if request.method == "POST":
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)                        # [DƏRS 12] hələ yazma —
#             post.author = request.user                            #           müəllif = giriş edən istifadəçi
#             post.save()
#             form.save_m2m()                                       # commit=False-dan sonra teqləri (M2M) ayrıca yazırıq
#             messages.success(request, "Post yaradıldı.")
#             return redirect(post)
#     else:
#         form = PostForm()
#     context = {"form": form, "page_title": "Yeni post"}
#     return render(request, "blog/post_form.html", context)


class PostCreateView(LoginRequiredMixin, CreateView):             # [DƏRS 12] CBV
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        form.save_m2m()
        messages.success(self.request, "Post yaradıldı.")
        return redirect(post)


# @login_required                                                   # [DƏRS 12]
# def post_edit(request, post_id):                                  # [DƏRS 11]
#     post = get_object_or_404(Post, id=post_id)

#     # [PRAKTİKA 12] tapşırıq 1 — yalnız müəllif. Giriş edib, amma post onun deyil → 403
#     if post.author != request.user:
#         raise PermissionDenied

#     if request.method == "POST":
#         form = PostForm(request.POST, request.FILES, instance=post)
#         if form.is_valid():
#             form.save()
#             messages.info(request, "Post yeniləndi.")
#             return redirect(post)
#     else:
#         form = PostForm(instance=post)
#     context = {"form": form, "page_title": "Postu redaktə et"}
#     return render(request, "blog/post_form.html", context)


# @login_required                                                   # [DƏRS 12]
# def post_delete(request, post_id):                                # [EV 11]
#     post = get_object_or_404(Post, id=post_id)

#     if post.author != request.user:                               # [PRAKTİKA 12] tapşırıq 1
#         raise PermissionDenied

#     if request.method == "POST":
#         post.delete()
#         messages.warning(request, "Post silindi.")
#         return redirect("blog:post_list")
#     return render(request, "blog/post_confirm_delete.html", {"post": post})


class PostEditView(LoginRequiredMixin, UpdateView):             # [DƏRS 12] CBV
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:                       # [PRAKTİKA 12] tapşırıq 1
            raise PermissionDenied
        return post

    def form_valid(self, form):
        form.save()
        messages.info(self.request, "Post yeniləndi.")
        return redirect(self.get_object())


class PostDeleteView(LoginRequiredMixin, DeleteView):             # [DƏRS 12] CBV
    model = Post
    template_name = "blog/post_confirm_delete.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:                       # [PRAKTİKA 12] tapşırıq 1
            raise PermissionDenied
        return post

    def get_success_url(self):
        messages.warning(self.request, "Post silindi.")
        return redirect("blog:post_list").url


@login_required                                                   # [PRAKTİKA 12] tapşırıq 2
def my_posts(request):
    # [EV 12] tapşırıq 6 — is_published filtri YOXDUR: müəllif öz qaralamalarını da görür
    posts = Post.objects.filter(author=request.user)
    return render(request, "blog/my_posts.html", {"posts": posts})


@login_required                                                   # [EV 12] tapşırıq 7
def comment_reply(request, comment_id):                           # [PRAKTİKA 11]
    parent = get_object_or_404(Comment, id=comment_id, is_active=True)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = parent.post                              # cavab da eyni posta aiddir
            reply.parent = parent                                 # kimə cavab verilir
            reply.author = request.user                           # [EV 12] tapşırıq 1
            reply.save()
            messages.success(request, "Cavabın əlavə olundu.")
            return redirect(parent.post)
    else:
        form = CommentForm()
    context = {"form": form, "parent": parent}
    return render(request, "blog/comment_reply.html", context)


def about(request):
    return render(request, "blog/about.html")


@login_required                                                   # [EV 12] tapşırıq 7 — öz şərhini silmək
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        raise PermissionDenied
    if request.method == "POST":                                  # silmək yalnız POST ilə
        comment.delete()
        messages.warning(request, "Şərh silindi.")
    return redirect(comment.post)


def contact(request):                                             # [EV 11]
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data                              # yoxlanmış məlumat — adi dict
            ContactMessage.objects.create(name=data["name"], email=data["email"], message=data["message"])
            messages.success(request, "Mesajın göndərildi. Təşəkkürlər!")
            return redirect("blog:contact")
    else:
        form = ContactForm()
    return render(request, "blog/contact.html", {"form": form})


# ───────────────────────── kateqoriyalar ─────────────────────────

def category_list(request):
    # [EV 10] hər kateqoriyaya post_count adlı əlavə "sütun" yapışdırılır
    categories = Category.objects.annotate(post_count=Count("posts"))
    return render(request, "blog/category_list.html", {"categories": categories})


def category_create(request):                                     # [EV 11]
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Kateqoriya yaradıldı.")
            return redirect("blog:category_list")
    else:
        form = CategoryForm()
    return render(request, "blog/category_form.html", {"form": form})


# def category_detail(request, slug):
#     category = get_object_or_404(Category, slug=slug)
#     # [DƏRS 10] tərs əlaqə
#     posts = category.posts.filter(is_published=True)
#     context = {"category": category, "posts": posts}
#     return render(request, "blog/category_detail.html", context)


class CategoryDetailView(DetailView):                              # [DƏRS 12] CBV
    model = Category
    template_name = "blog/category_detail.html"
    context_object_name = "category"
    slug_field = "slug"                                           # default: "slug"
    slug_url_kwarg = "slug"                                       # default: "slug"

    def get_context_data(self, **kwargs):                           # 
        context = super().get_context_data(**kwargs)
        context["posts"] = self.object.posts.filter(is_published=True)
        return context

# ─────────────────────────── teqlər ───────────────────────────

def tag_detail(request, slug):                                    # [PRAKTİKA 10]
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(is_published=True)
    context = {"tag": tag, "posts": posts}
    return render(request, "blog/tag_detail.html", context)


def tag_list(request):                                            # [EV 10]
    tags = Tag.objects.annotate(post_count=Count("posts"))
    return render(request, "blog/tag_list.html", {"tags": tags})


# ─────────────────────── digər səhifələr ───────────────────────

def author_posts(request, name):                                  # [EV 9]
    # [DƏRS 12] author indi User obyektidir: author__username → "müəllifin username-i"
    posts = Post.objects.filter(author__username=name, is_published=True)
    context = {"name": name, "posts": posts}
    return render(request, "blog/author_posts.html", context)


def latest(request):                                              # [EV 9]
    posts = Post.objects.filter(is_published=True).order_by("-created_at")[:3]
    return render(request, "blog/latest.html", {"posts": posts})


def stats(request):                                               # [EV 9]
    published = Post.objects.filter(is_published=True)

    # [EV 10] ən çox şərh yazılan post: əvvəl say, sonra sırala
    most_commented = published.annotate(comment_count=Count("comments"))
    most_commented = most_commented.order_by("-comment_count").first()

    context = {
        "post_count": published.count(),
        "category_count": Category.objects.count(),
        "top_post": published.order_by("-views").first(),
        "comment_count": Comment.objects.count(),                 # [EV 10]
        "tag_count": Tag.objects.count(),                         # [EV 10]
        "most_commented": most_commented,                         # [EV 10]
    }
    return render(request, "blog/stats.html", context)


def search(request, word):                                        # [EV 10] bonus
    posts = Post.objects.filter(title__icontains=word, is_published=True)
    context = {"word": word, "posts": posts}
    return render(request, "blog/search.html", context)
