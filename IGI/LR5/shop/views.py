import calendar
import logging
from decimal import Decimal
from statistics import StatisticsError, mean, median, mode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import BuyProductForm, ProductForm, RegisterForm, ReviewForm, SupplierForm, SupplyPurchaseForm
from .models import (
    Article,
    Category,
    CompanyInfo,
    Customer,
    Employee,
    FAQ,
    PickupPoint,
    Product,
    PromoCode,
    Review,
    Sale,
    SaleItem,
    Supplier,
    SupplyPurchase,
    Vacancy,
)
from .services import fetch_pet_api_highlights

logger = logging.getLogger(__name__)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


def home(request):
    latest_article = Article.objects.order_by("-published_at").first()
    products = Product.objects.select_related("category").order_by("name")[:6]
    return render(request, "shop/home.html", {"latest_article": latest_article, "products": products})


def about(request):
    company = CompanyInfo.objects.order_by("-updated_at").first()
    return render(request, "shop/about.html", {"company": company})


class NewsListView(ListView):
    model = Article
    template_name = "shop/news.html"
    context_object_name = "articles"
    paginate_by = 10


class ArticleDetailView(DetailView):
    model = Article
    template_name = "shop/article_detail.html"
    context_object_name = "article"


def faq(request):
    return render(request, "shop/faq.html", {"items": FAQ.objects.all()})


def contacts(request):
    return render(request, "shop/contacts.html", {"employees": Employee.objects.all()})


def privacy(request):
    return render(request, "shop/privacy.html")


def vacancies(request):
    return render(request, "shop/vacancies.html", {"vacancies": Vacancy.objects.all()})


def promo_codes(request):
    return render(request, "shop/promos.html", {"promos": PromoCode.objects.all()})


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.select_related("category").prefetch_related("suppliers")
        query = self.request.GET.get("q", "").strip()
        category_id = self.request.GET.get("category")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sort = self.request.GET.get("sort", "name")

        if query:
            queryset = queryset.filter(name__icontains=query) | queryset.filter(sku__icontains=query)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if sort in {"name", "-name", "price", "-price", "sku"}:
            queryset = queryset.order_by(sort)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["query"] = self.request.GET
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"


class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "shop/form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s created product %s",
            self.request.user.username,
            self.object.sku,
        )
        return response


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "shop/form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s updated product %s",
            self.request.user.username,
            self.object.sku,
        )
        return response


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "shop/confirm_delete.html"
    success_url = reverse_lazy("products")

    def form_valid(self, form):
        sku = self.object.sku
        response = super().form_valid(form)
        logger.warning("Staff user %s deleted product %s", self.request.user.username, sku)
        return response


class SupplierListView(StaffRequiredMixin, ListView):
    model = Supplier
    template_name = "shop/supplier_list.html"
    context_object_name = "suppliers"


class SupplierCreateView(StaffRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "shop/form.html"
    success_url = reverse_lazy("suppliers")

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s created supplier %s",
            self.request.user.username,
            self.object.name,
        )
        return response


class SupplierUpdateView(StaffRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "shop/form.html"
    success_url = reverse_lazy("suppliers")

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s updated supplier %s",
            self.request.user.username,
            self.object.name,
        )
        return response


class SupplierDeleteView(StaffRequiredMixin, DeleteView):
    model = Supplier
    template_name = "shop/confirm_delete.html"
    success_url = reverse_lazy("suppliers")

    def form_valid(self, form):
        supplier_name = self.object.name
        response = super().form_valid(form)
        logger.warning(
            "Staff user %s deleted supplier %s",
            self.request.user.username,
            supplier_name,
        )
        return response


class PurchaseListView(StaffRequiredMixin, ListView):
    model = SupplyPurchase
    template_name = "shop/purchase_list.html"
    context_object_name = "purchases"


class PurchaseCreateView(StaffRequiredMixin, CreateView):
    model = SupplyPurchase
    form_class = SupplyPurchaseForm
    template_name = "shop/form.html"
    success_url = reverse_lazy("purchases")

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s created purchase %s for product %s quantity %s",
            self.request.user.username,
            self.object.pk,
            self.object.supplier_product.product.sku,
            self.object.quantity,
        )
        return response


class PurchaseUpdateView(StaffRequiredMixin, UpdateView):
    model = SupplyPurchase
    form_class = SupplyPurchaseForm
    template_name = "shop/form.html"
    success_url = reverse_lazy("purchases")

    def form_valid(self, form):
        response = super().form_valid(form)
        logger.info(
            "Staff user %s updated purchase %s for product %s quantity %s",
            self.request.user.username,
            self.object.pk,
            self.object.supplier_product.product.sku,
            self.object.quantity,
        )
        return response


class PurchaseDeleteView(StaffRequiredMixin, DeleteView):
    model = SupplyPurchase
    template_name = "shop/confirm_delete.html"
    success_url = reverse_lazy("purchases")

    def form_valid(self, form):
        purchase_id = self.object.pk
        product_sku = self.object.supplier_product.product.sku
        quantity = self.object.quantity
        response = super().form_valid(form)
        logger.warning(
            "Staff user %s deleted purchase %s for product %s quantity %s",
            self.request.user.username,
            purchase_id,
            product_sku,
            quantity,
        )
        return response


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info("Registered new customer user %s", user.username)
            messages.success(request, "Регистрация выполнена.")
            return redirect("account")
        logger.warning(
            "Failed registration attempt for username %s",
            request.POST.get("username", ""),
        )
    else:
        form = RegisterForm()
    return render(request, "shop/register.html", {"form": form})


