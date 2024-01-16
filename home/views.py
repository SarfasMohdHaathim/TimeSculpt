from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *
from django.db.models import Q




class HomeView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Watch.objects.all()
        return context



class WatchDetailView(TemplateView):
    template_name = 'details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        watch_id = kwargs['watch_id']
        watch = Watch.objects.get(id=watch_id)
        related_products = Watch.objects.filter(
            Q(brands=watch.brands) |
            Q(gender=watch.gender) |
            Q(dial_type=watch.dial_type) |
            Q(dial_colour=watch.dial_colour) |
            Q(dial_shape=watch.dial_shape) |
            Q(style=watch.style) |
            Q(strap_material=watch.strap_material)
        ).exclude(id=watch.id)[:4]
        context['watch'] = watch
        context['related_products'] = related_products
        print(related_products)
        return context