from django.views.generic import *
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView as AuthLoginView
from django.core.mail import send_mail
from django.conf import settings
from .models import *
from .forms import *
from django.views import generic
from django.views.decorators.cache import never_cache
from .mixins import*

@method_decorator(never_cache, name='dispatch')
class Login(LogoutRequiredMixin, generic.View):
    def get(self, *args, **kwargs):
        form = LoginForm()
        context = {
            "form": form
        }
        return render(self.request, 'login.html', context)

    def post(self, *args, **kwargs):
        form = LoginForm(self.request.POST)

        if form.is_valid():
            user = authenticate(
                self.request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(self.request, user)
                return redirect('home')

            else:
                messages.warning(self.request, "Wrong credentials")
                return redirect('login')

        return render(self.request, 'login.html', {"form": form})


class Logout(generic.View):
    def get(self, *args, **kwargs):
        logout(self.request)
        return redirect('login')


class RegisterView(View):
    template_name = 'registration.html'

    def get(self, request, *args, **kwargs):
        form = UserRegistrationForm()
        categories = Categorie.objects.all()

        logo = Logo.objects.first()
        banners = Banner.objects.all()


        return render(request, self.template_name, {
            'form': form,
            'categories': categories,
            'logo': logo,
            'banners': banners,

        })

    def post(self, request, *args, **kwargs):
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            # Create user
            user = form.save()

            # Log in the user
            authenticated_user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            login(request, authenticated_user)

            # Send welcome email

            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Registration failed. Please check the form.')
            return render(request, self.template_name, {'form': form})




@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    template_name = 'user-details.html' 

    def get(self, request, *args, **kwargs):
        user = request.user
        enrollments = Enrollment.objects.filter(user=user)

        logo = Logo.objects.first() 
        
        context = {
            'user': user,
            'enrollments': enrollments,
            'logo': logo,
        }
        return render(request, self.template_name, context)



class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categorie.objects.all()
        context['banners'] = Banner.objects.all()
        context['about_enrolled'] = About_Enrolled.objects.first()
        context['faq_banners'] = FAQBanner.objects.all()
        context['logo'] = Logo.objects.first()
        context['instructors'] = Instructor.objects.all()
        context['courses'] = Course.objects.all()
        context['about_enrolled_points'] = About_Enrolled_point.objects.all()
        context['faq_banner_points'] = FAQBanner_point.objects.all()
        context['short_bar'] = short_Bar.objects.first()

        if context['about_enrolled']:
            about_enrolled_instance = context['about_enrolled']
            context['about_enrolled_title'] = about_enrolled_instance.title
            context['about_enrolled_description'] = about_enrolled_instance.description
            context['about_enrolled_image'] = about_enrolled_instance.image
            context['about_enrolled_students_image'] = about_enrolled_instance.Enrolled_Students
            context['about_enrolled_video_url'] = about_enrolled_instance.video_file.url

        return context

class CourseListView(ListView):
    model = Course
    template_name = 'courses.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        return Course.objects.select_related('instructor').all().order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logo'] = Logo.objects.first()
        context['categories'] = Categorie.objects.all()

        return context



class CourseDetailView(LoginRequiredMixin, View):
    template_name = 'course-details.html'
    login_url = reverse_lazy('login')

    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        instructor = Instructor.objects.filter(course=course).first()
        lessons = Lesson.objects.filter(course=course)
        for lesson in lessons:
            lesson.videos = Video.objects.filter(lesson=lesson)


        categories = [course.categories]  

        course_points = course_point.objects.filter(course=course)

        user_enrolled = Enrollment.objects.filter(course=course, user=request.user).exists()

        logo = Logo.objects.first()
        context = {
            'course': course,
            'instructor': instructor,
            'lessons': lessons,
            'categories': categories,
            'logo': logo,
            'course_points': course_points,
            'user_enrolled': user_enrolled,  
        }

        return render(request, self.template_name, context)



    

