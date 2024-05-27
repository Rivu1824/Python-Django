from django.urls import path
from .views import *


urlpatterns = [

    path('', HomePageView.as_view(), name='home'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),
    path('about/', AboutView.as_view(), name='about'),
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('course/<slug:slug>/', CourseDetailView.as_view(), name='course-detail'),
    path('enroll/<int:course_id>/', EnrollmentCreateView.as_view(), name='create_enroll'),
    path('transaction/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('create_transaction/<int:course_id>/', TransactionCreateView.as_view(), name='create_transaction'),
    path('instructors/', AllInstructorsView.as_view(), name='all-instructors'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('instructor/<int:pk>/', InstructorDetailView.as_view(), name='instructor-detail'),
    path('categories/', CategorieListView.as_view(), name='categorie_list'),
    path('categorie/<slug:slug>/', CategorieDetailView.as_view(), name='categorie_detail'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
    path('payment-failure/', PaymentFailureView.as_view(), name='payment_failure'),
    path('payment-success/', PaymentsuccessView.as_view(), name='payment_success'),
    path('privacy-policy/', Privacy_PolicyView.as_view(), name='privacy_policy'),
    path('govt-job-preparation/', Govt_Job_PreparationView.as_view(), name='govt_job_preparation'),
    path('university-admission-preparation/', University_Admission_PreparationView.as_view(), name='university_admission_preparation'),
    path('refunds-returns/', Refunds_ReturnsView.as_view(), name='refunds_returns'),
    path('terms-condition/', TermsConditionView.as_view(), name='terms_condition'),



    ]