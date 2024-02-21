from bootstrap_datepicker_plus.widgets import DatePickerInput, TimePickerInput
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q
from .models import Order, Photographer, User, PhotoDirectory


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['photographerID', 'spaceID','serviceID', 'scheduledDate', 'timeFrom', 'timeTo']
        widgets = {
            'photographerID': forms.Select(attrs={'class': 'form-select'}),
            'serviceID': forms.Select(attrs={'class': 'form-select'}),
            'spaceID': forms.Select(attrs={'class': 'form-select'}),
            'scheduledDate': DatePickerInput(),
            'timeFrom': TimePickerInput(),
            'timeTo': TimePickerInput(),
        }

    def clean_scheduledDate(self):
        scheduled_date = self.cleaned_data.get('scheduledDate')
        if scheduled_date < timezone.now().date():
            raise forms.ValidationError("")
        elif scheduled_date > timezone.now().date() + timezone.timedelta(days=14):
            raise forms.ValidationError("The date cannot be later than 14 days from the current date")
        return scheduled_date

    def clean(self):
        cleaned_data = super().clean()
        time_from = cleaned_data.get('timeFrom')
        time_to = cleaned_data.get('timeTo')
        if time_from and time_to:
            if time_from.hour < 8 or time_to.hour > 19:
                raise forms.ValidationError("The time should be between 8 a.m. and 7 p.m.")
            if time_from >= time_to:
                raise forms.ValidationError("The start time must be earlier than the end time")

        space_id = cleaned_data.get('spaceID')
        scheduled_date = cleaned_data.get('scheduledDate')

        # Проверка на перекрывающиеся заказы
        overlapping_orders = Order.objects.filter(
            spaceID=space_id,
            scheduledDate=scheduled_date
        ).filter(
            Q(timeFrom__lte=time_from, timeTo__gte=time_to) |  # Новый заказ полностью перекрывает существующий
            Q(timeFrom__lte=time_from, timeTo__gte=time_to) |  # Новый заказ полностью входит в существующий
            Q(timeFrom__lte=time_from, timeTo__lte=time_to, timeTo__gt=time_from) |  # Начало нового заказа внутри существующего
            Q(timeFrom__gte=time_from, timeTo__gte=time_to, timeFrom__lt=time_to)
            # Конец нового заказа внутри существующего
        ).exclude(id=self.instance.id if self.instance else None)

        if overlapping_orders.exists():
            raise ValidationError(
                "There is already an order for this place at this time."
            )

        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PhotographerForm(forms.ModelForm):
    # Define a new field for photo upload
    new_photo = forms.ImageField(required=False, label='Upload Photo')

    class Meta:
        model = Photographer
        fields = ['skills', 'schedule']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control'}),
            'schedule': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = PhotoDirectory
        fields = ['photo', 'photographer']