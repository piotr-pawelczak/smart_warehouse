from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import Group, User
import random
import string
from .forms import UserRegisterForm, UserUpdateForm

# Create your views here.


@login_required
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)

            alphabet = string.ascii_letters + string.digits
            temp = random.sample(alphabet, 20)
            password = "".join(temp)

            new_user.set_password(password)
            new_user.save()

            user_group = user_form.cleaned_data['group']
            if user_group == 'employee' or user_group == 'admin':
                employee_group = Group.objects.get(name='employee')
                employee_group.user_set.add(new_user)
            if user_group == 'admin':
                administrator_group = Group.objects.get(name='admin')
                administrator_group.user_set.add(new_user)

            context = {'new_user': new_user, 'password': password}
            return render(request, 'account/user_created.html', context)
    else:
        user_form = UserRegisterForm()

    context = {'user_form': user_form}

    return render(request, 'account/register.html', context)


def user_detail(request, pk):
    user = get_object_or_404(User, id=pk)

    edit_form = UserUpdateForm(instance=user)
    if request.method == 'POST':
        edit_form = UserUpdateForm(request.POST, instance=user)
        if edit_form.is_valid():
            edit_form.save()
            return redirect(reverse_lazy('account:profile', args=[user.id]))

    context = {'user': user, 'edit_form': edit_form}
    return render(request, 'account/profile.html', context)




