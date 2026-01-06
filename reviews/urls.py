from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Beer URLs
    path('', views.beer_list, name='beer_list'),
    path('beer/add/', views.beer_create, name='beer_create'),
    path('beer/<slug:slug>/', views.beer_detail, name='beer_detail'),
    path('beer/<slug:beer_slug>/review/', views.review_create,
         name='review_create'),
    
    # Review URLs
    path('reviews/', views.review_list, name='review_list'),
    path('review/<int:pk>/', views.review_detail, name='review_detail'),
    path('review/new/', views.review_create, name='review_create_new'),
    
    # Category and Brewery URLs
    path('category/<slug:slug>/', views.category_detail,
         name='category_detail'),
    path('breweries/', views.brewery_list, name='brewery_list'),
    path('brewery/<slug:slug>/', views.brewery_detail, name='brewery_detail'),
    
    # AJAX URLs
    path('ajax/like/<int:review_id>/', views.toggle_like, name='toggle_like'),
]
