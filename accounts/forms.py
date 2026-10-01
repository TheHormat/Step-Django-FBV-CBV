from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# [EV 12] bonus — hazır UserCreationForm-dan inheritance (Dərs 4): email sahəsi əlavə olunur.
# Parol sahələri parent-də yazılıb, ona görə burada təkrar yazmırıq.
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email"]
