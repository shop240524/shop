from django import forms
from django.forms import ModelForm, TextInput, Textarea, DateInput, NumberInput, DateTimeInput, CheckboxInput
from .models import Organization, Invoice, Category, Author, Catalog, News, Basket, Sale, Delivery
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import re
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytz

# При разработке приложения, использующего базу данных, чаще всего необходимо работать с формами, которые аналогичны моделям.
# В этом случае явное определение полей формы будет дублировать код, так как все поля уже описаны в модели.
# По этой причине Django предоставляет вспомогательный класс, который позволит вам создать класс Form по имеющейся модели
# атрибут fields - указание списка используемых полей, при fields = '__all__' - все поля
# атрибут widgets для указания собственный виджет для поля. Его значением должен быть словарь, ключами которого являются имена полей, а значениями — классы или экземпляры виджетов.

# Организация
class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['organization_title','address','phone',]
        widgets = {
            'organization_title': TextInput(attrs={"size":"100"}),            
            'address': TextInput(attrs={"size":"80"}),
            'phone': TextInput(attrs={"size":"50", "type":"tel"}),            
        }

# Приходные накладные  
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('organization', 'datei', 'numb',)
        widgets = {
            'organization': forms.Select(attrs={'class': 'chosen'}),
            'datei': DateInput(attrs={"type":"date"}),
            'numb': DateInput(attrs={"type":"number"}),
        }
        labels = {
            'organization': _('organization_title'),
            'datei': _('datei'),
            'numb': _('numb'),            
        }
    # Метод-валидатор для поля dateis
    def clean_datei(self):
        data = self.cleaned_data['datei']
        #print(data)
        #print(timezone.now())
        # Проверка даты (не больше текущей даты-времени)
        if data > timezone.now():
            raise forms.ValidationError(_('Cannot be greater than the current date'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data
    # Метод-валидатор для поля numb
    def clean_numb(self):
        data = self.cleaned_data['numb']
        #print(data)
        # Проверка номер больше нуля
        if data <= 0:
            raise forms.ValidationError(_('The number must be greater than zero'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data        

# Категория товара
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_title',]
        widgets = {
            'category_title': TextInput(attrs={"size":"100"}),            
        }

# Автор
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['author_name',]
        widgets = {
            'author_title': TextInput(attrs={"size":"100"}),            
        }

# Товар 
class CatalogForm(forms.ModelForm):
    class Meta:
        model = Catalog
        fields = ('category', 'author', 'catalog_title', 'details', 'price',  'quantity', 'unit', 'photo')
        widgets = {
            'category': forms.Select(attrs={'class': 'chosen'}),
            'author': forms.Select(attrs={'class': 'chosen'}),
            'catalog_title': TextInput(attrs={"size":"100"}),
            'details': Textarea(attrs={'cols': 100, 'rows': 5}),            
            'price': NumberInput(attrs={"size":"10", "min": "1", "step": "1"}),
            'quantity': NumberInput(attrs={"size":"10", "min": "1", "max": "10000", "step": "1"}), 
            'unit': TextInput(attrs={"size":"50"}),            
        }
        labels = {
            'category': _('category_title'),            
            'author': _('author_name'),            
        }

    # Метод-валидатор для поля price
    def clean_price(self):
        data = self.cleaned_data['price']
        #print(data)
        # Проверка номер больше нуля
        if data <= 0:
            raise forms.ValidationError(_('Price must be greater than zero'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data       

# Доставка
class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ('movement', 'details')
        widgets = {
            'details': Textarea(attrs={'cols': 50, 'rows': 5}),            
        }
        labels = {
            'movement': _('movement'),
            'details': _('details'),            
        }
    # Метод-валидатор для поля dateis
    def clean_deliveryday(self):
        data = self.cleaned_data['deliveryday']
        #print(data)
        #print(timezone.now())
        # Проверка даты (не больше текущей даты-времени)
        if data > timezone.now():
            raise forms.ValidationError(_('Cannot be greater than the current date'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data        

# Отзывы
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['rating', 'details',]
        widgets = {
            'rating': NumberInput(attrs={"size":"10", "min": "1", "max": "5", "step": "1"}), 
            'details': Textarea(attrs={'cols': 80, 'rows': 10}),                        
        }

# Новости
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ('daten', 'news_title', 'details', 'photo')
        widgets = {
            'daten': DateTimeInput(format='%d/%m/%Y %H:%M:%S'),
            'news_title': TextInput(attrs={"size":"100"}),
            'details': Textarea(attrs={'cols': 100, 'rows': 10}),                        
        }
    # Метод-валидатор для поля daten
    def clean_daten(self):        
        if isinstance(self.cleaned_data['daten'], datetime.date) == True:
            data = self.cleaned_data['daten']
            #print(data)        
        else:
            raise forms.ValidationError(_('Wrong date and time format'))
        # Метод-валидатор обязательно должен вернуть очищенные данные, даже если не изменил их
        return data   

# Форма регистрации
class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
