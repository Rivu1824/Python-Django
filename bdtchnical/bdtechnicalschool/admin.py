from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)

admin.site.register(User, UserAdmin)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user','title', 'sub_title', 'description','serial_Id', 'bio','designation','facebook_link','linkedin_link','instagram_link')

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_class', 'description', 'slug','image','serial_number_Categorie')



class CoursePointInline(admin.StackedInline):
    model = course_point
    extra = 3  

class CourseAdmin(admin.ModelAdmin):
    inlines = [CoursePointInline]

    list_display = ('title', 'instructor', 'price', 'status', 'created_at')
    list_filter = ('status', 'level')
    search_fields = ('title', 'instructor__name')

admin.site.register(Course, CourseAdmin)
admin.site.register(course_point)




@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'enrollment_date', 'duration']
    search_fields = ['user__username', 'course__title']
    list_filter = ['course']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'transaction_id', 'amount','timestamp','payment_status']
    search_fields = ['user__username', 'course__title', 'transaction_id']
    list_filter = ['course']


class VideoInline(admin.TabularInline):
    model = Video

class LessonAdmin(admin.ModelAdmin):
    inlines = [VideoInline]

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson','preview', 'duration', 'created_at', 'timestamp','serial_number')
    list_filter = ('lesson', 'created_at', 'timestamp')
    search_fields = ['title', 'lesson__title']

admin.site.register(Lesson, LessonAdmin)
admin.site.register(Video, VideoAdmin)


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ('file','facebook_link','linkedin_link','instagram_link','mobile_number','email')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_title','description', 'image',)



class AboutEnrolledPointInline(admin.StackedInline):
    model = About_Enrolled_point
    extra = 1 

@admin.register(About_Enrolled)
class EnrolledAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image', 'video_file', 'Enrolled_Students')
    inlines = [AboutEnrolledPointInline]

class AboutEnrolledPointAdmin(admin.ModelAdmin):
    list_display = ('about_point', 'point')
    search_fields = ('about_point__title', 'point')

admin.site.register(About_Enrolled_point, AboutEnrolledPointAdmin)


class FAQBannerPointInline(admin.StackedInline):
    model = FAQBanner_point
    extra = 1 

@admin.register(FAQBanner)
class FAQBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'image')
    inlines = [FAQBannerPointInline]

class FAQBannerPointAdmin(admin.ModelAdmin):
    list_display = ('title', 'point', 'sub_title')
    search_fields = ('title__title', 'point', 'sub_title')

admin.site.register(FAQBanner_point, FAQBannerPointAdmin)



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'website', 'created_at']
    search_fields = ['name', 'email', 'website']
    list_filter = ['created_at']



class ShortBarAdmin(admin.ModelAdmin):
    list_display = ('Students_number', 'Faculty_number', 'Professors_number', 'Award_number')
    search_fields = ('Students_number', 'Faculty_number', 'Professors_number', 'Award_number')

admin.site.register(short_Bar, ShortBarAdmin)



class AboutPagePointAdmin(admin.ModelAdmin):
    list_display = ('about_point', 'point')
    list_filter = ('about_point',)
    search_fields = ('point',)

admin.site.register(About_page_point, AboutPagePointAdmin)


class AboutPagePointInline(admin.StackedInline):
    model = About_page_point
    extra = 1 

class AboutPageAdmin(admin.ModelAdmin):
    inlines = [AboutPagePointInline]
    list_display = ('title', 'sub_title', 'description')
    search_fields = ('title', 'sub_title',)
    list_filter = ('title', 'sub_title',)

admin.site.register(About_Page, AboutPageAdmin)