class EnrollmentCreateView(LoginRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'enroll.html'

    def form_valid(self, form):
        course_id = self.kwargs['course_id']
        enrolled_course = get_object_or_404(Course, id=course_id)

        if Enrollment.objects.filter(course_id=course_id, user=self.request.user).exists():
            messages.warning(self.request, 'You are already enrolled in this course.')
            return redirect('course-detail', slug=enrolled_course.slug)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_id = self.kwargs['course_id']
        enrolled_course = get_object_or_404(Course, id=course_id)

        context['enrolled_course'] = enrolled_course
        context['categorie_data'] = Categorie.objects.all()  
        context['logo'] = Logo.objects.first() 

        return context

class TransactionCreateView(View):
    template_name = 'transaction.html'
    success_url = reverse_lazy('transaction_detail')

    def get(self, request, course_id):
       enrolled_course = get_object_or_404(Course, id=course_id)
       form = TransactionForm()
       logo = Logo.objects.first()

       total_amount = enrolled_course.calculate_discounted_price()

       context = {
          'form': form,
          'logo': logo,
          'enrolled_course': enrolled_course,
          'total_amount': total_amount,
    }

       return render(request, self.template_name, context)


    def post(self, request, course_id):
        form = TransactionForm(request.POST)

        if form.is_valid():
            user = self.request.user
            course = get_object_or_404(Course, id=course_id)

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            mobile = form.cleaned_data['mobile']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']

            transaction_data = Transaction.process_checkout(
                user, course, first_name, last_name, mobile, address, city
            )
            transaction = transaction_data['transaction']
            transaction_id = transaction.id

            success_url = reverse_lazy('transaction_detail', kwargs={'pk': transaction_id})
            return redirect(success_url)
        else:
            return JsonResponse({'errors': form.errors}, status=400)





class TransactionDetailView(View):
    template_name = 'transaction_detail.html'

    def get(self, request, pk, *args, **kwargs):
        transaction = get_object_or_404(Transaction, id=pk)
        context = self.get_context_data()
        context['transaction'] = transaction
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }
        return context



class AllInstructorsView(ListView):
    model = Instructor
    template_name = 'instructors.html'
    context_object_name = 'instructors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logo'] = Logo.objects.get_or_create()[0]

        context['categories'] = Categorie.objects.all()

        return context

class InstructorDetailView(DetailView):
    model = Instructor
    template_name = 'instructor-details.html'
    context_object_name = 'instructor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        courses = Course.objects.filter(instructor__user=self.object.user)

        context['courses'] = courses
        context['logo'] = Logo.objects.first()


        context['categories'] = Categorie.objects.all()

        return context



class SendMessageView(View):
    template_name = 'contact.html'
    form_class = ContactForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        logo = Logo.objects.first()
        categories = Categorie.objects.all()
        return render(request, self.template_name, {'form': form, 'logo': logo, 'categories': categories})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            messages.success(request, 'Your message was sent successfully.')
            return redirect(self.get_success_url())
        else:
            messages.error(request, 'There was an error in your submission. Please correct the errors below.')
            logo = Logo.objects.first()
            return render(request, self.template_name, {'form': form, 'logo': logo})

    def get_success_url(self):
        return reverse_lazy('login')


class AboutView(TemplateView):
    template_name = 'about-us.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['logo'] = Logo.objects.first()
        about_page_data = About_Page.objects.first()
        context['about_page'] = about_page_data

        categories = Categorie.objects.all()
        context['categories'] = categories

        about_page_points = About_page_point.objects.filter(about_point=about_page_data)
        context['about_page_points'] = about_page_points

        return context

    
class CategorieListView(ListView):
    model = Categorie
    template_name = 'categories.html'
    context_object_name = 'categories'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logo'] = Logo.objects.first()
        context['courses'] = Course.objects.all()  

        return context


class CategorieDetailView(DetailView):
    model = Categorie
    template_name = 'categories-details.html'
    context_object_name = 'categorie'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['logo'] = Logo.objects.first() 
        context['courses'] = Course.objects.filter(categories=context['categorie'])
        return context


class PaymentCancelView(View):
    template_name = 'cancel.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context


class PaymentFailureView(View):
    template_name = 'failed.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context
    

class PaymentsuccessView(View):
    template_name = 'success.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context



class Privacy_PolicyView(View):
    template_name = 'Privacy-Policy.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context


class Govt_Job_PreparationView(View):
    template_name = 'Govt-Job-Preparation.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context
    


class University_Admission_PreparationView(View):
    template_name = 'University-Admission-Preparation.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context
    

class Refunds_ReturnsView(View):
    template_name = 'Refunds-&-Returns.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context
    

class TermsConditionView(View):
    template_name = 'Terms-&-Condition.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {
            'logo': Logo.objects.first(),
            'instructors': Instructor.objects.all(),
            'courses': Course.objects.all(),
            'categories': Categorie.objects.all(),
        }

        return context