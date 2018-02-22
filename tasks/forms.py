from django import forms

from .models import Comment, Task

import os


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class TaskCreateForm(forms.ModelForm):
    kind = forms.ChoiceField(choices=Task.KIND_CHOICES,
                             widget=forms.RadioSelect(),
                             label='Тип завдання')

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if file._size > 50 * 1024 * 1024:
                raise forms.ValidationError("Файл занадто великий (>50Mb).")
            return file
        else:
            raise forms.ValidationError("Не вдалося завантажити файл.")

    class Meta:
        model = Task
        fields = ['kind', 'language', 'translation_language',
                  'description', 'deadline', 'file', 'estimated_price']
        labels = {
            'language': 'Мова тексту',
            'translation_language': 'Мова перекладу',
            'description': 'Опис',
            'deadline': 'Дедлайн',
            'file': 'Файл',
            'estimated_price': 'Вартість',
        }
        help_texts = {
            'description': 'Додатковий опис завдання. Не обов\'язково, але це '
                           'допоможе виконавцям максимально точно виконати завдання.',
            'deadline': 'Час, до якого завдання потрібно виконати.',
            'file': 'Оберіть файл, в якому знаходиться Ваш текст. Розмір не повинен перевищувати 50Mb.',
            'estimated_price': 'Ваша пропозиція вартості виконання цього завдання.'
        }


class TaskEditForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['description', 'deadline', 'file', 'estimated_price']
        labels = {
            'description': 'Опис',
            'deadline': 'Дедлайн',
            'file': 'Файл',
            'estimated_price': 'Вартість',
        }


class TaskExecuteForm(forms.ModelForm):
    solution_file = forms.FileField(label='Файл з виконаним завданням',
                                    help_text='Розмір не повинен перевищувати 50Mb.<br>'
                                              'Формат файлу - .docx',
                                    widget=forms.FileInput(attrs={
                                        'accept': '.docx'
                                    }))

    def clean_solution_file(self):
        solution_file = self.cleaned_data.get('solution_file')
        if solution_file:
            if solution_file._size > 50 * 1024 * 1024:
                raise forms.ValidationError("Файл занадто великий (>50Mb).")
            ext = os.path.splitext(solution_file._name)[1]
            if ext.lower() != '.docx':
                raise forms.ValidationError('Невірний формат файлу. '
                                            'Завантажувати можна тільки .docx файли.')
            return solution_file
        else:
            raise forms.ValidationError("Не вдалося завантажити файл.")

    class Meta:
        model = Task
        fields = ['solution_file']
