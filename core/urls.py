from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('admin/populate-db/', views.populate_database, name='populate_database'),
    path('admin/scrape-beers/', views.scrape_beers_daily, name='scrape_beers_daily'),
]
