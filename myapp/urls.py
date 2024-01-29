from django.contrib import admin
from django.urls import path
from .views import sign_out
from . import views
from myapp.views import index, create_project, become_annotator,handle_annotation_submission, start_test, submit_test, test_results, sign_in, start_annotation

urlpatterns = [
    # path('', index, name='home'),
    path('create-project/', create_project, name='create_project'),
    path('start-test/', start_test, name='start_test'),
    path('submit-test/', submit_test, name='submit_test'),
    path('test_results/', test_results, name='test_results'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('become-annotator/', views.become_annotator, name='become_annotator'),
    path('annotate/', views.handle_annotation_submission, name='handle_annotation_submission'),
    path('start_annotation/', views.start_annotation, name='start_annotation'),
    path('enter-password/', views.enter_password, name='enter_password'),
    path('sign-out/', sign_out, name='sign_out'),
    path('app-review/', views.app_review_form, name='app_review_form'),
    path('review-classification/', views.review_classification, name='review_classification'),
    path('check-email/', views.check_email, name='check_email'),
    path('', views.index, name='index'),
    
    # Other paths as needed...
]