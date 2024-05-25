from django.db import models
#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django import forms

from django.contrib.auth.models import User

# Модели отображают информацию о данных, с которыми вы работаете.
# Они содержат поля и поведение ваших данных.
# Обычно одна модель представляет одну таблицу в базе данных.
# Каждая модель это класс унаследованный от django.db.models.Model.
# Атрибут модели представляет поле в базе данных.
# Django предоставляет автоматически созданное API для доступа к данным

# choices (список выбора). Итератор (например, список или кортеж) 2-х элементных кортежей,
# определяющих варианты значений для поля.
# При определении, виджет формы использует select вместо стандартного текстового поля
# и ограничит значение поля указанными значениями.

# Читабельное имя поля (метка, label). Каждое поле, кроме ForeignKey, ManyToManyField и OneToOneField,
# первым аргументом принимает необязательное читабельное название.
# Если оно не указано, Django самостоятельно создаст его, используя название поля, заменяя подчеркивание на пробел.
# null - Если True, Django сохранит пустое значение как NULL в базе данных. По умолчанию - False.
# blank - Если True, поле не обязательно и может быть пустым. По умолчанию - False.
# Это не то же что и null. null относится к базе данных, blank - к проверке данных.
# Если поле содержит blank=True, форма позволит передать пустое значение.
# При blank=False - поле обязательно.

# Организации 
class Organization(models.Model):
    organization_title = models.CharField(_('organization_title'), max_length=256)
    address = models.CharField(_('address'), max_length=128)
    phone = models.CharField(_('phone'), max_length=128)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'organization'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['organization_title']),            
        ]
        # Сортировка по умолчанию
        ordering = ['organization_title']
    def __str__(self):
        # Вывод названия в тег SELECT 
        return "{}".format(self.organization_title)
        # Override the save method of the model

# Приходные накладные 
class Invoice(models.Model):
    organization = models.ForeignKey(Organization, related_name='invoice_organization', on_delete=models.CASCADE)
    datei = models.DateTimeField(_('datei'))
    numb = models.IntegerField(_('numb'))     
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'invoice'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['datei']),            
        ]
        # Сортировка по умолчанию
        ordering = ['datei']
    def __str__(self):
        # Вывод названия в тег SELECT 
        return "{}".format(self.organization)
        # Override the save method of the model

# Автор
class Author(models.Model):
    author_name = models.CharField(_('author_name'), max_length=128, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'author'
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}".format(self.author_name)

# Категория товара (услуги)
class Category(models.Model):
    category_title = models.CharField(_('category_title'), max_length=128, unique=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'category'
    def __str__(self):
        # Вывод названияв тег SELECT 
        return "{}".format(self.category_title)

# Каталог товаров (услуг)
class Catalog(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='catalog_invoice', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='catalog_category', on_delete=models.CASCADE)
    author = models.ForeignKey(Author, related_name='catalog_author', on_delete=models.CASCADE)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)
    details = models.TextField(_('catalog_details'), blank=True, null=True)
    price = models.DecimalField(_('catalog_price'), max_digits=9, decimal_places=2)
    quantity = models.IntegerField(_('quantity'))
    unit = models.CharField(_('unit'), max_length=32)
    photo = models.ImageField(_('catalog_photo'), upload_to='images/', blank=True, null=True)    
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'catalog'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['catalog_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['catalog_title']
    def __str__(self):
        # Вывод в тег SELECT 
        return "{} {} {}".format(self.category, self.author, self.catalog_title, self.price)

# Представление базы данных Каталог товаров (со средней оценкой)
class ViewCatalog(models.Model):
    invoice_id = models.IntegerField(_('invoice_id'))
    category_id = models.IntegerField(_('category_id'))
    category = models.CharField(_('category_title'), max_length=128)
    author_id = models.IntegerField(_('author_id'))
    author = models.CharField(_('author_name'), max_length=128)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)
    details = models.TextField(_('catalog_details'), blank=True, null=True)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.IntegerField(_('quantity'))
    unit = models.CharField(_('unit'), max_length=32)
    photo = models.ImageField(_('catalog_photo'), upload_to='images/', blank=True, null=True)    
    total = models.DecimalField(_('total'), max_digits=9, decimal_places=2, blank=True, null=True)
    sale_quantity = models.IntegerField(_('sale_quantity'))
    available = models.IntegerField(_('available'))
    avg_rating = models.DecimalField(_('avg_rating'), max_digits=6, decimal_places=2)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'view_catalog'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['catalog_title']),
        ]
        # Сортировка по умолчанию
        ordering = ['category', 'catalog_title']
        # Таблицу не надо не добавлять не удалять
        managed = False

