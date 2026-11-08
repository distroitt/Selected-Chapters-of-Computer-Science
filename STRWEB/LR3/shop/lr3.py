"""LR3: небольшие JSON-обработчики поверх существующих моделей магазина."""
import re
from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import Employee, SliderSettings

PHONE = re.compile(r'^(?:8\s*(?:\(0\d{2}\)|0\d{2})|\+375\s*(?:\(\d{2}\)|\d{2}))[\s-]*\d(?:[\s-]*\d){6}$')
PHOTO = re.compile(r'^https?://[^\s/?#]+/[^\s?#]*\.(?:php|html)$', re.I)


class ContactForm(forms.ModelForm):
    photo_url = forms.URLField(label="URL фотографии", required=True, max_length=200, assume_scheme="https")

    class Meta:
        model = Employee
        fields = ['full_name', 'position', 'phone', 'email', 'photo_url']
        widgets = {'position': forms.Textarea(attrs={'rows': 2})}

    def clean_phone(self):
        value = self.cleaned_data['phone'].strip()
        if not PHONE.fullmatch(value):
            raise forms.ValidationError('Введите белорусский номер: 80291112233 или +375 (29) 111-22-33.')
        digits = re.sub(r'\D', '', value)
        digits = digits[2:] if digits.startswith('80') else digits[3:]
        return f'+375 ({digits[:2]}) {digits[2:5]}-{digits[5:7]}-{digits[7:]}'

    def clean_photo_url(self):
        value = self.data.get('photo_url', '').strip()
        if not PHOTO.fullmatch(value):
            raise forms.ValidationError('URL должен начинаться с http:// или https:// и заканчиваться .php или .html.')
        return value


class SliderForm(forms.ModelForm):
    class Meta:
        model = SliderSettings
        fields = ['delay', 'loop', 'navs', 'pags', 'auto', 'stopMouseHover']


def employee_data(employee):
    return {key: getattr(employee, key) for key in ('id', 'full_name', 'position', 'phone', 'email', 'photo_url')}


def employees_table(request):
    return render(request, 'shop/employees_table.html', {'contact_form': ContactForm()})


def js_lab(request):
    return render(request, 'shop/js_lab.html')


@require_http_methods(['GET', 'POST'])
def employees_api(request):
    if request.method == 'GET':
        return JsonResponse({'employees': [employee_data(e) for e in Employee.objects.all()]})
    if not request.user.is_staff:
        return JsonResponse({'error': 'Добавление доступно администратору. Войдите в учетную запись сотрудника.'}, status=403)
    form = ContactForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors}, status=400)
    employee = form.save()
    return JsonResponse({'employee': employee_data(employee)}, status=201)


@require_http_methods(['GET', 'POST'])
def slider_settings(request):
    settings, _ = SliderSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        if not request.user.is_staff:
            return JsonResponse({'error': 'Настройки доступны администратору.'}, status=403)
        form = SliderForm(request.POST, instance=settings)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=400)
        settings = form.save()
    return JsonResponse({field: getattr(settings, field) for field in SliderForm.Meta.fields})
