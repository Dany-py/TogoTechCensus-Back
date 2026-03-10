from django.db import models
from users.models import Users
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Projects(models.Model):
    # Identification

    class Type(models.TextChoices):
        ACCELERATOR  = 'ACC', _('accelerator'),
        OPENSOURCE = 'OS', _('open source'),
        ENTERPRISE = 'ENT', _('entreprise'),
        COMMUNITY = 'COM', _('community'),
        INCUBATOR = 'INC', _('incubator'),
        ONG = 'ONG', _('organisation'),
        STARTUP = 'STP', _('startup'),
        HUB = 'HUB', _('hub')
    
    class Stage(models.TextChoices):
        EARLY = 'EA', _('early'),
        GROWTH = 'GR', _('growth'),
        MATURITY = 'MA', _('maturity')

    name = models.CharField(max_length=200, unique=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)  # URLField → SlugField

    # General information
    description = models.TextField()
    short_description = models.CharField(max_length=300)
    logo_url = models.ImageField(upload_to='media/', blank=True, null=True)
    cover_image_url = models.ImageField(upload_to='media/', blank=True, null=True)
    
    # Classification
    type = models.CharField(max_length=100, null=True, db_index=True)
    #status = models.CharField(max_length=50, db_index=True)
    stage = models.CharField(max_length=100, default=Stage.EARLY, db_index=True)
    needs = models.CharField(max_length=100, db_index=True)
    
    # Contact
    website_url = models.URLField(max_length=500, blank=True)
    github_url = models.URLField(max_length=500, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)
    twitter_url = models.URLField(max_length=500, blank=True)
    email = models.EmailField(max_length=200, blank=True)

    # Localisation
    city = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=10, null=True, blank=True)
    longitude = models.DecimalField(max_digits=13, decimal_places=10, null=True, blank=True)
    
    # Dates
    founded_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metrics
    view_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)

    # Moderation
    is_verified = models.BooleanField(default=False, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    #is_featured = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_project', null=True)

    # Relations many-to-many
    categories = models.ManyToManyField('Categories', through='ProjectCategory', related_name='projects')
    technologies = models.ManyToManyField('Technologies', through='ProjectTechnology', related_name='projects')
    authors = models.ManyToManyField('Authors', through='ProjectAuthor', related_name='projects')

    class Meta:
        app_label = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id}-{self.name}"


class Categories(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class ProjectCategory(models.Model):
    """Table intermédiaire pour la relation Projects-Categories"""
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['project', 'category']]
        verbose_name = 'Project Category'
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return f"{self.project.name} - {self.category.name}"


class Technologies(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    type = models.CharField(max_length=50)
    logo_url = models.ImageField(upload_to='tech_logos/', blank=True)
    popularity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Technology'
        verbose_name_plural = 'Technologies'
        ordering = ['-popularity', 'name']

    def __str__(self):
        return self.name


class ProjectTechnology(models.Model):
    """Table intermédiaire pour la relation Projects-Technologies"""
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    technology = models.ForeignKey(Technologies, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['project', 'technology']]
        verbose_name = 'Project Technology'
        verbose_name_plural = 'Project Technologies'

    def __str__(self):
        return f"{self.project.name} - {self.technology.name}"


class Authors(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250)
    email = models.EmailField(max_length=200, blank=True)
    github_url = models.URLField(max_length=500, blank=True)
    linkedin_url = models.URLField(max_length=500, blank=True)
    twitter_url = models.URLField(max_length=500, blank=True)
    avatar_url = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.name


class ProjectAuthor(models.Model):
    """Table intermédiaire pour la relation Projects-Authors"""
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['project', 'author']]
        verbose_name = 'Project Author'
        verbose_name_plural = 'Project Authors'

    def __str__(self):
        return f"{self.author.name} - {self.project.name}"


class Audiences(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='audiences')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Audience'
        verbose_name_plural = 'Audiences'
        unique_together = [['project', 'name']]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Updates(models.Model):
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=100)
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Update'
        verbose_name_plural = 'Updates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.title}"
    
 
# Model Submissions
class Submissions(models.Model):
    
    class Status(models.TextChoices):
        PENDING = 'PG', _('Attente')
        APPROVED = 'AP', _('Approuvé')
        REJECTED = 'RJ', _('Rejeté')

    submitted_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='submitted_submissions')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=2, choices=Status, default=Status.PENDING, db_index=True)
    reviewed_by = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='reviewed_submissions', db_index=True)
    review_notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        ordering = ['-created_at']
