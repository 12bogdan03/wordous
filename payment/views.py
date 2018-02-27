from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from tasks.models import Task
from notifications.tasks import create_notification_task

from liqpay import LiqPay


class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'payment/payment.html'

    def get(self, request, *args, **kwargs):
        task = Task.objects.get(pk=kwargs['pk'])
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        params = {
            'action': 'p2p',
            'amount': str(task.estimated_price),
            'order_id': str(task.pk),
            'currency': 'UAH',
            'description': 'Оплата за завдання #{}'.format(task.pk),
            'version': '3',
            'sandbox': settings.LIQPAY_SANDBOX_MODE,
            'receiver_card': task.executor.worker_profile.card_number,
            'server_url': settings.LIQPAY_SERVER_URL,
        }
        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_data(params)
        return render(request, self.template_name, {'signature': signature,
                                                    'data': data,
                                                    'task': task})


@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request, *args, **kwargs):
        liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        sign = liqpay.str_to_sign(settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY)
        if sign == signature:
            response = liqpay.decode_data_from_str(data)
            if settings.LIQPAY_SANDBOX_MODE:
                expected_status = 'sandbox'
            else:
                expected_status = 'success'
            if response['status'] == expected_status:
                task = Task.objects.get(pk=int(response['order_id']))
                task.status = Task.DONE
                task.save()
                create_notification_task.delay(
                    task.executor.id, task.id,
                    'Оплата завдання',
                    'Завдання #{} було оплачено.'.format(task.id)
                )
                return HttpResponse("OK")

        return HttpResponse("Oops! Something went wrong.")
