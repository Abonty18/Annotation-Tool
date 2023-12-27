import logging
from django.db.models import Q
import sys
from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import StudentForm
from .models import CustomUser
from django.contrib.auth import authenticate, login
from myapp.models import Review
from django.contrib.auth import logout
import json
import random
from django.db.models import Count, Case, When, IntegerField
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
from django.core.paginator import Paginator


from django.db.models import Case, When, Value

def get_prioritized_reviews_for_annotation(user):
    # Fetch reviews that have less than 3 annotations and not annotated by the current user
    return UnannotatedReview.objects.annotate(
        num_annotations=Count('studentannotation')
    ).exclude(
        studentannotation__student1=user
    ).exclude(
        studentannotation__student2=user
    ).exclude(
        studentannotation__student3=user
    ).filter(
        num_annotations__lt=3
    ).order_by('?')  # Random order



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

def sign_out(request):
 logout(request)
 return redirect('index') 

@login_required
def start_annotation(request):
    user = request.user
    unannotated_reviews = get_prioritized_reviews_for_annotation(user)

    paginator = Paginator(unannotated_reviews, 1)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Fetch the current review id
    current_review_id = None
    if page_obj.object_list:
        current_review = page_obj.object_list[0]
        current_review_id = current_review.id

    # Retrieve the selections from the session
    selections = request.session.get('selections', {})
    selected_option = selections.get(str(current_review_id))  # Ensure this is a string key

    return render(request, 'myapp/start_annotation.html', {
        'page_obj': page_obj,
        'selected_option': selected_option
    })




@login_required
def handle_annotation_submission(request):
    if request.method == 'POST':
        student = request.user
        action = request.POST.get('action')
        current_page = int(request.POST.get('current_page', 1))
        selections = request.session.get('selections', {})
        if action == 'save':
            # Logic to save and exit
            current_page = request.POST.get('current_page', 1)
            StudentProject.objects.filter(student=student).update(last_page=current_page)
            messages.success(request, "Your progress has been saved.")
            return redirect('sign_out')  # Redirect to the sign-out page

        # Logic to handle annotations and navigation
        for key, value in request.POST.items():
            if key.startswith('annotation_'):
                review_id = int(key.split('_')[1])
                annotation_value = value
                selections[review_id] = annotation_value
                review = get_object_or_404(UnannotatedReview, id=review_id)

                # Check if the student has already annotated this review
                existing_annotation = StudentAnnotation.objects.filter(
                    review=review,
                    student1=student
                ) | StudentAnnotation.objects.filter(
                    review=review,
                    student2=student
                ) | StudentAnnotation.objects.filter(
                    review=review,
                    student3=student
                )

                if existing_annotation.exists():
                    messages.error(request, f"You have already annotated review {review_id}.")
                    continue

                # Check for an existing annotation object to update
                annotation = StudentAnnotation.objects.filter(review=review).first()

                if not annotation:
                    # Create a new annotation if none exist for this review
                    annotation = StudentAnnotation.objects.create(review=review, student1=student, student1annotation=annotation_value)
                else:
                    # Update an existing annotation with a new student if slots are available
                    if not annotation.student1:
                        annotation.student1 = student
                        annotation.student1annotation = annotation_value
                    elif not annotation.student2:
                        annotation.student2 = student
                        annotation.student2annotation = annotation_value
                    elif not annotation.student3:
                        annotation.student3 = student
                        annotation.student3annotation = annotation_value
                    else:
                        messages.error(request, f"Review {review_id} already has 3 annotations by different students.")
                        continue

                annotation.save()

                # Update annotation count in the UnannotatedReview model
                review.annotation_count = StudentAnnotation.objects.filter(review=review).count()
                review.save()

                messages.success(request, f"Annotation for review {review_id} saved successfully.")
        request.session['selections'] = selections

        # Handling navigation
        if action in ['next', 'previous']:
            current_page = int(request.POST.get('current_page', 1))
            if action == 'next':
            # Store the selection for the current page
              for key, value in request.POST.items():
                if key.startswith('annotation_'):
                    selections[current_page] = (key, value)
              current_page += 1
            elif action == 'previous' and current_page > 1:
              current_page -= 1

        # Save the selections back to the session
            request.session['selections'] = selections
            request.session['last_page'] = current_page  # Save the last page in the session

            return redirect(f"{reverse('start_annotation')}?page={current_page}")

        return redirect('start_annotation')
    else:
        messages.error(request, "You must submit the form with the POST method.")
        return redirect('start_annotation')






def handle_pagination(request, action):
    # Get the current page number from the session or default to 1
    current_page = request.session.get('current_page', 1)

    if action == 'next':
        current_page += 1
    elif action == 'previous' and current_page > 1:
        current_page -= 1

    # Update the current page in the session
    request.session['current_page'] = current_page

    # Redirect back to the annotation view with the updated page number
    return redirect(reverse('start_annotation') + '?page=' + str(current_page))

def become_annotator(request):
    # Clear any existing messages
    storage = messages.get_messages(request)
    storage.used = True

    next_page = request.GET.get('next', 'start_test') 
    email = request.GET.get('email', '')
    form = StudentForm(initial={'email': email})

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            department = form.cleaned_data['department']
            # No need to check if the email exists here, as it's already handled in the form's clean method
            has_taken_course = form.cleaned_data['has_taken_software_course']
            User = get_user_model() 
            user = User.objects.create_user(email=email, password=password, department=department, has_taken_software_course=has_taken_course)
            user.save()

            login(request, user)
            return redirect('start_annotation')
        else:
            # Handle form errors
            for field in form.errors:
                form[field].field.widget.attrs['class'] = 'error'
            # Log the errors for debugging
            print(form.errors)
    else:
        form = StudentForm()

    return render(request, 'myapp/become_annotator.html', {'form': form, 'next': 'start_annotation'})


def index(request):
    # Fetch all projects
    projects = StudentProject.objects.all()
    return render(request, 'myapp/index.html')

def start_test(request):
    # Fetch all reviews from the database
    reviews = Review.objects.all()

    # Get the count of reviews or 10, whichever is smaller
    count = min(reviews.count(), 5)

    # Select random reviews
    random_reviews = random.sample(list(reviews), count)

    return render(request, 'myapp/annotation_test.html', {'reviews': random_reviews})



def create_project(request):
    return render(request, 'create_project.html')


def sign_in(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if CustomUser.objects.filter(email=email).exists():
            request.session['email_for_signin'] = email
            return redirect('enter_password')
        else:
            # Redirect to become-annotator with email as query parameter
            # messages.info(request, "You are not a listed annotator for this project. Please signup first to become an annotator.")
            return redirect(f"{reverse('become_annotator')}?email={email}")

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

