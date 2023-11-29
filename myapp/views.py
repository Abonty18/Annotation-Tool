from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import StudentForm
from .models import CustomUser
from django.contrib.auth import authenticate, login
from myapp.models import Review
import json
import random
from django.contrib.auth.models import User
from .models import StudentProject
from .forms import StudentForm
import os
from django.conf import settings
from .models import Review
from django.core.paginator import Paginator
from .models import StudentAnnotation, UnannotatedReview
from django.contrib.auth.decorators import login_required


def load_reviews():
    file_path = os.path.join(settings.BASE_DIR, 'myapp', 'reviews.json')
    with open(file_path, 'r') as file:
        reviews = json.load(file)
        for review_data in reviews:
            Review.objects.get_or_create(
                id=review_data['id'],
                defaults={
                    'content': review_data['content'],
                    'ground_truth_annotation': review_data['label']
                }
            )

@login_required
def start_annotation(request):
    user = request.user  # Directly use the logged-in user

    page_number = request.GET.get('page', 1)

    # Check if the user has an ongoing project
    project, created = StudentProject.objects.get_or_create(student=user)

    if not created:
        page_number = project.last_page

    # Fetch reviews for annotation
    unannotated_reviews = UnannotatedReview.objects.all()
    paginator = Paginator(unannotated_reviews, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, 'myapp/start_annotation.html', {
        'page_obj': page_obj,
        'project': project
    })




def handle_annotation_submission(request):
    if request.method == 'POST':
        student = request.user.student
        project, _ = StudentProject.objects.get_or_create(student=student)

        if 'action' in request.POST:
            if request.POST['action'] == 'save':
                # Process each annotation in the form data
                for key, value in request.POST.items():
                    if key.startswith('annotation_'):
                        review_id = int(key.split('_')[1])  # Extracting review ID
                        annotation_content = value

                        # Retrieve or create the corresponding UnannotatedReview
                        review, _ = UnannotatedReview.objects.get_or_create(id=review_id)

                        # Create or update the StudentAnnotation
                        StudentAnnotation.objects.update_or_create(
                            student=student,
                            review=review,
                            defaults={'annotation': annotation_content}
                        )

                # Update the project's last page if provided
                page_number = request.POST.get('page_number')
                if page_number:
                    project.last_page = int(page_number)
                    project.save()

                # Check if there's a project name to be saved
                project_name = request.POST.get('project_name')
                if project_name:
                    project.name = project_name
                    project.save()

                # Redirect to a confirmation page or back to the annotation page
                return redirect('home')

    # If the request method is not POST or the 'action' is not 'save', redirect to another page
    return redirect('home')



def become_annotator(request):
    # Clear any existing messages
    storage = messages.get_messages(request)
    storage.used = True
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if the email already exists in Student model
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please sign in.')
                return redirect('sign_in')  # Redirect to the sign-in page

            # Save the new Student
            form.save()

            # Redirect to an appropriate page after registration
            return redirect('start_test')
    else:
        form = StudentForm()

    return render(request, 'myapp/become_annotator.html', {'form': form})






def index(request):
    return render(request, 'myapp/index.html')
# myapp/views.py

def start_test(request):
    # Fetch all reviews from the database
    reviews = Review.objects.all()

    # Get the count of reviews or 10, whichever is smaller
    count = min(reviews.count(), 5)

    # Select random reviews
    random_reviews = random.sample(list(reviews), count)

    return render(request, 'myapp/annotation_test.html', {'reviews': random_reviews})



def create_project(request):
    # Your logic for creating a project
    return render(request, 'create_project.html')
# myapp/views.py

# def sign_in(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         if email and password:
#             user = authenticate(username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 # Redirect to the test or some other page
#                 return redirect('start_test')
#             else:
#                 messages.error(request, 'Invalid email or password.')

#     return render(request, 'myapp/sign_in.html')

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Debugging
        print("Email:", email)
        print("Password:", password)

        # user = authenticate(username=email, password=password)
        # print("User:", user)  # Check if user is not None

        # if user is not None:
        #     login(request, user)
        #     ## Get the 'next' parameter from the request
        #     next_page = request.GET.get('next', 'start_annotation')
        #     return redirect(next_page)
        user = authenticate(username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            next_page = request.GET.get('next', 'start_annotation')
            return redirect(next_page)
        else:
            messages.error(request, 'Invalid email or password.')


        # else:
        #     messages.error(request, 'Invalid email or password.')


    return render(request, 'myapp/sign_in.html')



def submit_test(request):

    if request.method == 'POST':
        user_annotations = {key: int(value) for key, value in request.POST.items() if key.startswith('annotation_')}
        correct_count = 0
        total_annotations = len(user_annotations)

        if total_annotations == 0:
            messages.error(request, 'No annotations were submitted.')
            print("Total annotations:", total_annotations)
            print("Correct count:", correct_count)
            return redirect('start_test')

        for review_id, user_annotation_value in user_annotations.items():
            try:
                review_id_num = int(review_id.split('_')[1])
                review = Review.objects.get(id=review_id_num)
                if review.ground_truth_annotation == user_annotation_value:
                    correct_count += 1
            except (Review.DoesNotExist, ValueError) as e:
                print("Exception:", e)
                messages.error(request, 'There was an error processing your annotations.', extra_tags='submit_test')
                return redirect('start_test')

        accuracy = (correct_count / total_annotations) * 100
        # Display accuracy or redirect to a results page
        print("Total annotations:", total_annotations)
        print("Correct count:", correct_count)
        return render(request, 'myapp/test_results.html', {'accuracy': accuracy})
    else:
        # Handle case where method is not POST
        print("Total annotations:", total_annotations)
        print("Correct count:", correct_count)
        return redirect('start_test')
    

    


def test_results(request):
    # Passing a default or dummy accuracy value
    dummy_accuracy = 0  # You can change this as needed
    return render(request, 'myapp/test_results.html', {'accuracy': dummy_accuracy})


