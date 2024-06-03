import logging
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.urls import reverse
from .models import move_annotated_reviews
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import os
import joblib
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import StudentProject
from django.conf import settings
from django.db.models import F, Q
import sys
from django.db import transaction
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
from .forms import AppReviewForm
from django.db.models import Case, When, Value
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from myapp.models import UnannotatedReview
from .models import Annotation
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import UnannotatedReview, ReviewLock
from django.utils import timezone
import datetime
from .forms import ProjectForm

@login_required
def get_review_to_annotate(request):
    user = request.user

    # Release expired locks
    ReviewLock.objects.filter(is_locked=True, lock_time__lte=timezone.now() - datetime.timedelta(minutes=5)).update(is_locked=False)

    # Try to find an unlocked review that is not fully annotated and prioritize by annotation count
    review = UnannotatedReview.objects.exclude(
        locks__is_locked=True
    ).exclude(
        studentannotation__in=StudentAnnotation.objects.filter(
            Q(student1=user) | Q(student2=user) | Q(student3=user)
        )
    ).filter(
        annotation_count__lt=3
    ).order_by(
        'annotation_count', 'id'
    ).first()

    if review:
        # Lock this review for the current user
        ReviewLock.objects.create(review=review, user=user, is_locked=True)
        return review
    else:
        # No reviews are available for annotation
        return None


@login_required
# def start_annotation(request):
#     user = request.user
#     review = get_review_to_annotate(request)  # Make sure this function is correctly implemented

#     if not review:
#         messages.info(request, "No reviews are currently available for annotation.")
#         return render(request, 'index.html')

#     reviews_list = [review] if review else []
#     paginator = Paginator(reviews_list, 1)
#     page_obj = paginator.get_page(1)

#     selections = request.session.get('selections', {})
#     selected_option = selections.get(str(review.id)) if review else None

#     annotation_count = get_user_annotation_count(user)

#     return render(request, 'myapp/start_annotation.html', {
#         'page_obj': page_obj,
#         'selected_option': selected_option,
#         'annotation_count': annotation_count,
#     })
#prev one
# def start_annotation(request):
#     user = request.user
#     projects = StudentProject.objects.filter(student=user)
#     if projects.exists():
#         # Render a template to display existing projects and provide an option to continue with one
#         return render(request, 'myapp/existing_projects.html', {'projects': projects})
#     else:
#         # If no projects exist, proceed with the regular annotation process
#         review = get_review_to_annotate(request)
#         if not review:
#             messages.info(request, "No reviews are currently available for annotation.")
#             return render(request, 'index.html')

#         reviews_list = [review] if review else []
#         paginator = Paginator(reviews_list, 1)
#         page_obj = paginator.get_page(1)

#         selections = request.session.get('selections', {})
#         selected_option = selections.get(str(review.id)) if review else None

#         annotation_count = get_user_annotation_count(user)

#         return render(request, 'myapp/start_annotation.html', {
#             'page_obj': page_obj,
#             'selected_option': selected_option,
#             'annotation_count': annotation_count,
#         })
#new one
@login_required
def start_annotation(request, unique_link=None):
    user = request.user
    if unique_link:
        project = get_object_or_404(StudentProject, unique_link=unique_link)
    else:
        project = None

    if project:
        review = get_review_to_annotate(request)
        if not review:
            messages.info(request, "No reviews are currently available for annotation.")
            return render(request, 'index.html')

        reviews_list = [review] if review else []
        paginator = Paginator(reviews_list, 1)
        page_obj = paginator.get_page(1)

        selections = request.session.get('selections', {})
        selected_option = selections.get(str(review.id)) if review else None

        annotation_count = get_user_annotation_count(user)

        return render(request, 'myapp/start_annotation.html', {
            'page_obj': page_obj,
            'selected_option': selected_option,
            'annotation_count': annotation_count,
            'project': project,
        })
    else:
        projects = StudentProject.objects.filter(student=user)
        if projects.exists():
            return render(request, 'myapp/existing_projects.html', {'projects': projects})
        else:
            messages.info(request, "No projects available.")
            return render(request, 'index.html')




    
