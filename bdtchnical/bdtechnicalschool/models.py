from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import *
from .utils import *
from django.contrib.auth.models import *


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username must be set")

        if not email:
            raise ValueError("Email must be set")

        email = self.normalize_email(email)
        user = self.model(username=username,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

        

    def create_superuser(self, email, username, password=None, **extra_fields):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
            *extra_fields
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=30, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ['-date_joined']
        verbose_name_plural = '01. User'



class Instructor(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    description = models.TextField()
    serial_Id =models.IntegerField(null=True)
    instructor_profile = models.ImageField(upload_to="author")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    designation = models.CharField(max_length=50)
    bio = models.TextField()

    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


class Categorie(models.Model):
    image = models.ImageField(upload_to="Media/Categorie",null=False)
    title = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=50)
    serial_number_Categorie =models.IntegerField(null=True)
    description = models.TextField()
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return self.title

def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Categorie.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

@receiver(pre_save, sender=Categorie)
def pre_save_categorie_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_categorie_receiver, Categorie)


class Course(models.Model):
    LEVEL_CHOICES = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    STATUS = (
        ('PUBLISH', 'PUBLISH'),
        ('DRAFT', 'DRAFT'),
    )
    image = models.ImageField(upload_to="Media/img", null=True)
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    description = models.TextField()
    categories = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    level = models.CharField(choices=LEVEL_CHOICES, max_length=20, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)
    status = models.CharField(choices=STATUS, max_length=100, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def calculate_discounted_price(self):
        discount_amount = (self.discount_percentage / 100) * self.price
        discounted_price = self.price - discount_amount
        return max(discounted_price, 0)

    def save(self, *args, **kwargs):

        self.total_amount = self.calculate_discounted_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    
def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    qs = Course.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug


@receiver(pre_save, sender=Course)
def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Course)



class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(default=timezone.timedelta(days=365))

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"




class Transaction(models.Model):

    STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    )


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=50)
    payment_status = models.CharField(choices=STATUS, max_length=100, default='Pending')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.mobile
    
    @classmethod
    def process_checkout(cls, user, course, first_name, last_name, mobile, address, city):

        transaction = Transaction.objects.create(
             user=user, 
             course=course,
             transaction_id=generate_unique_transaction_id(),
             amount=course.calculate_discounted_price(),
             first_name=first_name,
             last_name=last_name,
             mobile=mobile,
             address=address,
             city=city,
             payment_status='Pending',
)

        return {'transaction': transaction}




class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Video(models.Model):
    serial_number =models.IntegerField(null=True)
    title = models.CharField(max_length=200)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    video_file = models.FileField(upload_to="Media/videos/")
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(default=timezone.now)
    preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Logo(models.Model):
    file = models.ImageField(upload_to='logo_files/')
    email = models.EmailField(max_length=254, unique=True)
    mobile_number = models.BigIntegerField(unique=True)
    facebook_link = models.URLField(max_length=200, blank=True, null=True)
    linkedin_link = models.URLField(max_length=200, blank=True, null=True)
    instagram_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return str(self.file)


class Banner(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='home/banner_images/')

    def __str__(self):
        return self.title

class About_Enrolled(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='banner_images/')
    Enrolled_Students= models.ImageField(upload_to='Enrolled_Students')
    video_file = models.FileField(upload_to="media/About_Enrolled/videos/")

    def __str__(self):
        return self.title

class FAQBanner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='FAQbanner_images/')

    def __str__(self):
        return self.title



class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    website = models.URLField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class About_Page(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='about/banner_images/')
    video_file = models.FileField(upload_to="media/About_Enrolled/videos/")

    def __str__(self):
        return self.title
    
class About_page_point(models.Model):
    about_point = models.ForeignKey(About_Page, on_delete=models.CASCADE)
    point = models.CharField(max_length=200)

    def __str__(self):
        return self.point
    

class course_point(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    point = models.CharField(max_length=200)

    def __str__(self):
        return self.point


class About_Enrolled_point(models.Model):
    about_point = models.ForeignKey(About_Enrolled, on_delete=models.CASCADE)
    point = models.CharField(max_length=200)

    def __str__(self):
        return self.point
    

class FAQBanner_point(models.Model):
    title  = models.ForeignKey(FAQBanner, on_delete=models.CASCADE)
    point = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=255)

    def __str__(self):
        return self.point
    


class short_Bar(models.Model):
    Students_number = models.IntegerField(null=True)
    Faculty_number = models.IntegerField(null=True)
    Professors_number = models.IntegerField(null=True)
    Award_number = models.IntegerField(null=True)

    def __str__(self):
        return f"Students: {self.Students_number}, Faculty: {self.Faculty_number}, Professors: {self.Professors_number}, Award: {self.Award_number}"
