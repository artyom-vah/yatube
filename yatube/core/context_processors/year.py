from django.utils.timezone import now


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': now().year
    }
