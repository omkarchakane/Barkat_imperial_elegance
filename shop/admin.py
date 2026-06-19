from calendar import month_abbr
from math import ceil
from types import MethodType

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth
from django.utils import timezone

from .models import Product,Cart,Review,UserRegister,OfferPoster,ProductImage,Wishlist,Order,OrderItem


admin.site.site_header = 'Barkat'
admin.site.site_title = 'Barkat'
admin.site.index_title = 'Barkat Dashboard'
admin.site.index_template = 'admin/index.html'


def _format_indian_currency(value):
    value = int(value or 0)
    prefix = '-' if value < 0 else ''
    amount = str(abs(value))

    if len(amount) > 3:
        last_three = amount[-3:]
        remaining = amount[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        amount = ','.join(groups + [last_three])

    return f'\u20b9 {prefix}{amount}'


def _percent_change(current, previous):
    current = current or 0
    previous = previous or 0

    if previous == 0:
        return 100 if current else 0

    return round(((current - previous) / previous) * 100, 1)


def _image_url(file_field):
    if not file_field:
        return ''

    try:
        return file_field.url
    except ValueError:
        return ''


def _sales_chart_context():
    today = timezone.localdate()
    monthly_totals = {month: 0 for month in range(1, 13)}
    rows = (
        Order.objects
        .filter(order_date__year=today.year)
        .annotate(month=ExtractMonth('order_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
    )

    for row in rows:
        monthly_totals[row['month']] = row['total'] or 0

    values = [monthly_totals[month] for month in range(1, 13)]
    if not any(values):
        values = [9000, 13500, 21000, 26000, 17000, 19500, 31500, 24000, 26500, 34500, 42000, 25000]

    max_value = max(50000, ceil(max(values) / 10000) * 10000)
    chart_top = 34
    chart_bottom = 226
    chart_left = 50
    chart_width = 586
    step = chart_width / 11

    points = []
    for index, value in enumerate(values):
        x = chart_left + (index * step)
        y = chart_bottom - ((value / max_value) * (chart_bottom - chart_top))
        bar_percent = max(8, (float(value) / float(max_value)) * 100) if max_value else 8
        points.append({
            'label': month_abbr[index + 1],
            'amount': _format_indian_currency(value),
            'value': value,
            'percent': f'{bar_percent:.1f}',
            'x': f'{x:.1f}',
            'y': f'{y:.1f}',
        })

    revenue_trend_values = []
    running_total = 0
    for value in values:
        running_total += value
        revenue_trend_values.append(running_total)

    line_path = 'M ' + ' L '.join(f"{point['x']},{point['y']}" for point in points)
    area_path = f"{line_path} L {points[-1]['x']},{chart_bottom} L {points[0]['x']},{chart_bottom} Z"
    y_axis = []
    for index in range(6):
        ratio = index / 5
        value = max_value - (max_value * ratio)
        y = chart_top + ((chart_bottom - chart_top) * ratio)
        y_axis.append({
            'label': '0' if value == 0 else f'{int(value / 1000)}K',
            'y': f'{y:.1f}',
        })

    return {
        'sales_line_path': line_path,
        'sales_area_path': area_path,
        'sales_points': points,
        'sales_y_axis': y_axis,
        'sales_year': today.year,
        'sales_chart_labels': [point['label'] for point in points],
        'sales_chart_values': values,
        'revenue_trend_values': revenue_trend_values,
    }


def _category_distribution(total_products):
    colors = ['#9b143d', '#d9a441', '#74569b', '#ef4b83', '#38aaa2']
    rows = list(
        Product.objects
        .exclude(fabric__isnull=True)
        .exclude(fabric__exact='')
        .values('fabric')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    if not rows and total_products:
        rows = [{'fabric': 'Unspecified Sarees', 'count': total_products}]

    top_rows = rows[:4]
    other_count = sum(row['count'] for row in rows[4:])
    if other_count:
        top_rows.append({'fabric': 'Others', 'count': other_count})

    categories = []
    gradient_parts = []
    current = 0
    total_count = sum(row['count'] for row in top_rows) or 1

    for index, row in enumerate(top_rows):
        percent = round((row['count'] / total_count) * 100)
        end = 100 if index == len(top_rows) - 1 else current + percent
        color = colors[index % len(colors)]
        name = row['fabric']
        if name != 'Others' and 'saree' not in name.lower():
            name = f'{name} Sarees'

        categories.append({
            'name': name,
            'count': row['count'],
            'percent': percent,
            'color': color,
        })
        gradient_parts.append(f'{color} {current}% {end}%')
        current = end

    if not categories:
        categories.append({
            'name': 'No products yet',
            'count': 0,
            'percent': 100,
            'color': '#e5e7eb',
        })
        gradient_parts.append('#e5e7eb 0% 100%')

    return {
        'categories': categories,
        'category_gradient': ', '.join(gradient_parts),
        'category_chart_labels': [category['name'] for category in categories],
        'category_chart_values': [category['count'] for category in categories],
        'category_chart_colors': [category['color'] for category in categories],
    }


def _top_products():
    sold_rows = list(
        OrderItem.objects
        .values('product')
        .annotate(units_sold=Sum('quantity'))
        .order_by('-units_sold')[:5]
    )
    products_by_id = Product.objects.in_bulk([row['product'] for row in sold_rows])
    products = []

    for rank, row in enumerate(sold_rows, start=1):
        product = products_by_id.get(row['product'])
        if not product:
            continue
        products.append({
            'rank': rank,
            'name': product.name,
            'price': _format_indian_currency(product.price),
            'sold': row['units_sold'] or 0,
            'image_url': _image_url(product.image),
        })

    if products:
        return products

    for rank, product in enumerate(Product.objects.all().order_by('name')[:5], start=1):
        products.append({
            'rank': rank,
            'name': product.name,
            'price': _format_indian_currency(product.price),
            'sold': 0,
            'image_url': _image_url(product.image),
        })

    return products


def _inventory_status():
    products = []
    for product in Product.objects.all().order_by('-is_new_arrival', 'name')[:5]:
        products.append({
            'name': product.name,
            'price': _format_indian_currency(product.price),
            'status': 'New Arrival' if product.is_new_arrival else 'In Catalog',
            'status_class': 'warning' if product.is_new_arrival else 'success',
        })

    return products


def _order_status_summary(total_orders):
    colors = {
        'pending': '#f59e0b',
        'confirmed': '#8b5cf6',
        'shipped': '#2563eb',
        'delivered': '#16a34a',
        'cancelled': '#e11d48',
    }
    counts = dict(
        Order.objects
        .values('status')
        .annotate(count=Count('id'))
        .values_list('status', 'count')
    )
    summary = []

    for status, label in Order.ORDER_STATUS_CHOICES:
        count = counts.get(status, 0)
        summary.append({
            'status': status,
            'label': label,
            'count': count,
            'percent': round((count / total_orders) * 100) if total_orders else 0,
            'color': colors.get(status, '#9ca3af'),
        })

    return summary


def _admin_dashboard_context():
    now = timezone.now()
    today = timezone.localdate()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if current_month_start.month == 1:
        previous_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
    else:
        previous_month_start = current_month_start.replace(month=current_month_start.month - 1)

    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = Order.objects.count()
    total_customers = UserRegister.objects.count()
    total_products = Product.objects.count()
    total_reviews = Review.objects.count()
    total_wishlist = Wishlist.objects.count()
    current_revenue = (
        Order.objects
        .filter(order_date__gte=current_month_start)
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )
    previous_revenue = (
        Order.objects
        .filter(order_date__gte=previous_month_start, order_date__lt=current_month_start)
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )
    current_orders = Order.objects.filter(order_date__gte=current_month_start).count()
    previous_orders = Order.objects.filter(
        order_date__gte=previous_month_start,
        order_date__lt=current_month_start,
    ).count()
    today_orders = Order.objects.filter(order_date__date=today).count()
    today_revenue = (
        Order.objects
        .filter(order_date__date=today)
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )
    pending_orders = Order.objects.filter(status='pending').count()

    recent_orders = list(Order.objects.order_by('-order_date')[:5])
    for order in recent_orders:
        order.display_id = f'#ORD{order.id:04d}'
        order.customer_name = f'{order.first_name} {order.last_name}'.strip() or order.username
        order.formatted_total = _format_indian_currency(order.total_amount)
        order.status_class = order.status

    dashboard_context = {
        'dashboard_cards': [
            {
                'label': 'Total Revenue',
                'value': _format_indian_currency(total_revenue),
                'delta': _percent_change(current_revenue, previous_revenue),
                'hint': 'vs last month',
                'icon': 'fa-indian-rupee-sign',
                'theme': 'rose',
                'sparkline': 'M2 31 L24 38 L48 36 L72 27 L96 29 L120 23 L144 35 L168 39 L192 34 L216 40 L240 31 L264 21 L288 23 L312 18 L336 20 L360 28 L384 22',
            },
            {
                'label': 'Total Orders',
                'value': f'{total_orders:,}',
                'delta': _percent_change(current_orders, previous_orders),
                'hint': 'vs last month',
                'icon': 'fa-bag-shopping',
                'theme': 'gold',
                'sparkline': 'M2 34 L24 22 L48 28 L72 33 L96 32 L120 29 L144 35 L168 42 L192 31 L216 24 L240 30 L264 38 L288 32 L312 34 L336 28 L360 21 L384 25',
            },
            {
                'label': 'Customers',
                'value': f'{total_customers:,}',
                'delta': 0,
                'hint': 'registered users',
                'icon': 'fa-users',
                'theme': 'purple',
                'sparkline': 'M2 39 L24 29 L48 32 L72 33 L96 27 L120 28 L144 26 L168 30 L192 38 L216 29 L240 32 L264 27 L288 28 L312 34 L336 29 L360 30 L384 22',
            },
            {
                'label': 'Products',
                'value': f'{total_products:,}',
                'delta': 0,
                'hint': 'active catalog',
                'icon': 'fa-box-open',
                'theme': 'coral',
                'sparkline': 'M2 28 L24 35 L48 37 L72 33 L96 27 L120 32 L144 24 L168 21 L192 34 L216 32 L240 41 L264 35 L288 42 L312 32 L336 36 L360 29 L384 20',
            },
        ],
        'quick_insights': [
            {'label': 'Today Revenue', 'value': _format_indian_currency(today_revenue), 'detail': f'{today_orders} orders today'},
            {'label': 'Pending Orders', 'value': f'{pending_orders:,}', 'detail': 'Need attention'},
            {'label': 'Wishlist Saves', 'value': f'{total_wishlist:,}', 'detail': 'Customer interest'},
            {'label': 'Reviews', 'value': f'{total_reviews:,}', 'detail': 'Product feedback'},
        ],
        'recent_orders': recent_orders,
        'top_products': _top_products(),
        'inventory_products': _inventory_status(),
        'order_status_summary': _order_status_summary(total_orders),
        'pending_orders': pending_orders,
        'total_products': total_products,
    }
    sales_context = _sales_chart_context()
    category_context = _category_distribution(total_products)
    dashboard_context.update(sales_context)
    dashboard_context.update(category_context)
    dashboard_context['admin_chart_data'] = {
        'salesLabels': sales_context['sales_chart_labels'],
        'monthlySales': sales_context['sales_chart_values'],
        'revenueTrends': sales_context['revenue_trend_values'],
        'categoryLabels': category_context['category_chart_labels'],
        'categoryValues': category_context['category_chart_values'],
        'categoryColors': category_context['category_chart_colors'],
    }

    return dashboard_context


def _custom_admin_index(self, request, extra_context=None):
    extra_context = extra_context or {}
    extra_context.update(_admin_dashboard_context())
    return AdminSite.index(self, request, extra_context=extra_context)


admin.site.index = MethodType(_custom_admin_index, admin.site)

# Register your models here.
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','is_new_arrival','offer_text','fabric','color','work')
    list_filter = ('is_new_arrival','fabric','color','work')
    search_fields = ('name','description','fabric','color')
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('name','price','image','description')
        }),
        ('Saree Details', {
            'fields': ('fabric','color','work','occasion','length','blouse_piece')
        }),
        ('Additional Info', {
            'fields': ('wash_care','shipping_info','is_new_arrival','offer_text')
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('username','product','quantity')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('username','product','rating','created_at')
    list_filter = ('rating',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('username','product','added_at')

@admin.register(UserRegister)
class UserRegisterAdmin(admin.ModelAdmin):
    list_display = ('email','name')

@admin.register(OfferPoster)
class OfferPosterAdmin(admin.ModelAdmin):
    list_display = ('title','active','has_mobile_image')
    list_filter = ('active',)
    search_fields = ('title',)
    fields = ('title', 'image', 'mobile_image', 'active')

    @admin.display(boolean=True, description='Mobile Image')
    def has_mobile_image(self, obj):
        return bool(obj.mobile_image)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'order_date', 'total_amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'order_date')
    search_fields = ('username', 'email', 'phone')
    readonly_fields = ('order_date',)
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Info', {
            'fields': ('username', 'order_date', 'total_amount', 'status', 'payment_method')
        }),
        ('Customer Details', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
