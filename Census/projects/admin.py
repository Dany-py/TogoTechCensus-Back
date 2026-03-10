from django.contrib import admin

from .models import Projects, Authors, Audiences, Categories, Technologies, Submissions

# Register your models here.

admin.site.register(Projects)
admin.site.register(Authors)
admin.site.register(Audiences)
admin.site.register(Categories)
admin.site.register(Technologies)
admin.site.register(Submissions)