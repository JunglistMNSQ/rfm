from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='main'),
    path('register/', views.Register.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('parse/', views.Parse.as_view(), name='parse'),
    path('corrupt_data/', views.CorruptData.as_view(), name='corrupt_data'),
    path('my_tables/', views.MyTables.as_view(), name='my_tables'),
    path('my_tables/<slug>', views.ManageTab.as_view(), name='manage_tab'),
    path('my_tables/<slug>/clients', views.ClientList.as_view(),
         name='client_list'),
    path('my_tables/<slug_tab>/clients/<slug>',
         views.ClientCard.as_view(),
         name='client_card'),
    path('my_tables/<slug>/delete/', views.Delete.as_view(), name='delete'),
    path('my_tables/<slug>/rules/', views.RulesList.as_view(), name='rules'),
    path('my_tables/<slug>/rules/new/', views.NewRule.as_view(),
         name='new_rule'),
    path('my_tables/<slug_tab>/rules/<slug>', views.EditRule.as_view(),
         name='rule'),
    path('log/', views.Log.as_view(), name='log')
]

urlpatterns += staticfiles_urlpatterns()