# Корзина 
class Basket(models.Model):
    basketday = models.DateTimeField(_('basketday'), auto_now_add=True)
    catalog = models.ForeignKey(Catalog, related_name='basket_catalog', on_delete=models.CASCADE)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.IntegerField(_('quantity'), default=1)
    user = models.ForeignKey(User, related_name='user_basket', on_delete=models.CASCADE)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'basket'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['basketday']),
        ]
        # Сортировка по умолчанию
        ordering = ['basketday']
    # Сумма по товару
    def total(self):
        return self.price * self.quantity

# Продажа 
class Sale(models.Model):
    saleday = models.DateTimeField(_('saleday'), auto_now_add=True)
    catalog = models.ForeignKey(Catalog, related_name='sale_catalog', on_delete=models.CASCADE)
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    quantity = models.IntegerField(_('quantity'), default=1)
    user = models.ForeignKey(User, related_name='sale_user', on_delete=models.CASCADE)
    address = models.CharField(_('delivery_address'), max_length=128, blank=True, null=True)
    rating = models.IntegerField(_('rating'), blank=True, null=True)
    details = models.TextField(_('review_details'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'sale'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['saleday']),
        ]
        # Сортировка по умолчанию
        ordering = ['saleday']
    # Сумма по товару
    def total(self):
        return self.price * self.quantity
    def __str__(self):
        # Вывод в тег SELECT 
        return "{} {} {}".format(self.saleday, self.catalog, self.user.username)
        # Таблицу не надо не добавлять не удалять
        #managed = False
    def save(self):
        if self.id == None:
            super().save()
            print( str(self.id) )
            print( str(self.saleday) )
            delivery = Delivery()
            delivery.sale_id = self.id
            delivery.deliveryday = self.saleday
            delivery.movement = _('Application accepted for processing')
            delivery.details= _('Application accepted for processing')
            delivery.save()
            delivery.deliveryday = self.saleday
            delivery.save()
        else:
            super().save()

# Представление базы данных Продажа (с последним движением по доставке)
class ViewSale(models.Model):
    username = models.CharField(_('username'), max_length=128)
    first_name = models.CharField(_('first_name'), max_length=128)
    last_name = models.CharField(_('last_name'), max_length=128)
    saleday = models.DateTimeField(_('saleday'))
    catalog_id = models.IntegerField(_('catalog_id'))
    author = models.CharField(_('author_name'), max_length=128)
    category = models.CharField(_('category'), max_length=128)
    catalog_title = models.CharField(_('catalog_title'), max_length=255)        
    price = models.DecimalField(_('price'), max_digits=9, decimal_places=2)
    photo = models.ImageField(_('photo'), upload_to='images/', blank=True, null=True)
    quantity = models.IntegerField(_('quantity'))
    total = models.DecimalField(_('total'), max_digits=9, decimal_places=2)
    user_id = models.IntegerField(_('user_id'))
    address = models.CharField(_('delivery_address'), max_length=128, blank=True, null=True)
    rating = models.IntegerField(_('rating'), blank=True, null=True)
    details = models.TextField(_('review_details'), blank=True, null=True)
    final = models.TextField(_('final'), blank=True, null=True)
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'view_sale'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['saleday']),
        ]
        # Сортировка по умолчанию
        ordering = ['saleday']
        # Таблицу не надо не добавлять не удалять
        managed = False
    # Сумма по товару
    def total(self):
        return self.price * self.quantity
    #def __str__(self):
    #    return "{} {} {}".format(self.category, self.title, self.username)

# Доставка товара
class Delivery(models.Model):
    DELIVERY_CHOICES = (
        (_('Application accepted for processing'),_('Application accepted for processing')),
        (_('Goods in transit'), _('Goods in transit')),
        (_('Stock item'), _('Stock item')),
        (_('The application is closed, the goods have been delivered'), _('The application is closed, the goods have been delivered')),
    )
    sale = models.ForeignKey(Sale, related_name='sale_delivery', on_delete=models.CASCADE)    
    deliveryday = models.DateTimeField(_('deliveryday'), auto_now_add=True)
    movement = models.CharField(_('movement'), max_length=64, choices=DELIVERY_CHOICES, default='М')
    details = models.TextField(_('delivery_details'), blank=True, null=True) 
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'delivery'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['deliveryday']),
        ]
        # Сортировка по умолчанию
        ordering = ['deliveryday']
    def __str__(self):
        # Вывод в тег SELECT 
        return "{} {} {}".format(self.deliveryday, self.sale, self.movement)
            
# Новости 
class News(models.Model):
    daten = models.DateTimeField(_('daten'))
    news_title = models.CharField(_('news_title'), max_length=256)
    details = models.TextField(_('news_details'))
    photo = models.ImageField(_('news_photo'), upload_to='images/', blank=True, null=True)    
    class Meta:
        # Параметры модели
        # Переопределение имени таблицы
        db_table = 'news'
        # indexes - список индексов, которые необходимо определить в модели
        indexes = [
            models.Index(fields=['daten']),
        ]
        # Сортировка по умолчанию
        ordering = ['daten']