# from django.shortcuts import get_object_or_404
# from .models import StudentAnnotation, ReviewLock, UnannotatedReview
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect

def submit_annotation(request):
    if request.method == "POST":
        review_id = request.POST.get('review_id')
        user = request.user
        annotation_value = request.POST.get(f'annotation_{review_id}')
        
        if annotation_value:
            review = get_object_or_404(UnannotatedReview, id=review_id)
            annotation, created = StudentAnnotation.objects.get_or_create(
                review=review,
                defaults={"student1": user, "student1annotation": annotation_value}
            )
            
            if not created:
                # If the annotation was not created, it means it already exists.
                # Update the existing annotation with the new value for the correct student.
                if annotation.student2 is None:
                    annotation.student2 = user
                    annotation.student2annotation = annotation_value
                elif annotation.student3 is None:
                    annotation.student3 = user
                    annotation.student3annotation = annotation_value
                else:
                    # All annotation slots are filled. Handle this case appropriately.
                    messages.error(request, "This review has already been fully annotated.")
                    return redirect('start_annotation')
                
                annotation.save()

            # After saving the annotation, update the annotation count for the review.
            update_annotation_count(review_id)
            
            # Release the lock on the review if you're using review locks.
            ReviewLock.objects.filter(review_id=review_id, user=user).update(is_locked=False)
            
            # Redirect to get the next review for annotation.
            messages.success(request, "Your annotation has been saved.")
            return redirect('start_annotation')
        else:
            messages.error(request, "You must select an annotation value.")
            return redirect('start_annotation')
    else:
        # If it's not a POST request, handle accordingly.
        return redirect('start_annotation')

def update_annotation_count(review_id):
    review = get_object_or_404(UnannotatedReview, id=review_id)
    annotations = StudentAnnotation.objects.filter(review=review)
    total_annotations = 0

    for annotation in annotations:
        if annotation.student1annotation is not None:
            total_annotations += 1
        if annotation.student2annotation is not None:
            total_annotations += 1
        if annotation.student3annotation is not None:
            total_annotations += 1

    review.annotation_count = total_annotations
    review.is_fully_annotated = total_annotations >= 3  # Assuming 3 is the max number of annotations
    review.save()

    
def check_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if CustomUser.objects.filter(email=email).exists():
            # Redirect to enter_password page with email in session
            request.session['email_for_signin'] = email
            return redirect('enter_password')
        else:
            # Redirect to signup page with email as query parameter
            return redirect(f"{reverse('become_annotator')}?email={email}")
    return redirect('index')



def get_prioritized_reviews_for_annotation(user):
    # Fetch reviews that have less than 3 annotations and not annotated by the current user
    return UnannotatedReview.objects.annotate(
        num_annotations=Count('studentannotation', distinct=True)
    ).exclude(
        studentannotation__in=StudentAnnotation.objects.filter(
            Q(student1=user) | Q(student2=user) | Q(student3=user)
        )
    ).filter(
        annotation_count__lt=3
    ).order_by('num_annotations')




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



def update_annotation_count(review_id):
    review = UnannotatedReview.objects.get(id=review_id)
    # Recalculate the total annotations for the review
    total_annotations = StudentAnnotation.objects.filter(review=review).count()
    # Update the review's annotation count
    review.annotation_count = total_annotations
    review.save()



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
def get_user_annotation_count(user):
    return StudentAnnotation.objects.filter(
        Q(student1=user) | Q(student2=user) | Q(student3=user)
    ).distinct().count()




# @login_required
# def start_annotation(request):
#     user = request.user

#     # Get a review that matches the criteria and is not already locked
#     review = get_review_to_annotate(user)
#     if not review:
#         # If no reviews are available, inform the user
#         messages.info(request, "No reviews are currently available for annotation.")
#         return render(request, 'index.html')

#     # Since we have a single review, we can construct a one-item list for pagination
#     reviews_list = [review]
#     paginator = Paginator(reviews_list, 1)  # We are showing one review per page

