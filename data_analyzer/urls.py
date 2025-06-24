# data_analyzer/urls.py
from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('files/', views.file_list, name='file_list'),
    path('delete/<int:pk>/', views.delete_file, name='delete_file'),
    path('visualize/', views.visualize_data, name='visualize_data'),
    path('api/sheets/', views.get_sheets, name='get_sheets'),
    path('api/columns/', views.get_columns, name='get_columns'),
    path('api/plot/', views.plot_graph, name='plot_graph'),
    path('api/export/', views.export_graph, name='export_graph'),
    
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
]