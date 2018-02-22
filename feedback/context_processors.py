from .forms import FeedbackForm


def feedback_form_processor(request):
    return {'feedback_form': FeedbackForm}
