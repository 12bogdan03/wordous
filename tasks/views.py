from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.views import generic
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Task, Comment
from .forms import CommentForm, TaskCreateForm, TaskEditForm, TaskExecuteForm
from notifications.tasks import create_notification_task


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = 'task_list'
    template_name = 'tasks/task_list.html'
    paginate_by = 15

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kind_list'] = Task.KIND_CHOICES
        context['selected_kind'] = self.kwargs.get('kind', 'all')
        context['languages'] = Task.LANGUAGES
        return context

    def get_queryset(self):
        kind_list = [i for i, _ in Task.KIND_CHOICES]
        selected_kind = self.kwargs.get('kind', 'all')
        task_list = Task.objects.filter(status=Task.NEW).order_by('deadline')
        query = self.request.GET.get('q')
        if selected_kind in kind_list:
            if query:
                return task_list.filter(
                    Q(language__icontains=query) | Q(translation_language__icontains=query),
                    kind=selected_kind
                )
            return task_list.filter(kind=selected_kind)
        elif selected_kind == 'all':
            if query:
                return task_list.filter(
                    Q(language__icontains=query) | Q(translation_language__icontains=query)
                )
            return task_list
        else:
            raise Http404


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = Comment.objects.filter(task=self.object)
        if self.object.status == Task.DONE and \
           self.request.user == self.object.creator:
            context['solution_file'] = self.object.solution_file
        return context


class TaskCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = 'tasks/task_create.html'
    raise_exception = True

    def test_func(self):
        return self.request.user.groups.filter(name='Client').exists()

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['languages'] = Task.LANGUAGES
        return context


class TaskUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Task
    form_class = TaskEditForm
    template_name = 'tasks/task_update.html'
    context_object_name = 'task'
    success_message = 'Завдання успішно оновлено.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task'] = self.object
        return context

    def get_object(self, queryset=None):
        obj = super(TaskUpdateView, self).get_object()
        if obj.creator != self.request.user:
            messages.error(self.request, 'У Вас немає доступу до цієї операції.')
            raise PermissionDenied
        elif obj.status != Task.NEW:
            messages.error(self.request, 'Внести зміни неможливо.')
            raise PermissionDenied
        return obj


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks:task_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Завдання було успішно видалено.')
        return super().delete(request, *args, **kwargs)

    def get_object(self, queryset=None):
        obj = super(TaskDeleteView, self).get_object()
        if obj.creator != self.request.user:
            messages.error(self.request, 'У Вас немає доступу до цієї операції.')
            return redirect(obj)
        elif obj.status == Task.IN_PROGRESS:
            messages.error(self.request, 'Необхідно провести оплату перед видаленням.')
            return redirect(obj)
        return obj


class CommentCreateView(LoginRequiredMixin, generic.View):
    form_class = CommentForm
    http_method_names = ['post']

    def post(self, request, task_id):
        form = self.form_class(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.creator = request.user
            task = get_object_or_404(Task, pk=task_id)
            comment.task = task
            comment.save()
            if comment.creator != task.creator:
                create_notification_task.delay(user_id=task.creator.id,
                                               task_id=task.id,
                                               title='Новий коментар',
                                               text="У завдання #{} з'явився новий"
                                                    " коментар.".format(task.pk))
            messages.success(request, 'Коментар додано.')
        else:
            messages.error(request, 'Не вдалося додати коментар.')

        return redirect('tasks:task_detail', pk=task_id)


class BecomeTaskExecutorView(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        task = Task.objects.filter(pk=kwargs['pk']).first()
        is_worker = request.user.groups.filter(name='Worker').exists()
        if is_worker and task.status == Task.NEW:
            task.executor = request.user
            task.status = Task.IN_PROGRESS
            task.save()
            create_notification_task.delay(user_id=task.creator.id,
                                           task_id=task.id,
                                           title='Завдання в роботі',
                                           text="Завдання #{} було взято до "
                                                "роботи.".format(task.pk))
            messages.success(request, 'Завдання взято до роботи.')
            return redirect('tasks:task_execute', pk=task.id)

        messages.error(request, 'Ваш акаунт не відповідає вимогам для виконання '
                                'цієї операції або завдання вже виконується '
                                'чи завершене.')
        return redirect('tasks:task_detail', pk=task.id)


class TaskExecuteView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = Task
    form_class = TaskExecuteForm
    template_name = 'tasks/task_execute.html'
    context_object_name = 'task'
    success_message = 'Завдання успішно виконано.'
    raise_exception = True

    def test_func(self):
        task = self.get_object()
        return task.executor == self.request.user and \
            task.status == Task.IN_PROGRESS

    def form_valid(self, form):
        super().form_valid(form)
        form.instance.status = Task.WAITING_FOR_FEE
        form.instance.generate_solution_preview()
        form.instance.save()
        create_notification_task.delay(user_id=form.instance.creator.id,
                                       task_id=form.instance.id,
                                       title='Завдання виконано',
                                       text="Завдання #{} було виконано. Вам "
                                            "доступне прев'ю результату. "
                                            "Будь ласка, здійсніть "
                                            "оплату, щоб отримати повний файл з "
                                            "результатом.".format(form.instance.pk))
        return HttpResponseRedirect(self.get_success_url())
