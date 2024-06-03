from django.contrib import admin
from django.urls import path
from .views import sign_out
from . import views
from myapp.views import index,project_list,train_dataset,classify_reviews,invite_annotators, create_project, become_annotator,handle_annotation_submission, start_test, submit_test, test_results, sign_in, start_annotation

urlpatterns = [
    # path('', index, name='home'),
    # path('create-project/', create_project, name='create_project'),
    path('start-test/', start_test, name='start_test'),
    path('submit-test/', submit_test, name='submit_test'),
    path('test_results/', test_results, name='test_results'),
    path('sign-in/', views.sign_in, name='sign_in'),
    path('become-annotator/', views.become_annotator, name='become_annotator'),
    path('annotate/', views.handle_annotation_submission, name='handle_annotation_submission'),
    # path('start_annotation/', views.start_annotation, name='start_annotation'),
    path('enter-password/', views.enter_password, name='enter_password'),
    path('sign-out/', sign_out, name='sign_out'),
    path('app-review/', views.app_review_form, name='app_review_form'),
    path('review-classification/', views.review_classification, name='review_classification'),
    path('check-email/', views.check_email, name='check_email'),
    path('submit_annotation/', views.submit_annotation, name='submit_annotation'),
    path('', views.index, name='index'),
    path('create_project/', views.create_project, name='create_project'),
    path('projects/', project_list, name='project_list'),
    # path('train-dataset/<int:project_id>/', train_dataset, name='train_dataset'),
    path('train_dataset/<int:project_id>/', views.train_dataset, name='train_dataset'),
    path('download_labeled_file/<int:project_id>/', views.download_labeled_file, name='download_labeled_file'),
    path('invite_annotators/<int:project_id>/', invite_annotators, name='invite_annotators'),
    path('annotate_project/<str:unique_link>/', views.start_annotation, name='start_annotation'),
    path('classify_reviews/', classify_reviews, name='classify_reviews'),
 
    # Other paths as needed...
]