# myproject/urls.py
from django.contrib import admin
from django.urls import path
from . import views
from myapp.views import start_test 
from myapp.views import index

# urls.py


urlpatterns = [
path('', index, name='home'),
path('create-project/', views.create_project, name='create_project'),
path('become-annotator/', views.become_annotator, name='become_annotator'),
path('start-test/', views.start_test, name='start_test'),
path('submit-test/', views.submit_test, name='submit_test'),
path('test_results/', views.test_results, name='test_results'),

# path('sign-in/', views.sign_in, name='sign_in'),
]