@login_required
def account(request):
    customer = getattr(request.user, "customer_profile", None)
    employee = getattr(request.user, "employee_profile", None)
    sales = Sale.objects.filter(customer=customer).prefetch_related("items__product") if customer else []
    pickups = PickupPoint.objects.all()
    return render(
        request,
        "shop/account.html",
        {"customer": customer, "employee": employee, "sales": sales, "pickups": pickups},
    )


def reviews(request):
    return render(request, "shop/reviews.html", {"reviews": Review.objects.all()})


@login_required
def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.name = request.user.get_full_name() or request.user.username
            review.save()
            logger.info(
                "User %s added review %s with rating %s",
                request.user.username,
                review.pk,
                review.rating,
            )
            messages.success(request, "Отзыв добавлен.")
            return redirect("reviews")
        logger.warning("User %s submitted invalid review form", request.user.username)
    else:
        form = ReviewForm()
    return render(request, "shop/form.html", {"form": form, "title": "Добавить отзыв"})


@login_required
def buy_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    customer = getattr(request.user, "customer_profile", None)
    if not customer:
        logger.warning(
            "User %s tried to buy product %s without customer profile",
            request.user.username,
            product.sku,
        )
        messages.error(request, "Для покупки заполните профиль постоянного клиента.")
        return redirect("account")
    if request.method == "POST":
        form = BuyProductForm(request.POST, product=product)
        if form.is_valid():
            promo_code = form.cleaned_data["promo_code"]
            sale = Sale.objects.create(customer=customer, promo_code=promo_code)
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=form.cleaned_data["quantity"],
                unit_price=product.price,
            )
            if promo_code:
                logger.info(
                    "User %s bought product %s quantity %s with promo %s",
                    request.user.username,
                    product.sku,
                    form.cleaned_data["quantity"],
                    promo_code.code,
                )
            else:
                logger.info(
                    "User %s bought product %s quantity %s without promo",
                    request.user.username,
                    product.sku,
                    form.cleaned_data["quantity"],
                )
            if promo_code:
                messages.success(
                    request,
                    f"Покупка сохранена. Применен промокод {promo_code.code}.",
                )
            else:
                messages.success(request, "Покупка сохранена в личном кабинете.")
            return redirect("account")
        logger.warning(
            "User %s failed to buy product %s: %s",
            request.user.username,
            product.sku,
            form.errors.as_text(),
        )
    else:
        form = BuyProductForm(product=product)
    return render(request, "shop/buy_product.html", {"form": form, "product": product})


@login_required
def statistics_view(request):
    sale_totals = [sale.total_amount for sale in Sale.objects.prefetch_related("items", "promo_code")]
    numeric_totals = [float(total) for total in sale_totals]
    total_revenue = sum(sale_totals, Decimal("0.00"))
    try:
        sales_mode = mode(numeric_totals) if numeric_totals else 0
    except StatisticsError:
        sales_mode = "нет единственной моды"

    categories = (
        Category.objects.annotate(
            sold_units=Sum("products__sale_items__quantity"),
            revenue=Sum(F("products__sale_items__quantity") * F("products__sale_items__unit_price")),
        )
        .order_by("-sold_units")
        .values("name", "sold_units", "revenue")
    )
    chart_items = [
        {"label": item["name"], "value": item["sold_units"] or 0}
        for item in categories
    ]
    now_local = timezone.localtime()
    now_utc = timezone.now()
    text_calendar = calendar.TextCalendar(firstweekday=0).formatmonth(now_local.year, now_local.month)

    context = {
        "products": Product.objects.order_by("name"),
        "total_revenue": total_revenue,
        "mean_total": mean(numeric_totals) if numeric_totals else 0,
        "median_total": median(numeric_totals) if numeric_totals else 0,
        "mode_total": sales_mode,
        "popular_category": categories[0] if chart_items else None,
        "profitable_category": sorted(categories, key=lambda x: x["revenue"] or 0, reverse=True)[0]
        if chart_items
        else None,
        "chart_items": chart_items,
        "timezone_name": timezone.get_current_timezone_name(),
        "now_local": now_local,
        "now_utc": now_utc,
        "calendar": text_calendar,
    }
    return render(request, "shop/statistics.html", context)


def external_apis(request):
    return render(request, "shop/external_apis.html", fetch_pet_api_highlights())


@require_GET
@login_required
def products_api(request):
    logger.info("User %s requested products API", request.user.username)
    products = Product.objects.select_related("category").values("sku", "name", "price", "category__name")
    return JsonResponse({"products": list(products)})


@require_GET
@login_required
def sales_api(request):
    logger.info("User %s requested sales API", request.user.username)
    if request.user.is_staff:
        sales = Sale.objects.all()
    else:
        customer = getattr(request.user, "customer_profile", None)
        sales = Sale.objects.filter(customer=customer) if customer else Sale.objects.none()
    data = [
        {
            "id": sale.id,
            "date": sale.sale_date.strftime("%d/%m/%Y"),
            "total": str(sale.total_amount),
        }
        for sale in sales.prefetch_related("items")
    ]
    return JsonResponse({"sales": data})
