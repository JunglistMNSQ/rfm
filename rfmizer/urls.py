from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    # path('login/', views.user_login, name='login'),
    path('register/', views.Register.as_view(), name='register'),
    # path('personal/', views.personal_area, name='personal'),
    path('upload/', views.Upload.as_view(), name='upload'),
    path('parse/', views.Parse.as_view(), name='parse'),
    # path('my_tables/', views.my_tables, name='my_tables'),
    # path('my_tables/<slug>', views.manage_tab, name='manage_tab'),
    # path('my_tables/<slug>/clients', views.clients_list,
    #      name='clients_list'),
    # path('my_tables/<slug_tab>/clients/<slug_client>',
    #      views.client_card,
    #      name='client_card'),
    # path('my_tables/<slug>/delete/', views.delete_tab, name='delete'),
    # path('my_tables/<slug>/rfmize/', views.rfmize_tab, name='rfmize'),
    # path('my_tables/<slug>/rules/', views.rules_tab, name='rules'),
    # path('my_tables/<slug>/rules/new/', views.new_rule,
    #      name='new_rule'),
    # path('my_tables/<slug>/rules/run_rules/', views.run_rules,
    #      name='run_rules'),
    # path('my_tables/<slug_tab>/rules/<slug_rule>', views.rule,
    #      name='rule'),
    path('log/', views.Log.as_view(), name='log')
]

urlpatterns += staticfiles_urlpatterns()