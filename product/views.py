from django.shortcuts import render, redirect

# Класс HttpResponse из пакета django.http, который позволяет отправить текстовое содержимое.
from django.http import HttpResponse, HttpResponseNotFound
# Конструктор принимает один обязательный аргумент – путь для перенаправления. Это может быть полный URL (например, 'https://www.yahoo.com/search/') или абсолютный путь без домена (например, '/search/').
from django.http import HttpResponseRedirect

from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from django.db.models import Max
from django.db.models import Q

from datetime import datetime, timedelta

# Отправка почты
from django.core.mail import send_mail

# Подключение моделей
from .models import Organization, Invoice, Category, Author, Catalog, ViewCatalog, Basket, Sale, ViewSale, Delivery, News
# Подключение форм
from .forms import OrganizationForm, InvoiceForm, CategoryForm, AuthorForm, CatalogForm, DeliveryForm, ReviewForm, NewsForm, SignUpForm

from django.db.models import Sum

from django.db import models

import sys

import math

#from django.utils.translation import ugettext as _
from django.utils.translation import gettext_lazy as _

from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy

from django.contrib.auth import login as auth_login

from django.db.models.query import QuerySet

import csv
import xlwt
from io import BytesIO

# Create your views here.
# Групповые ограничения
def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

###################################################################################################

# Стартовая страница 
def index(request):
    try:
        catalog = ViewCatalog.objects.all().order_by('?')[0:4]
        review = ViewSale.objects.exclude(rating=None).order_by('?')[0:4]
        news1 = News.objects.all().order_by('-daten')[0:1]
        news24 = News.objects.all().order_by('-daten')[1:4]
        return render(request, "index.html", {"catalog": catalog, "review": review, "news1": news1, "news24": news24})    
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)    

# Контакты
def contact(request):
    try:
        return render(request, "contact.html")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


###################################################################################################

