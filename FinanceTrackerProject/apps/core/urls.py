from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # home page
    path('dashboard/', views.dashboard, name='dashboard'),  # dashboard page
    path("create-plan/", views.create_plan, name="create_plan"),
    path('add-money/', views.add_money, name='add_money'),
    path('subtract-money/', views.subtract_money, name='subtract_money'),
    path('add-category/', views.add_category, name='add_category'),
]
