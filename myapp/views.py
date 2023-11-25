from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import StudentForm
from .models import Student
from django.contrib.auth import authenticate, login
from myapp.models import Review
import json
import random
from django.contrib.auth.models import User
from .models import Student
from .forms import StudentForm
import os
from django.conf import settings

def become_annotator(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if the email already exists as a username
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Email already exists. Please sign in.')
                return redirect('sign_in')  # Redirect to the sign-in page

            # Create a User instance
            user = User.objects.create_user(
                username=email, 
                email=email, 
                password=form.cleaned_data['password']
            )

            # Now create a Student instance
            Student.objects.create(
                user=user,
                department=form.cleaned_data['department'],
                program=form.cleaned_data['program'],
                graduation_year=form.cleaned_data['graduation_year']
            )

            # Redirect to the test or another appropriate page
            return redirect('start_test') 

    else:
        form = StudentForm()

    return render(request, 'myapp/become_annotator.html', {'form': form})



def index(request):
    return render(request, 'myapp/index.html')
# myapp/views.py

def start_test(request):
    # Construct the absolute file path to the JSON file
    file_path = os.path.join(settings.BASE_DIR, 'myapp', 'reviews.json')

    # Load reviews from JSON file
    with open(file_path, 'r') as file:
        reviews = json.load(file)

    # Select 20 random reviews
    random_reviews = random.sample(reviews, 20)

    return render(request, 'myapp/annotation_test.html', {'reviews': random_reviews})




def create_project(request):
    # Your logic for creating a project
    return render(request, 'create_project.html')
def sign_in(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the test or some other page
            return redirect('start_test')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'myapp/sign_in.html')

# def become_annotator(request):
#     if request.method == 'POST':
#         form = StudentForm(request.POST)
#         if form.is_valid():
#             # Check if the email already exists
#             if Student.objects.filter(email=form.cleaned_data['email']).exists():
#                 messages.error(request, 'Email already exists. Please sign in.')
#                 return redirect('sign_in')  # Redirect to the sign-in page
#             else:
#                 student = form.save()  # Save the new student

#                 # Log in the new student (user)
#                 login(request, student)  # Adjust as per your user model and authentication setup

#                 # Redirect to the start_test view
#                 return redirect(reverse('start_test'))
#     else:
#         form = StudentForm()

#     return render(request, 'myapp/become_annotator.html', {'form': form})

def submit_test(request):
    if request.method == 'POST':
        user_annotations = {key: int(value) for key, value in request.POST.items() if key.startswith('annotation_')}
        correct_count = 0
        total_annotations = len(user_annotations)

        if total_annotations == 0:
            messages.error(request, 'No annotations were submitted.')
            return redirect('start_test')

        for review_id, annotation in user_annotations.items():
            try:
                review_id_num = int(review_id.split('_')[1])
                review = Review.objects.get(id=review_id_num)
                if review.ground_truth_annotation == annotation:
                    correct_count += 1
            except (Review.DoesNotExist, ValueError):
                messages.error(request, 'There was an error processing your annotations.')
                return redirect('start_test')  # Or handle error differently

        accuracy = correct_count / total_annotations
        # Display accuracy or redirect to a results page
        messages.success(request, f'Your annotation accuracy: {accuracy:.2%}')
        return render(request, 'myapp/test_results.html', {'accuracy': accuracy})



