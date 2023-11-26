from django.contrib import admin
from django.urls import path
from . import views
from myapp.views import index, create_project, become_annotator, start_test, submit_test, test_results, sign_in, start_annotation

urlpatterns = [
    path('', index, name='home'),
    path('create-project/', create_project, name='create_project'),
    path('become-annotator/', become_annotator, name='become_annotator'),
    path('start-test/', start_test, name='start_test'),
    path('submit-test/', submit_test, name='submit_test'),
    path('test_results/', test_results, name='test_results'),
    path('sign-in/', sign_in, name='sign_in'),
    path('annotate/', start_annotation, name='start_annotation'),  # Corrected path for start_annotation
    # Other paths as needed...
]
