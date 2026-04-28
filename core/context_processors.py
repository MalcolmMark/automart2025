from cars.models import Car


def site_stats(request):
    return {'total_listings': Car.objects.filter(is_approved=True).count()}
