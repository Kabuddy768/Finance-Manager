
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('profile/<int:user_id>/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.register, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reports/', views.reports_view, name='reports'),
    path('budget/', views.budget_view, name='budget'),
    path('budget/add/', views.add_budget, name='add_budget'),
    path('budget/category/<int:category_id>/insights/', views.category_insights, name='category_insights'),
    path('budget/edit/<int:category_id>/', views.edit_budget, name='edit_budget'),
    path('budget/delete/<int:category_id>/', views.delete_budget, name='delete_budget'),
    path('savings/add/', views.add_savings_goal, name='add_savings_goal'),
    path('savings/', views.view_savings_goals, name='view_savings_goals')


]