#     # Since we have only one review, we are on the first page
#     page_number = 1
#     page_obj = paginator.get_page(page_number)

#     # Prepare the selections for the current review
#     selections = request.session.get('selections', {})
#     selected_option = selections.get(str(review.id))

#     # Set the current annotation page in the session
#     request.session['current_annotation_page'] = page_number

#     return render(request, 'myapp/start_annotation.html', {
#         'page_obj': page_obj,
#         'selected_option': selected_option,
#         'annotation_count': get_user_annotation_count(user),
#     })


@login_required
def handle_annotation_submission(request):
    if request.method == 'POST':
        user = request.user
        action = request.POST.get('action')
        current_page = int(request.POST.get('current_page', 1))
        selections = request.session.get('selections', {})
        if action == 'next':
            # Attempt to fetch the next review for annotation
            next_review = get_review_to_annotate(request)
            if next_review:
                # If there is a next review, redirect to the annotation view for the next review
                return HttpResponseRedirect(reverse('start_annotation'))
            else:
                # If no more reviews are available, redirect to a completion page or back to the main page
                messages.info(request, "You have completed all available annotations.")
                return redirect('index')
        elif action == 'save':
            StudentProject.objects.filter(student=user).update(last_page=current_page)
            messages.success(request, "Your progress has been saved.")
            return redirect('sign_out')

        # Logic to handle annotations
        for key, value in request.POST.items():
            if key.startswith('annotation_'):
                review_id = int(key.split('_')[1])
                annotation_value = int(value)

                # Check if the review is already fully annotated
                try:
                    review = UnannotatedReview.objects.get(id=review_id)
                    if review.is_fully_annotated:
                        messages.error(request, "This review is already fully annotated.")
                        continue
                except UnannotatedReview.DoesNotExist:
                    messages.error(request, "This review does not exist.")
                    continue

                # Assign annotation and update review
                with transaction.atomic():
                    annotation, created = StudentAnnotation.objects.get_or_create(
                        review=review,
                        defaults={
                            'student1': user,
                            'student1annotation': annotation_value
                        }
                    )
                    
                    if not created:
                        if annotation.student2 is None:
                            annotation.student2 = user
                            annotation.student2annotation = annotation_value
                        elif annotation.student3 is None:
                            annotation.student3 = user
                            annotation.student3annotation = annotation_value
                        else:
                            messages.error(request, "No available slots for annotation.")
                            continue  # This should not happen as we check annotation_count before

                        annotation.save()

                    # Update review's annotation count and fully annotated status
                    review.save()  # This triggers the save method in the model which updates the count and status
                print(f"Review {review_id} annotation count after submission: {review.annotation_count}")

        request.session['selections'] = selections

        # Handling navigation
        if action in ['next', 'previous']:
            if action == 'next':
                current_page += 1
            elif action == 'previous' and current_page > 1:
                current_page -= 1
            request.session['current_annotation_page'] = current_page

            return redirect(f"{reverse('start_annotation')}?page={current_page}")

        return redirect('start_annotation')
    else:
        messages.error(request, "You must submit the form with the POST method.")
        return redirect('start_annotation')

    
# def update_annotation_count(review):
#     # Retrieve the current annotations for this review atomically to avoid race conditions
#     with transaction.atomic():
#         current_count = StudentAnnotation.objects.filter(review=review).count()
#         review.annotation_count = current_count
#         review.save()


def create_annotation(user, review_id):
    # Ensure you're handling duplicates and concurrency issues as per your application's requirements
    with transaction.atomic():
        review = get_object_or_404(UnannotatedReview, id=review_id)
        annotation, created = StudentAnnotation.objects.get_or_create(
            review=review,
            student1=user  # Adjust according to your logic for assigning students
        )
        if created:
            # If a new annotation is created, update the annotation count for the review
            update_annotation_count(review_id)


