from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import Group, User
import random
import string
from .forms import UserRegisterForm, UserUpdateForm, UserUpdateFormAdmin

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


@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, id=pk)

    if request.user.groups.filter(name="admin").exists():
        edit_form = UserUpdateFormAdmin(instance=user)
    else:
        edit_form = UserUpdateForm(instance=user)

    if request.method == 'POST':

        if request.user.groups.filter(name="admin").exists():
            edit_form = UserUpdateFormAdmin(request.POST, instance=user)
        else:
            edit_form = UserUpdateForm(request.POST, instance=user)

        if edit_form.is_valid():
            updated_user = edit_form.save()

            user_group = edit_form.cleaned_data['group']

            administrator_group = Group.objects.get(name='admin')
            employee_group = Group.objects.get(name='employee')
            if user_group == 'employee':
                employee_group.user_set.add(updated_user)
                administrator_group.user_set.remove(updated_user)
            if user_group == 'admin':
                employee_group.user_set.add(updated_user)
                administrator_group.user_set.add(updated_user)

            if request.user.groups.filter(name="admin").exists():
                return redirect(reverse_lazy("account:user_list"))

            return redirect(reverse_lazy('account:profile', args=[user.id]))

    context = {'user': user, 'edit_form': edit_form}
    return render(request, 'account/profile.html', context)


@login_required
def user_list(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'account/user_list.html', context)


def user_delete(request, pk):
    user = get_object_or_404(User, id=pk)
    if request.method == 'POST':
        user.delete()
        messages.warning(request, 'Użytkownik został usunięty')
    return redirect(reverse('account:user_list'))




