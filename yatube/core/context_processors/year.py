import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    date = datetime.date.today()
    return {
        'year': date.year,
    }