# def delete_annotation(user, review):
#     # Delete the user's annotation for the review
#     StudentAnnotation.objects.filter(review=review, student1=user).delete()
#     # Update the annotation_count for the review
#     update_annotation_count(review.id)

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

    next_page = request.GET.get('next', 'start_annotation') 
    email = request.GET.get('email', '')
    show_email_field = not bool(email)  # Show email field only if email is not provided

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if not show_email_field:
            # Manually set the email data if the field is hidden
            form.data = form.data.copy()
            form.data['email'] = email
        
        if form.is_valid():
            # Create the user
            User = get_user_model()
            user = User.objects.create_user(
                email=form.cleaned_data.get('email', email),
                password=form.cleaned_data['password'],
                department=form.cleaned_data['department'],
                age=form.cleaned_data.get('age'),  # Get optional age
                working_experience=form.cleaned_data.get('working_experience'),  # Get working experience
                software_related_courses=form.cleaned_data.get('software_related_courses', [])  # Get selected courses
            )
            user.save()

            # Log the user in and redirect to the next page
            login(request, user)
            return redirect(next_page)
        else:
            # If the form is invalid and the email field is not shown, add it back as a hidden field
            if not show_email_field:
                form.initial['email'] = email
            for field in form.errors:
                form[field].field.widget.attrs['class'] = 'error'
    else:
        # Display the form for a GET request
        
        form = StudentForm(initial={'email': email}, show_email_field=show_email_field)

    return render(request, 'myapp/become_annotator.html', {
        'form': form,
        'show_email_field': show_email_field,
        'email': email,  # Add this line
        # ... other context variables ...
    })


def index(request):
    if request.method == 'POST':
        if 'continue_project' in request.POST:
            # Redirect to the unannotated reviews page
            return redirect('start_annotation')
        elif 'create_project' in request.POST:
            # Redirect to the create project page
            return redirect('create_project')
    return render(request, 'myapp/index.html')


def start_test(request):
    # Fetch all reviews from the database
    reviews = Review.objects.all()

    # Get the count of reviews or 10, whichever is smaller
    count = min(reviews.count(), 5)

    # Select random reviews
    random_reviews = random.sample(list(reviews), count)

    return render(request, 'myapp/annotation_test.html', {'reviews': random_reviews})

# def create_project(request):
#     return render(request, 'create_project.html')


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
    email = request.session.get('email_for_signin')
    if not email:
        return redirect('index')  # Redirect to index if no email in session

    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('start_annotation')
        else:
            messages.error(request, 'Invalid password. Please try again.')

    return render(request, 'myapp/enter_password.html', {'email': email})



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

    
def review_classification(request):
    # Here you might set up context data to pass to the template
    context = {
        # 'reviews': get_reviews_from_database_or_service(),
    }
    return render(request, 'myapp/review_page.html', context)

def app_review_form(request):
    if request.method == "POST":
        form = AppReviewForm(request.POST)
        if form.is_valid():
            # Here you would normally process the form data

            # Redirect to the review classification page
            return redirect('review_classification')  # Ensure you have a URL named 'review_classification'
    else:
        form = AppReviewForm()
    return render(request, 'myapp/app_review_form.html', {'form': form})



def test_results(request):
    # Passing a default or dummy accuracy value
    dummy_accuracy = 0  # You can change this as needed
    return render(request, 'myapp/test_results.html', {'accuracy': dummy_accuracy})



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProjectForm  # Import your project creation form

# def create_project(request):
#     if request.method == 'POST':
#         form = ProjectForm(request.POST)
#         if form.is_valid():
#             # Save the form data to create a new StudentProject instance
#             form.save()
#             # Optionally, you can redirect the user to a success page or another URL
#             return redirect('success_url_name')
#     else:
#         form = ProjectForm()

#     return render(request, 'myapp/create_project.html', {'form': form})


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            student_project = form.save(commit=False)
            student_project.student = request.user
            student_project.save()
            return redirect('invite_annotators', project_id=student_project.id)
        else:
            print(form.errors)
    else:
        form = ProjectForm()

    return render(request, 'myapp/create_project.html', {'form': form})



