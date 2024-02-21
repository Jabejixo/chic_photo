from django.contrib import admin
from .models import Role, User, Photographer, PhotoDirectory, StudioSpace, Service, Order

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('roleName',)
    search_fields = ('roleName',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'RoleID')
    list_filter = ('is_active', 'is_staff', 'RoleID')
    search_fields = ('email', 'first_name', 'last_name')

class PhotoDirectoryInline(admin.TabularInline):
    model = PhotoDirectory

class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('user', 'skills', 'schedule')
    inlines = [PhotoDirectoryInline]

admin.site.register(Photographer, PhotographerAdmin)
admin.site.register(PhotoDirectory)

@admin.register(StudioSpace)
class StudioSpaceAdmin(admin.ModelAdmin):
    list_display = ('spaceName', 'description', 'costPerHour', 'availability', 'image')
    list_filter = ('availability',)
    search_fields = ('spaceName', 'description')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('serviceName', 'description', 'cost')
    search_fields = ('serviceName', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'userID', 'photographerID', 'spaceID', 'scheduledDate', 'timeFrom', 'timeTo', 'totalCost')
    search_fields = ('userID__email', 'photographerID__user__first_name', 'photographerID__user__last_name', 'spaceID__spaceName')
