from django.views.generic import View, TemplateView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import login
from django.contrib.auth.models import Group, User
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.db.models import Q


from .forms import UserRegistrationForm, UserEditForm, WorkerProfileForm
from .models import WorkerProfile
from .tokens import account_activation_token
from .utils import check_groups_exist
from .tasks import send_activation_email_task

from tasks.models import Task


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = "Це ім'я вже використовується."
    return JsonResponse(data)


def validate_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=email).exists()
    }
    if data['is_taken']:
        data['error_message'] = "Цей email вже використовується."
    return JsonResponse(data)


class DashboardView(LoginRequiredMixin, ListView):
    model = Task
    paginate_by = 15
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_list'] = Task.STATUS_CHOICES
        if self.request.user.groups.filter(name='Client').exists():
            context['selected_status'] = self.kwargs.get('status',
                                                         Task.WAITING_FOR_FEE)
        else:
            context['selected_status'] = self.kwargs.get('status',
                                                         Task.IN_PROGRESS)
        return context

    def get_queryset(self):
        user = self.request.user
        status_list = [i for i, _ in Task.STATUS_CHOICES]
        if user.groups.filter(name='Client').exists():
            selected_status = self.kwargs.get('status', Task.WAITING_FOR_FEE)
        else:
            selected_status = self.kwargs.get('status', Task.IN_PROGRESS)
        task_list = Task.objects.filter(Q(creator=user) | Q(executor=user))
        if selected_status in status_list:
            return task_list.filter(status=selected_status)
        elif selected_status == 'all':
            return task_list
        else:
            raise Http404


class RegisterView(View):
    user_form_class = UserRegistrationForm
    profile_form_class = WorkerProfileForm
    template_name = 'accounts/register.html'

    def get(self, request):
        return render(request, self.template_name,
                      {'user_form': self.user_form_class(),
                       'profile_form': self.profile_form_class(),
                       'languages': Task.LANGUAGES})

    def post(self, request):
        check_groups_exist()

        user_form = self.user_form_class(request.POST)
        if user_form.is_valid():
            role = user_form.cleaned_data.get('role')
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            if role == 'Client':
                group = Group.objects.get(name='Client')
                group.user_set.add(new_user)

                send_activation_email_task(request, new_user.id)
                return redirect('accounts:account_activation_sent')
            elif role == 'Worker':
                group = Group.objects.get(name='Worker')
                group.user_set.add(new_user)

                WorkerProfile.objects.create(user=new_user)
                new_user.refresh_from_db()
                profile_form = self.profile_form_class(request.POST,
                                                       request.FILES,
                                                       instance=new_user.worker_profile)
                if profile_form.is_valid():
                    profile_form.save()
                    send_activation_email_task(request, new_user.id)
                    return redirect('accounts:account_activation_sent')
                else:
                    return render(request, self.template_name,
                                  {'user_form': user_form,
                                   'profile_form': profile_form})
        else:
            return render(request, self.template_name,
                          {'user_form': user_form,
                           'profile_form': self.profile_form_class()})

        return render(request, self.template_name,
                      {'user_form': self.user_form_class(),
                       'profile_form': self.profile_form_class()})


class AccountActivationView(TemplateView):
    template_name = 'accounts/account_activation_sent.html'


class AccountActivationConfirmView(View):
    template_name = 'accounts/account_activation_confirm.html'

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError,
                User.DoesNotExist):
            user = None

        if user is not None and \
                account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
            message = 'Email підтверджено. Дякуємо за реєстрацію!'
            alert_class = 'alert-success'
        else:
            message = 'Посилання не є дійсним.'
            alert_class = 'alert-warning'

        return render(request, self.template_name, {'message': message,
                                                    'alert_class': alert_class})


class EditInfoView(LoginRequiredMixin, View):
    user_form = UserEditForm
    profile_form = WorkerProfileForm
    template_name = 'accounts/edit.html'

    def get(self, request):
        user_form = self.user_form(instance=request.user)
        if hasattr(request.user, 'worker_profile'):
            profile_form = self.profile_form(instance=request.user.worker_profile)
            return render(request, self.template_name,
                          {'user_form': user_form,
                           'profile_form': profile_form,
                           'languages': Task.LANGUAGES})
        return render(request, self.template_name,
                      {'user_form': user_form})

    def post(self, request):
        user_form = self.user_form(instance=request.user,
                                   data=request.POST)
        # if user has worker_profile
        if hasattr(request.user, 'worker_profile'):
            profile_form = self.profile_form(
                instance=request.user.worker_profile,
                data=request.POST,
                files=request.FILES)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профіль успішно оновлено.')
            else:
                messages.error(request, 'Зміни не збережено.')

            return render(request, self.template_name,
                          {'user_form': user_form,
                           'profile_form': profile_form,
                           'languages': Task.LANGUAGES})

        # if user doesn't have worker_profile
        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Профіль успішно оновлено.')
        else:
            messages.error(request, 'Зміни не збережено.')

        return render(request, self.template_name,
                      {'user_form': user_form})


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('accounts:login')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if hasattr(user, 'worker_profile'):
            profile = WorkerProfile.objects.get(user=user)
            profile.delete()
        messages.success(request, 'Профіль видалено.')
        return super().delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj != self.request.user:
            messages.error(self.request, 'У Вас немає доступу до цієї операції.')
            return redirect(reverse('accounts:edit'))
        return obj


class ExecutorDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/executor_detail.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['languages'] = obj.worker_profile.languages.split(',')
        return context

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj.groups.filter(name='Worker').exists():
            return obj
        raise Http404
