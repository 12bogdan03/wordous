from django.views.generic import View
from django.http import JsonResponse

from .forms import FeedbackForm
from .tasks import send_feedback_email_task


class SendFeedbackView(View):
    form_class = FeedbackForm

    def post(self, request):
        form = self.form_class(request.POST)
        result = False
        if form.is_valid():
            dict_choices = dict(FeedbackForm.SUBJECT_CHOICES)
            subject = dict_choices[form.cleaned_data['subject']]
            result = True
            send_feedback_email_task.delay(subject,
                                           form.cleaned_data['from_email'],
                                           form.cleaned_data['message'])
            return JsonResponse(result, safe=False)

        return JsonResponse(result, safe=False)
