from django.contrib import admin

from .models import Projects, Authors, Categories, Technologies, Submissions, Updates

# Register your models here.

admin.site.register(Projects)
admin.site.register(Authors)
admin.site.register(Updates)
admin.site.register(Categories)
admin.site.register(Technologies)
admin.site.register(Submissions)