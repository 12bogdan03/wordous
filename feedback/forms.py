from django import forms


class FeedbackForm(forms.Form):
    QUESTION = 'question'
    BUG = 'bug'
    IDEA = 'idea'
    OTHER = 'other'

    SUBJECT_CHOICES = (
        (QUESTION, 'Запитання'),
        (BUG, 'Повідомлення про знайдену помилку/баг'),
        (IDEA, 'Пропозиція щодо роботи сайту'),
        (OTHER, 'Інше')
    )

    subject = forms.ChoiceField(label='Тема', choices=SUBJECT_CHOICES)
    from_email = forms.EmailField(label='Email')
    message = forms.CharField(label='Повідомлення', max_length=1000,
                              widget=forms.Textarea(attrs={'rows': 5}))