# Отчеты
@login_required
@group_required("Managers")
def report_index(request):
    try:
        start_date = datetime(datetime.now().year, 1, 1, 0, 0).strftime('%Y-%m-%d') 
        finish_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0, 0).strftime('%Y-%m-%d')         
        catalog = ViewCatalog.objects.all().order_by('catalog_title')
        sale = ViewSale.objects.all().order_by('saleday')
        total_sale = ViewSale.objects.aggregate(Sum('price'))
        delivery = Delivery.objects.all().order_by('deliveryday')
        review = ViewSale.objects.exclude(rating=None).order_by('saleday')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по дате
                start_date = request.POST.get("start_date")
                #print(start_date)
                finish_date = request.POST.get("finish_date")
                finish_date = str(datetime.strptime(finish_date, "%Y-%m-%d") + timedelta(days=1))
                total_sale = ViewSale.objects.filter(saleday__range=[start_date, finish_date]).aggregate(Sum('price'))
                print(total_sale)
                sale = ViewSale.objects.filter(saleday__range=[start_date, finish_date]).order_by('saleday')                
                delivery = Delivery.objects.filter(deliveryday__range=[start_date, finish_date]).order_by('deliveryday')
                review = ViewSale.objects.exclude(rating=None).filter(saleday__range=[start_date, finish_date]).order_by('saleday')
                finish_date = request.POST.get("finish_date")
        return render(request, "report/index.html", {"catalog": catalog, "sale": sale, "delivery": delivery, "review": review, "total_sale": total_sale, "start_date": start_date, "finish_date": finish_date,  })    
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)    

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def organization_index(request):
    try:
        organization = Organization.objects.all().order_by('organization_title')
        return render(request, "organization/index.html", {"organization": organization})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def organization_create(request):
    try:    
        if request.method == "POST":
            organization = Organization()
            organization.organization_title = request.POST.get("organization_title")
            organization.address = request.POST.get("address")
            organization.phone = request.POST.get("phone")                
            organizationform = OrganizationForm(request.POST)
            if organizationform.is_valid():
                organization.save()
                return HttpResponseRedirect(reverse('organization_index'))
            else:
                return render(request, 'organization/create.html', {'form': organizationform})            
        else:        
            organizationform = OrganizationForm()
            return render(request, "organization/create.html", {"form": organizationform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def organization_edit(request, id):
    try:
        organization = Organization.objects.get(id=id) 
        if request.method == "POST":
            organization.organization_title = request.POST.get("organization_title")
            organization.address = request.POST.get("address")
            organization.phone = request.POST.get("phone")
            organizationform = OrganizationForm(request.POST)
            if organizationform.is_valid():
                print(organization.phone)
                organization.save()
                return HttpResponseRedirect(reverse('organization_index'))
            else:
                print(0)
                return render(request, "organization/edit.html", {"form": organizationform}) 
        else:
            # Загрузка начальных данных
            organizationform = OrganizationForm(initial={'organization_title': organization.organization_title, 'address': organization.address, 'phone': organization.phone })
            return render(request, "organization/edit.html", {"form": organizationform})
    except Organization.DoesNotExist:
        return HttpResponseNotFound("<h2>Organization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def organization_delete(request, id):
    try:
        organization = Organization.objects.get(id=id)
        organization.delete()
        return HttpResponseRedirect(reverse('organization_index'))
    except Organization.DoesNotExist:
        return HttpResponseNotFound("<h2>Organization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def organization_read(request, id):
    try:
        organization = Organization.objects.get(id=id) 
        return render(request, "organization/read.html", {"organization": organization})
    except Organization.DoesNotExist:
        return HttpResponseNotFound("<h2>Organization not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Получить следующий порядковый номер накладной (в текущем году)
def get_invoice_number():
    try:
        current_datetime = datetime.now()
        max = Invoice.objects.filter(datei__year=current_datetime.year).aggregate(Max('numb'))['numb__max']
        if max == None:
            max = 0
        return max+1
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def invoice_index(request):
    try:
        invoice = Invoice.objects.all().order_by('datei')
        return render(request, "invoice/index.html", {"invoice": invoice})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def invoice_create(request):
    try:
        if request.method == "POST":
            invoice = Invoice()
            invoice.organization = Organization.objects.filter(id=request.POST.get("organization")).first()
            invoice.datei = request.POST.get("datei")
            invoice.numb = request.POST.get("numb")
            invoiceform = InvoiceForm(request.POST)
            if invoiceform.is_valid():
                invoice.save()
                return HttpResponseRedirect(reverse('invoice_index'))
            else:
                return render(request, "invoice/create.html", {"form": invoiceform})
        else:        
            invoiceform = InvoiceForm(initial={'datei': datetime.now().strftime('%Y-%m-%d'), 'numb': get_invoice_number() })        
            return render(request, "invoice/create.html", {"form": invoiceform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def invoice_edit(request, id):
    try:
        invoice = Invoice.objects.get(id=id) 
        if request.method == "POST":
            invoice.organization = Organization.objects.filter(id=request.POST.get("organization")).first()
            invoice.datei = request.POST.get("datei")
            invoice.numb = request.POST.get("numb")
            invoiceform = InvoiceForm(request.POST)
            if invoiceform.is_valid():
                invoice.save()
                return HttpResponseRedirect(reverse('invoice_index'))
            else:
                return render(request, "invoice/edit.html", {"form": invoiceform})
        else:
            # Загрузка начальных данных
            invoiceform = InvoiceForm(initial={'organization': invoice.organization, 'datei': invoice.datei.strftime('%Y-%m-%d'), 'numb': invoice.numb })
            return render(request, "invoice/edit.html", {"form": invoiceform})
    except Invoice.DoesNotExist:
        return HttpResponseNotFound("<h2>Invoice not found</h2>")

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def invoice_delete(request, id):
    try:
        invoice = Invoice.objects.get(id=id)
        invoice.delete()
        return HttpResponseRedirect(reverse('invoice_index'))
    except Invoice.DoesNotExist:
        return HttpResponseNotFound("<h2>Invoice not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def invoice_read(request, id):
    try:
        invoice = Invoice.objects.get(id=id) 
        return render(request, "invoice/read.html", {"invoice": invoice})
    except Invoice.DoesNotExist:
        return HttpResponseNotFound("<h2>Invoice not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def category_index(request):
    try:
        category = Category.objects.all().order_by('category_title')
        return render(request, "category/index.html", {"category": category,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def category_create(request):
    try:
        if request.method == "POST":
            category = Category()
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/create.html", {"form": categoryform})
        else:        
            categoryform = CategoryForm()
            return render(request, "category/create.html", {"form": categoryform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def category_edit(request, id):
    try:
        category = Category.objects.get(id=id)
        if request.method == "POST":
            category.category_title = request.POST.get("category_title")
            categoryform = CategoryForm(request.POST)
            if categoryform.is_valid():
                category.save()
                return HttpResponseRedirect(reverse('category_index'))
            else:
                return render(request, "category/edit.html", {"form": categoryform})
        else:
            # Загрузка начальных данных
            categoryform = CategoryForm(initial={'category_title': category.category_title, })
            return render(request, "category/edit.html", {"form": categoryform})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def category_delete(request, id):
    try:
        category = Category.objects.get(id=id)
        category.delete()
        return HttpResponseRedirect(reverse('category_index'))
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@group_required("Managers")
def category_read(request, id):
    try:
        category = Category.objects.get(id=id) 
        return render(request, "category/read.html", {"category": category})
    except Category.DoesNotExist:
        return HttpResponseNotFound("<h2>Category not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def author_index(request):
    try:
        author = Author.objects.all().order_by('author_name')
        return render(request, "author/index.html", {"author": author,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def author_create(request):
    try:
        if request.method == "POST":
            author = Author()
            author.author_name = request.POST.get("author_name")
            authorform = AuthorForm(request.POST)
            if authorform.is_valid():
                author.save()
                return HttpResponseRedirect(reverse('author_index'))
            else:
                return render(request, "author/create.html", {"form": authorform})
        else:        
            authorform = AuthorForm()
            return render(request, "author/create.html", {"form": authorform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def author_edit(request, id):
    try:
        author = Author.objects.get(id=id)
        if request.method == "POST":
            author.author_name = request.POST.get("author_name")
            authorform = AuthorForm(request.POST)
            if authorform.is_valid():
                author.save()
                return HttpResponseRedirect(reverse('author_index'))
            else:
                return render(request, "author/edit.html", {"form": authorform})
        else:
            # Загрузка начальных данных
            authorform = AuthorForm(initial={'author_name': author.author_name, })
            return render(request, "author/edit.html", {"form": authorform})
    except Author.DoesNotExist:
        return HttpResponseNotFound("<h2>Author not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def author_delete(request, id):
    try:
        author = Author.objects.get(id=id)
        author.delete()
        return HttpResponseRedirect(reverse('author_index'))
    except Author.DoesNotExist:
        return HttpResponseNotFound("<h2>Author not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
@group_required("Managers")
def author_read(request, id):
    try:
        author = Author.objects.get(id=id) 
        return render(request, "author/read.html", {"author": author})
    except Author.DoesNotExist:
        return HttpResponseNotFound("<h2>Author not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

####################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def catalog_index(request, invoice_id):
    try:
        #catalog = Catalog.objects.all().order_by('title')
        invoice = Invoice.objects.get(id=invoice_id)
        catalog = Catalog.objects.filter(invoice_id=invoice_id).order_by('catalog_title')
        return render(request, "catalog/index.html", {"catalog": catalog, "invoice": invoice, "invoice_id": invoice_id})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
    
# Список для просмотра и отправки в корзину
#@login_required
#@group_required("Managers")
#@login_required
def catalog_list(request):
    try:
        # Текущий пользователь
        _user_id = request.user.id
        # Каталог доступных товаров
        catalog = ViewCatalog.objects.all().order_by('category').order_by('catalog_title')
        # Категории и подкатегория товара (для поиска)
        category = Category.objects.all().order_by('category_title')
        # Автор
        author = Author.objects.all().order_by('author_name')
        # Доступны записи только текущего пользователя
        basket = Basket.objects.filter(user_id=_user_id).order_by('basketday')
        # Количество товара в корзине и общая стоимость товарв в корзине для пользователя _user_id
        basket_count, basket_total = basket_count_total(_user_id)   
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по категории товара
                selected_item_category = request.POST.get('item_category')
                #print(selected_item_category)
                if selected_item_category != '-----':
                    category_query = Category.objects.filter(category_title = selected_item_category).only('id').all()
                    catalog = catalog.filter(category_id__in = category_query).all()
                # Поиск по автору
                selected_item_author = request.POST.get('item_author')
                #print(selected_item_author)
                if selected_item_author != '-----':
                    author_query = Author.objects.filter(author_name = selected_item_author).only('id').all()
                    catalog = catalog.filter(author_id__in = author_query).all()
                # Поиск по названию товара
                catalog_search = request.POST.get("catalog_search")
                #print(catalog_search)                
                if catalog_search != '':
                    catalog = catalog.filter(catalog_title__contains = catalog_search).all()
                # Сортировка
                sort = request.POST.get('radio_sort')
                #print(sort)
                direction = request.POST.get('checkbox_sort_desc')
                #print(direction)
                if sort=='title':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-catalog_title')
                    else:
                        catalog = catalog.order_by('catalog_title')
                elif sort=='author':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-author')
                    else:
                        catalog = catalog.order_by('author')
                elif sort=='price':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-price')
                    else:
                        catalog = catalog.order_by('price')
                elif sort=='category':                    
                    if direction=='ok':
                        catalog = catalog.order_by('-category')
                    else:
                        catalog = catalog.order_by('category')
                return render(request, "catalog/list.html", {"catalog": catalog, "category": category, "selected_item_category": selected_item_category, "author": author, "selected_item_author": selected_item_author, "catalog_search": catalog_search, "sort": sort, "direction": direction,})    
            elif 'resetBtn' in request.POST:
                return render(request, "catalog/list.html", {"catalog": catalog, "category": category, "author": author,})  
            else:          
                # Выделить id товара
                catalog_id = request.POST.dict().get("catalog_id")
                #print("catalog_id ", catalog_id)
                price = request.POST.dict().get("price")
                #print("price ", price)
                user = request.POST.dict().get("user")
                #print("user ", user)
                # Отправить товар в корзину
                basket = Basket()
                basket.catalog_id = catalog_id
                try:
                    basket.price = float(int(price.replace(",00","")))
                except:
                    basket.price = price
                basket.user_id = user
                basket.save()
                message = _('Item added to basket')
                basket_count = Basket.objects.filter(user_id=_user_id).count()
                return render(request, "catalog/list.html", {"catalog": catalog, "category": category, "author": author, "mess": message, "basket_count": basket_count, "basket_total": basket_total, })         

        else:
            return render(request, "catalog/list.html", {"catalog": catalog, "category": category, "author": author, "basket_count": basket_count, "basket_total": basket_total,})            
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def catalog_create(request, invoice_id):
    try:
        if request.method == "POST":
            catalog = Catalog()
            catalog.invoice_id = invoice_id
            catalog.category = Category.objects.filter(id=request.POST.get("category")).first()
            catalog.author = Author.objects.filter(id=request.POST.get("author")).first()
            catalog.catalog_title = request.POST.get("catalog_title")
            catalog.details = request.POST.get("details")        
            catalog.price = request.POST.get("price")
            catalog.quantity = request.POST.get("quantity")
            catalog.unit = request.POST.get("unit")
            if "photo" in request.FILES:                
                catalog.photo = request.FILES["photo"]
            catalogform = CatalogForm(request.POST)
            if catalogform.is_valid():
                catalog.save()
                return HttpResponseRedirect(reverse('catalog_index', args=(invoice_id,)))
            else:
                return render(request, "catalog/create.html", {"form": catalogform})
        else:        
            catalogform = CatalogForm()
            return render(request, "catalog/create.html", {"form": catalogform, "invoice_id": invoice_id})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def catalog_edit(request, id, invoice_id):
    try:
        catalog = Catalog.objects.get(id=id) 
        if request.method == "POST":
            catalog.category = Category.objects.filter(id=request.POST.get("category")).first()
            catalog.author = Author.objects.filter(id=request.POST.get("author")).first()
            catalog.catalog_title = request.POST.get("catalog_title")
            catalog.details = request.POST.get("details")        
            catalog.price = request.POST.get("price")
            catalog.quantity = request.POST.get("quantity")
            catalog.unit = request.POST.get("unit")
            if "photo" in request.FILES:                
                catalog.photo = request.FILES["photo"]
            catalogform = CatalogForm(request.POST)
            if catalogform.is_valid():
                catalog.save()
                return HttpResponseRedirect(reverse('catalog_index', args=(invoice_id,)))
            else:
                return render(request, "catalog/edit.html", {"form": catalogform, "invoice_id": invoice_id}) 
        else:
            # Загрузка начальных данных
            catalogform = CatalogForm(initial={'category': catalog.category, 'author': catalog.author, 'catalog_title': catalog.catalog_title, 'details': catalog.details, 'price': catalog.price, 'quantity': catalog.quantity, 'unit': catalog.unit, 'photo': catalog.photo })
            #print('->',catalog.photo )
            return render(request, "catalog/edit.html", {"form": catalogform, "invoice_id": invoice_id})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def catalog_delete(request, id, invoice_id):
    try:
        catalog = Catalog.objects.get(id=id)
        catalog.delete()
        return HttpResponseRedirect(reverse('catalog_index', args=(invoice_id,)))
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы с информацией о товаре для менеджера.
@login_required
@group_required("Managers")
def catalog_read(request, id, invoice_id):
    try:
        catalog = ViewCatalog.objects.get(id=id) 
        return render(request, "catalog/read.html", {"catalog": catalog, "invoice_id": invoice_id})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы с информацией о товаре для клиента
#@login_required
def catalog_details(request, id):
    try:
        # Товар с каталога
        catalog = ViewCatalog.objects.get(id=id)
        # Отзывы на данный товар
        review = ViewSale.objects.filter(catalog_id=id).order_by('-saleday')
        return render(request, "catalog/details.html", {"catalog": catalog, "review": review, })
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")

###################################################################################################

# Количество товара в корзине и общая стоимость товарв в корзине для пользователя _user_id
def basket_count_total(_id):
    try:
        # Количество товара в корзине и общая стоимость товарв в корзине для пользователя _user_id
        count = 0        
        total = 0
        # Текущий пользователь _user_id
        # Доступны записи только текущего пользователя
        basket = Basket.objects.filter(user_id=_id)
        # Подсчитать стоимость товара в корзине
        if basket.count() > 0:
            count = basket.count()
            for b in basket:
                total = total + b.price*b.quantity
        print(count)        
        print(total)        
        return count, total
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Корзина
@login_required
def basket(request):
    try:
        # Текущий пользователь
        _user_id = request.user.id
        # Доступны записи только текущего пользователя
        basket = Basket.objects.filter(user_id=_user_id).order_by('basketday')
        # Количество товара в корзине и общая стоимость товарв в корзине для пользователя _user_id
        basket_count, basket_total = basket_count_total(_user_id)   
        print(basket_count)
        print(basket_total)
        # Узнать последний адрес доставки, если его нет то самовывоз
        address = Sale.objects.filter(user_id=_user_id).values_list('address').order_by('-saleday')
        print(address)
        print(address.count())
        if address.count() != 0:
            #print(address[0][0])
            address = address[0][0]
        else:
            address = _('pickup')
        #print(total)        
        # Если это подтверждение какого-либо действия
        if request.method == "POST":        
            # Увеличение или уменьшение количества товара в корзине
            if ('btn_plus' in request.POST) or ('btn_minus' in request.POST):
                # Выделить id записи в корзине и количество товара       
                basket_id = request.POST.dict().get("basket_id")
                quantity = request.POST.dict().get("quantity")
                # Найти запись в корзине
                basket = Basket.objects.get(id=basket_id)
                # Изменить запись в корзине
                if 'btn_plus' in request.POST:
                    basket.quantity = basket.quantity + 1
                if 'btn_minus' in request.POST:
                    if basket.quantity > 1:
                        basket.quantity = basket.quantity - 1
                # Сохранить
                basket.save()
                # Доступны записи только текущего пользователя
                basket = Basket.objects.filter(user_id=_user_id).order_by('basketday')
                # Подсчитать количество и стоимость товара в корзине
                basket_count, basket_total = basket_count_total(_user_id)        
                return render(request, "catalog/basket.html", {"basket": basket,  "basket_count": basket_count, "basket_total": basket_total, "address": address})
            # Приобретение, если нажата кнопка Buy
            if 'buy' in request.POST:
                # Перебрать всю корзину отправить ее в продажи!
                for b in basket:
                    # Добавить в продажи
                    sale = Sale()
                    sale.catalog_id = b.catalog_id
                    sale.price = b.price
                    sale.quantity = b.quantity
                    sale.user_id = b.user_id
                    sale.address = request.POST.get('address')
                    sale.details = ""
                    #print("Сохранено")
                    sale.save()
                # Очистить корзину
                #print("Корзина очищена")
                basket.delete()
                # отправка сообщения
                #print("Подготовка сообщения")
                #send_mail(
                #    "Заявка #" + str(sale.id),
                #    str(sale.saleday.strftime('%d.%m.%Y %H:%M:%S')) + "\n" + str(sale.catalog.category)+ "\n" + str(sale.catalog.catalog_title) + "\n" + _('price') + ":"  + str(sale.price) + "\n" + _('quantity') + ":" + str(sale.quantity) + "\n" + str(sale.user.first_name) + " " + str(sale.user.last_name) + "\n" + str(sale.address) + "\n" + str(sale.details),
                #    "shop260222@mail.ru",
                #    ["shop260222@mail.ru", "user538542@mail.ru"],
                #    fail_silently=True,
                #)
                #print("Сообщение отправленно")

                # Перейти к совершенным покупкам
                return HttpResponseRedirect(reverse("buy"))
        else:
            return render(request, "catalog/basket.html", {"basket": basket, "basket_count": basket_count, "basket_total": basket_total, "address": address})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление из корзины
@login_required
def basket_delete(request, id):
    try:
        basket = Basket.objects.get(id=id)                
        basket.delete()
        # Текущий пользователь
        _user_id = request.user.id
        # Доступны записи только текущего пользователя
        basket = Basket.objects.filter(user_id=_user_id).order_by('basketday')
        # Подсчитать стоимость товара в корзине
        basket_total = 0
        for b in basket:
            basket_total = basket_total + b.price*b.quantity    
        return render(request, "catalog/basket.html", {"basket": basket, "basket_total": basket_total})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Basket not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)
    
# Список приобретения + Оставление отзыва
@login_required
def buy(request):
    try:
        # Текущий пользователь
        # Текущий пользователь
        _user_id = request.user.id
        # Доступны записи только текущего пользователя
        basket = Basket.objects.filter(user_id=_user_id).order_by('basketday')
        # Количество товара в корзине и общая стоимость товарв в корзине для пользователя _user_id
        basket_count, basket_total = basket_count_total(_user_id)  
        # Доступны записи только текущего пользователя
        sale = ViewSale.objects.filter(user_id=_user_id).order_by('-saleday')  
        return render(request, "catalog/buy.html", {"sale": sale, "basket_count": basket_count, "basket_total": basket_total})        
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################
    
# Список продаж с указанием последнего движения в доставке
@login_required
def delivery_list(request):    
    if request.user.groups.filter(name='Managers').exists():
        view_sale = ViewSale.objects.all().order_by('-saleday')        
    else:
        _user_id = request.user.id
        view_sale = ViewSale.objects.filter(user_id=_user_id).order_by('-saleday')        
    return render(request, "delivery/list.html", {"view_sale": view_sale})
    
# Список для изменения с кнопками создать, изменить, удалить для конкретной доставки
@login_required
def delivery_index(request, id):
    try:
        delivery = Delivery.objects.filter(sale_id=id)
        view_sale = ViewSale.objects.get(id=id)
        return render(request, "delivery/index.html", {"delivery": delivery, "view_sale": view_sale})
    except Delivery.DoesNotExist:
        return HttpResponseNotFound("<h2>Delivery not found</h2>")

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def delivery_create(request, sale_id):
    try:
        if request.method == "POST":
            delivery = Delivery()
            delivery.sale_id = sale_id
            delivery.deliveryday = request.POST.get("deliveryday")
            delivery.movement = request.POST.get("movement")
            delivery.details = request.POST.get("details")
            deliveryform = DeliveryForm(request.POST)
            if deliveryform.is_valid():
                delivery.save()
                return HttpResponseRedirect(reverse('delivery_index', args=(delivery.sale_id,)))
            else:
                return render(request, "delivery/create.html", {"form": deliveryform})
        else:
            deliveryform = DeliveryForm()
            return render(request, "delivery/create.html/", {"form": deliveryform, 'sale_id': sale_id,})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
@group_required("Managers")
def delivery_edit(request, id):
    try:
        delivery = Delivery.objects.get(id=id) 
        if request.method == "POST":
            delivery.movement = request.POST.get("movement")
            delivery.details = request.POST.get("details")
            deliveryform = DeliveryForm(request.POST)
            if deliveryform.is_valid():
                delivery.save()
                return HttpResponseRedirect(reverse('delivery_index', args=(delivery.sale_id,)))
            else:
                return render(request, "delivery/edit.html", {"form": deliveryform})
        else:
            # Загрузка начальных данных
            deliveryform = DeliveryForm(initial={'sale': delivery.sale, 'deliveryday': delivery.deliveryday, 'movement': delivery.movement, 'details': delivery.details,})
            return render(request, "delivery/edit.html", {"form": deliveryform, 'sale_id': delivery.sale_id, })
    except Delivery.DoesNotExist:
        return HttpResponseNotFound("<h2>Delivery not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def delivery_delete(request, id):
    try:
        delivery = Delivery.objects.get(id=id)
        delivery.delete()
        return HttpResponseRedirect(reverse('delivery_index', args=(delivery.sale_id,)))
    except Delivery.DoesNotExist:
        return HttpResponseNotFound("<h2>Delivery not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
@login_required
def delivery_read(request, id):
    try:
        delivery = Delivery.objects.get(id=id) 
        return render(request, "delivery/read.html", {"delivery": delivery, "sale_id": delivery.sale_id})
    except Catalog.DoesNotExist:
        return HttpResponseNotFound("<h2>Catalog not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)


###################################################################################################

# Список для просмотра с кнопкой удалить
@login_required
@group_required("Managers")
def review_index(request):
    try:
        review = ViewSale.objects.exclude(rating=None).order_by('saleday') 
        if request.method == "POST":
            # Выделить id sale
            sale_id = request.POST.dict().get("sale_id")
            print("sale_id ", sale_id)
            # Удалить отзывы
            sale = Sale.objects.get(id=sale_id) 
            sale.rating = None
            sale.details = None
            sale.save()        
        return render(request, "review/index.html", {"review": review})        
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
@login_required
def review_edit(request, id):
    try:
        review = Sale.objects.get(id=id)
        if request.method == "POST":
            review.rating = request.POST.get("rating")
            review.details = request.POST.get("details")
            reviewform = ReviewForm(request.POST)
            if reviewform.is_valid():
                review.save()
                return HttpResponseRedirect(reverse('buy'))
            else:
                return render(request, "review/edit.html", {"form": reviewform})
        else:
            # Загрузка начальных данных
            reviewform = ReviewForm(initial={'rating': review.rating, 'details': review.details, })
            return render(request, "review/edit.html", {"form": reviewform})
    except Sale.DoesNotExist:
        return HttpResponseNotFound("<h2>Sale not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Список для изменения с кнопками создать, изменить, удалить
@login_required
@group_required("Managers")
def news_index(request):
    try:
        news = News.objects.all().order_by('-daten')
        return render(request, "news/index.html", {"news": news})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Список для просмотра
def news_list(request):
    try:
        news = News.objects.all().order_by('-daten')
        if request.method == "POST":
            # Определить какая кнопка нажата
            if 'searchBtn' in request.POST:
                # Поиск по названию 
                news_search = request.POST.get("news_search")
                #print(news_search)                
                if news_search != '':
                    news = news.filter(Q(title__contains = news_search) | Q(details__contains = news_search)).all()                
                return render(request, "news/list.html", {"news": news, "news_search": news_search, })    
            else:          
                return render(request, "news/list.html", {"news": news})                 
        else:
            return render(request, "news/list.html", {"news": news}) 
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# В функции create() получаем данные из запроса типа POST, сохраняем данные с помощью метода save()
# и выполняем переадресацию на корень веб-сайта (то есть на функцию index).
@login_required
@group_required("Managers")
def news_create(request):
    try:
        if request.method == "POST":
            news = News()        
            news.daten = request.POST.get("daten")
            news.news_title = request.POST.get("news_title")
            news.details = request.POST.get("details")
            if 'photo' in request.FILES:                
                news.photo = request.FILES['photo']   
            newsform = NewsForm(request.POST)
            if newsform.is_valid():
                news.save()
                return HttpResponseRedirect(reverse('news_index'))
            else:
                return render(request, "news/create.html", {"form": newsform})
        else:        
            newsform = NewsForm(initial={'daten': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), })
            return render(request, "news/create.html", {"form": newsform})
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Функция edit выполняет редактирование объекта.
# Функция в качестве параметра принимает идентификатор объекта в базе данных.
@login_required
@group_required("Managers")
def news_edit(request, id):
    try:
        news = News.objects.get(id=id) 
        if request.method == "POST":
            news.daten = request.POST.get("daten")
            news.news_title = request.POST.get("news_title")
            news.details = request.POST.get("details")
            if "photo" in request.FILES:                
                news.photo = request.FILES["photo"]
            newsform = NewsForm(request.POST)
            if newsform.is_valid():
                news.save()
                return HttpResponseRedirect(reverse('news_index'))
            else:
                return render(request, "news/edit.html", {"form": newsform})
        else:
            # Загрузка начальных данных
            newsform = NewsForm(initial={'daten': news.daten.strftime('%Y-%m-%d %H:%M:%S'), 'news_title': news.news_title, 'details': news.details, 'photo': news.photo })
            return render(request, "news/edit.html", {"form": newsform})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Удаление данных из бд
# Функция delete аналогичным функции edit образом находит объет и выполняет его удаление.
@login_required
@group_required("Managers")
def news_delete(request, id):
    try:
        news = News.objects.get(id=id)
        news.delete()
        return HttpResponseRedirect(reverse('news_index'))
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

# Просмотр страницы read.html для просмотра объекта.
#@login_required
def news_read(request, id):
    try:
        news = News.objects.get(id=id) 
        return render(request, "news/read.html", {"news": news})
    except News.DoesNotExist:
        return HttpResponseNotFound("<h2>News not found</h2>")
    except Exception as exception:
        print(exception)
        return HttpResponse(exception)

###################################################################################################

# Регистрационная форма 
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')
            #return render(request, 'registration/register_done.html', {'new_user': user})
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# Изменение данных пользователя
@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'registration/my_account.html'
    success_url = reverse_lazy('index')
    #success_url = reverse_lazy('my_account')
    def get_object(self):
        return self.request.user

# Выход
from django.contrib.auth import logout
def logoutUser(request):
    logout(request)
    return render(request, "index.html")