# from django.shortcuts import render, get_object_or_404
# from django.core.mail import send_mail
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import StudentProject
# from django.urls import reverse

@login_required
def invite_annotators(request, project_id):
    project = get_object_or_404(StudentProject, id=project_id, student=request.user)
    project_link = request.build_absolute_uri(reverse('start_annotation', args=[project.unique_link]))

    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Send an email invitation
            send_mail(
                'You are invited to annotate a project',
                f'Click the link to annotate the project: {project_link}',
                'labibafarah2998@gmail.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, f'Invitation sent to {email}')
        else:
            messages.error(request, 'Please provide an email address')

    return render(request, 'myapp/invite_annotators.html', {'project': project, 'project_link': project_link})



@login_required
def project_list(request):
    projects = StudentProject.objects.all()
    desired_labels = [
        'privacy related bug detection',
        'privacy related feature request detection',
        'privacy related bug+feature request detection',
        'not privacy related review'
    ]
    for project in projects:
        project_labels = [label.strip().lower() for label in project.labels.split(',')]
        project.can_train = all(label in desired_labels for label in project_labels)

    return render(request, 'myapp/project_list.html', {'projects': projects})


import os
import io
import joblib
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.files.base import ContentFile
import logging
from .models import StudentProject  # Ensure your models are imported

logger = logging.getLogger(__name__)

import chardet

@login_required
@csrf_exempt
def train_dataset(request, project_id):
    project = get_object_or_404(StudentProject, id=project_id)

    # Load the dataset and models
    file_path = project.uploaded_file.path
    review_column_index = int(project.review_column)  # Convert the column number to integer

    df = None
    # Ensure the file is a CSV
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension != '.csv':
        return JsonResponse({'status': 'error', 'message': 'Uploaded file is not a CSV.'})

    # Detect encoding with chardet
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    if not encoding:
        return JsonResponse({'status': 'error', 'message': 'Failed to detect encoding of the file.'})

    delimiters = [',', ';', '\t', '|']
    file_content = raw_data.decode(encoding)

    for delimiter in delimiters:
        try:
            df = pd.read_csv(io.StringIO(file_content), delimiter=delimiter)
            # Check if the specified column index is within the range
            if review_column_index < len(df.columns):
                review_column_name = df.columns[review_column_index]
                logger.info(f"Successfully read the file with detected encoding={encoding} and delimiter={delimiter}")
                break
        except (pd.errors.ParserError, ValueError, IndexError) as e:
            logger.error(f"Failed to read file with detected encoding={encoding} and delimiter={delimiter}: {e}")
            continue

    if df is None or review_column_index >= len(df.columns):
        return JsonResponse({'status': 'error', 'message': f'Failed to read the uploaded file with supported encodings and delimiters. Invalid column index: {review_column_index}.'})

    # Load the models from the model_files directory
    model_path = settings.MODEL_FILES_DIR
    tfidf_vectorizer = joblib.load(os.path.join(model_path, 'tfidf_vectorizer.pkl'))
    scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
    best_logreg_model = joblib.load(os.path.join(model_path, 'best_logreg_model.pkl'))
    label_encoder = joblib.load(os.path.join(model_path, 'label_encoder.pkl'))

    # Preprocess the data
    reviews = df[review_column_name].astype(str)
    tfidf_reviews = tfidf_vectorizer.transform(reviews)
    scaled_reviews = scaler.transform(tfidf_reviews.toarray())

    # Predict the labels
    predicted_labels = best_logreg_model.predict(scaled_reviews)
    predicted_labels = label_encoder.inverse_transform(predicted_labels)

    # Add the labels to the DataFrame
    df['Predicted_Labels'] = predicted_labels

    # Save the labeled dataset to a CSV file
    labeled_file_name = f'labeled_{project.uploaded_file.name}'
    labeled_file_path = os.path.join(settings.MEDIA_ROOT, 'labeled_files', labeled_file_name)
    df.to_csv(labeled_file_path, index=False)

    # Save the labeled file path in the project model
    project.labeled_file.save(labeled_file_name, ContentFile(open(labeled_file_path, 'rb').read()))
    project.save()

    return JsonResponse({'status': 'success', 'message': 'Dataset has been labeled and is ready for download.'})

@login_required
def download_labeled_file(request, project_id):
    project = get_object_or_404(StudentProject, id=project_id)
    if not project.labeled_file:
        return JsonResponse({'status': 'error', 'message': 'No labeled file available for this project.'})

    response = HttpResponse(project.labeled_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{project.labeled_file.name}"'
    return response


import os
import joblib
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@csrf_exempt
def classify_reviews(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        review_column_index = int(request.POST.get('review_column', 0)) - 1  # Adjust for zero-based indexing

        if not uploaded_file:
            return JsonResponse({'status': 'error', 'message': 'No file uploaded.'})

        # Try reading the file with multiple encodings and delimiters
        encodings = ['utf-8', 'utf-16', 'windows-1252', 'iso-8859-1']
        delimiters = [',', ';', '\t', '|']
        df = None
        errors = []

        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    uploaded_file.seek(0)  # Reset file pointer to the beginning
                    df = pd.read_csv(uploaded_file, encoding=encoding, delimiter=delimiter)
                    logger.debug(f"Successfully read file with encoding={encoding} and delimiter={delimiter}")
                    break
                except UnicodeDecodeError as e:
                    error_message = f"UnicodeDecodeError with encoding={encoding} and delimiter={delimiter}: {e}"
                    errors.append(error_message)
                    logger.error(error_message)
                except pd.errors.EmptyDataError as e:
                    error_message = f"EmptyDataError with encoding={encoding} and delimiter={delimiter}: {e}"
                    errors.append(error_message)
                    logger.error(error_message)
                except pd.errors.ParserError as e:
                    error_message = f"ParserError with encoding={encoding} and delimiter={delimiter}: {e}"
                    errors.append(error_message)
                    logger.error(error_message)
            if df is not None:
                break

        if df is None:
            return JsonResponse({'status': 'error', 'message': 'Failed to read the uploaded file with supported encodings and delimiters.', 'errors': errors})

        # Ensure the review column index is valid
        if review_column_index >= len(df.columns) or review_column_index < 0:
            return JsonResponse({'status': 'error', 'message': 'Invalid review column index.'})

        # Extract the review content based on the column index
        review_content = df.iloc[:, review_column_index]

        # Load the models from the model_files directory
        model_path = settings.MODEL_FILES_DIR
        tfidf_vectorizer = joblib.load(os.path.join(model_path, 'tfidf_vectorizer.pkl'))
        scaler = joblib.load(os.path.join(model_path, 'scaler.pkl'))
        best_logreg_model = joblib.load(os.path.join(model_path, 'best_logreg_model.pkl'))
        label_encoder = joblib.load(os.path.join(model_path, 'label_encoder.pkl'))

        # Preprocess the data
        reviews = review_content.astype(str)
        tfidf_reviews = tfidf_vectorizer.transform(reviews)
        scaled_reviews = scaler.transform(tfidf_reviews.toarray())

        # Predict the labels
        predicted_labels = best_logreg_model.predict(scaled_reviews)
        predicted_labels = label_encoder.inverse_transform(predicted_labels)

        # Add the labels to the DataFrame
        df['predicted_labels'] = predicted_labels

        # Ensure the 'labeled_files' directory exists
        labeled_file_dir = os.path.join(settings.MEDIA_ROOT, 'labeled_files')
        if not os.path.exists(labeled_file_dir):
            os.makedirs(labeled_file_dir)

        # Save the labeled DataFrame to a CSV file
        labeled_file_name = 'labeled_reviews.csv'
        labeled_file_path = os.path.join(labeled_file_dir, labeled_file_name)
        df.to_csv(labeled_file_path, index=False)

        # Prepare the file for download
        with open(labeled_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename={labeled_file_name}'
            return response

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
