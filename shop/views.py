from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Homepage with featured products and welcome message."""
    template_name = 'shop/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Welcome'
        # TODO: Add featured products when Product model is ready
        # context['featured_products'] = Product.objects.filter(is_featured=True)[:6]
        return context


class AboutView(TemplateView):
    """About page for Joana."""
    template_name = 'shop/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'About'
        return context
