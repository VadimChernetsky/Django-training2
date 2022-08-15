from django.template.loader import render_to_string
from django.core.signing import Signer

from mercury.settings import ALLOWED_HOSTS

from datetime import datetime
from os.path import splitext

signer = Signer()

#код, реализующий отправку писем с оповещаниями об активации
def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = 'http://' + ALLOWED_HOSTS[0]
    else:
        host = 'http://localhost:8000'
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_user.txt', context)
    body_text = render_to_string('email/activation_cod.txt', context)
    user.email_user(subject, body_text)

#генерация имен сохраняемых в модели выгруженных файлов
def get_timestamp_path(instance, filename):
    return '%s%s' % (datetime.now().timestamp(), splitext(filename)[1])