from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models
from django.contrib.auth.models import User, PermissionsMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email, password, **extra_fields
        )

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(
            email, password, **extra_fields
        )


class Role(models.Model):
    roleName = models.CharField(max_length=10) #Client, Photographer, Admin

    def __str__(self):
        return self.roleName

class User(AbstractBaseUser, PermissionsMixin):
    username = None
    RoleID = models.ForeignKey('Role', on_delete=models.CASCADE, db_default=1)
    email = models.EmailField(unique=True)
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True)
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True)

    is_active = models.BooleanField(db_default=True)
    is_staff = models.BooleanField(db_default=False)
    USERNAME_FIELD = 'email'
    objects = UserManager()

    def get_role(self):
        return self.RoleID

class Photographer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skills = models.TextField(null=True, blank=True)
    schedule = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.user.first_name

class PhotoDirectory(models.Model):
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='photos/')

    def __str__(self):
        return self.photo.name

class StudioSpace(models.Model):
    spaceName = models.CharField(max_length=20, db_index=True)
    description = models.TextField()
    costPerHour = models.DecimalField(max_digits=10, decimal_places=2)
    availability = models.BooleanField()
    image = models.ImageField(upload_to='studios/', null=True, blank=True)

    def __str__(self):
        return self.spaceName

class Service(models.Model):
    serviceName = models.CharField(max_length=20, db_index=True)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.serviceName

class Order(models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    serviceID = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    photographerID = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    spaceID = models.ForeignKey(StudioSpace, on_delete=models.CASCADE)
    scheduledDate = models.DateField()
    timeFrom = models.TimeField()
    timeTo = models.TimeField()
    active = models.BooleanField(db_default=True)
    totalCost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id} - {self.userID.first_name + " " + self.userID.last_name}"

