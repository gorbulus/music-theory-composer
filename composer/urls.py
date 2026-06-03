from django.urls import path
from . import views

app_name = 'composer'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/theory/', views.theory_data, name='theory_data'),
    path('api/save/', views.save_combination, name='save_combination'),
    path('api/delete/<int:pk>/', views.delete_combination, name='delete_combination'),
    path('api/load/<int:pk>/', views.load_combination, name='load_combination'),
    path('saved/', views.saved_list, name='saved_list'),
]
