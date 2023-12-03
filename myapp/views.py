from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import StudentForm
from .models import CustomUser
from django.contrib.auth import authenticate, login
from myapp.models import Review
import json
import random
from django.db.models import Count
from django.contrib.auth import get_user_model  # Import the user model
from django.contrib.auth.models import User
from .models import StudentProject
from .forms import StudentForm
import os
from django.conf import settings
from .models import Review
from django.core.paginator import Paginator
from .models import StudentAnnotation, UnannotatedReview
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_reviews_for_annotation():
    # Get reviews with less than 3 annotations, excluding those with an annotation count of 3
    return UnannotatedReview.objects.annotate(
        annotation_count=Count('studentannotation')
    ).filter(
        annotation_count__lt=3
    ).exclude(
        annotation_count=3  # Exclude reviews with an annotation count of 3
    ).order_by('annotation_count')


def get_labels_for_review(review_id):
    annotations = StudentAnnotation.objects.filter(review_id=review_id)
    if annotations.count() == 3:
        return [annotation.label for annotation in annotations]
    return None

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
    user = request.user
    page_number = request.GET.get('page', 1)
    unannotated_reviews = UnannotatedReview.objects.annotate(
        annotation_count_annotation=Count('studentannotation')
    ).filter(
        annotation_count_annotation__lt=3
    ).exclude(
        annotation_count_annotation=3
    ).order_by('annotation_count_annotation')
    print("Number of reviews fetched: ", unannotated_reviews.count())
    for review in unannotated_reviews:
        print("Review ID:", review.id, "Annotation Count:", review.annotation_count)

    # Randomize the order of reviews
    unannotated_reviews = sorted(unannotated_reviews, key=lambda x: random.random())

    paginator = Paginator(unannotated_reviews, 10)
    page_obj = paginator.get_page(page_number)

    # Add information about the students who have annotated each review
    for review in page_obj:
        review.student_annotations = review.studentannotation_set.all()

    return render(request, 'myapp/start_annotation.html', {'page_obj': page_obj})


def handle_annotation_submission(request):
    if request.method == 'POST':
        # Get the student making the annotation
        student = request.user  # Assuming you have a user system in place

        # Iterate through the POST data to process annotations
        for key, value in request.POST.items():
            if key.startswith('annotation_'):
                review_id = int(key.split('_')[1])  # Extract the review ID
                label = int(value)  # Extract the selected label

                # Get or create the StudentAnnotation object
                annotation, created = StudentAnnotation.objects.get_or_create(
                    student=student,
                    review_id=review_id,
                    defaults={'label': label}
                )

                # Update the label if the annotation already exists
                if not created:
                    annotation.label = label
                    annotation.save()

                # Increment annotation count
                unannotated_review = UnannotatedReview.objects.get(id=review_id)
                unannotated_review.annotation_count += 1
                unannotated_review.save()

                # Logic for preventing display if annotation count is 3
                # Note: This logic depends on how you choose to implement the restriction.
                # For instance, you might skip such reviews in your query when fetching reviews for annotation.

        # Redirect to a success page or the next set of reviews
        return redirect('start_annotation')

    # Handle other cases like GET requests or invalid form submissions
    return render(request, 'start_annotation.html')  # Replace with your template name
  # Replace 'annotation_page.html' with your template name



def become_annotator(request):
    # Clear any existing messages
    storage = messages.get_messages(request)
    storage.used = True

    # Capture 'next' parameter from the request
    next_page = request.GET.get('next', 'start_test')  # default to 'start_annotation' if 'next' is not provided

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']  # Get the password from the form data

            # Check if the email already exists in the Student model
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Student with this Email already exists. Please sign in.')
                return redirect('sign_in')  # Redirect to the sign-in page

            # Create a new user with the custom user manager's create_user method
            User = get_user_model()  # Get the custom user model
            user = User.objects.create_user(email=email, password=password)

            # Log in the user after registration
            login(request, user)

            # Redirect to the next page after registration
            return redirect(next_page)
    else:
        form = StudentForm()

    return render(request, 'myapp/become_annotator.html', {'form': form, 'next': next_page})

def index(request):
    # Fetch all projects
    projects = StudentProject.objects.all()
    return render(request, 'myapp/index.html')

def start_test(request):
    # Fetch all reviews from the database
    reviews = Review.objects.all()

    # Get the count of reviews or 10, whichever is smaller
    count = min(reviews.count(), 15)

    # Select random reviews
    random_reviews = random.sample(list(reviews), count)

    return render(request, 'myapp/annotation_test.html', {'reviews': random_reviews})



def create_project(request):
    return render(request, 'create_project.html')

def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email exists in the database
        if CustomUser.objects.filter(email=email).exists():
            # Store email in session and redirect to password page
            request.session['email_for_signin'] = email
            return redirect('enter_password')
        else:
            # Email does not exist, show message to become an annotator
            messages.info(request, "You are not a listed annotator for this project. Please choose Next to become an annotator.")
            return redirect('become_annotator')

    return render(request, 'myapp/sign_in.html')
def enter_password(request):
    if request.method == 'POST':
        email = request.session.get('email_for_signin')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('start_annotation')
        else:
            messages.error(request, 'Invalid password. Please try again.')

    return render(request, 'myapp/enter_password.html')


def submit_test(request):
    total_annotations = 0  # Initialize total_annotations
    correct_count = 0  # Initialize correct_count

    if request.method == 'POST':
        user_annotations = {key: int(value) for key, value in request.POST.items() if key.startswith('annotation_')}
        total_annotations = len(user_annotations)  # Update total_annotations

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


