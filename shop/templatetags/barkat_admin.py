from django import template
from django.utils import timezone

register = template.Library()


def _fallback_points():
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    values = [9000, 13500, 21000, 26000, 17000, 19500, 31500, 24000, 26500, 34500, 42000, 25000]
    max_value = 50000
    chart_top = 34
    chart_bottom = 226
    chart_left = 50
    step = 586 / 11
    points = []

    for index, value in enumerate(values):
        x = chart_left + (index * step)
        y = chart_bottom - ((value / max_value) * (chart_bottom - chart_top))
        points.append({
            'label': labels[index],
            'amount': f'₹ {value:,}',
            'value': value,
            'percent': f'{max(8, (value / max_value) * 100):.1f}',
            'x': f'{x:.1f}',
            'y': f'{y:.1f}',
        })

    return points


def _fallback_dashboard_context():
    points = _fallback_points()
    line_path = 'M ' + ' L '.join(f"{point['x']},{point['y']}" for point in points)
    area_path = f"{line_path} L {points[-1]['x']},226 L {points[0]['x']},226 Z"
    categories = [
        {'name': 'Silk Sarees', 'count': 3, 'percent': 35, 'color': '#9b143d'},
        {'name': 'Cotton Sarees', 'count': 2, 'percent': 25, 'color': '#d9a441'},
        {'name': 'Designer Sarees', 'count': 2, 'percent': 20, 'color': '#74569b'},
        {'name': 'Chiffon Sarees', 'count': 1, 'percent': 10, 'color': '#ef4b83'},
        {'name': 'Others', 'count': 1, 'percent': 10, 'color': '#38aaa2'},
    ]

    return {
        'dashboard_cards': [
            {'label': 'Total Revenue', 'value': '₹ 2,45,000', 'delta': 15.6, 'hint': 'sample trend', 'icon': 'fa-indian-rupee-sign', 'theme': 'rose'},
            {'label': 'Total Orders', 'value': '1,256', 'delta': 12.4, 'hint': 'sample trend', 'icon': 'fa-bag-shopping', 'theme': 'gold'},
            {'label': 'Customers', 'value': '875', 'delta': 8.2, 'hint': 'sample trend', 'icon': 'fa-users', 'theme': 'purple'},
            {'label': 'Products', 'value': '320', 'delta': 5.7, 'hint': 'sample trend', 'icon': 'fa-box-open', 'theme': 'coral'},
        ],
        'recent_orders': [],
        'top_products': [],
        'inventory_products': [],
        'order_status_summary': [
            {'status': 'pending', 'label': 'Pending', 'count': 0, 'percent': 0, 'color': '#f59e0b'},
            {'status': 'confirmed', 'label': 'Confirmed', 'count': 0, 'percent': 0, 'color': '#8b5cf6'},
            {'status': 'shipped', 'label': 'Shipped', 'count': 0, 'percent': 0, 'color': '#2563eb'},
            {'status': 'delivered', 'label': 'Delivered', 'count': 0, 'percent': 0, 'color': '#16a34a'},
            {'status': 'cancelled', 'label': 'Cancelled', 'count': 0, 'percent': 0, 'color': '#e11d48'},
        ],
        'pending_orders': 0,
        'total_products': 9,
        'sales_line_path': line_path,
        'sales_area_path': area_path,
        'sales_points': points,
        'sales_y_axis': [
            {'label': '50K', 'y': '34.0'},
            {'label': '40K', 'y': '72.4'},
            {'label': '30K', 'y': '110.8'},
            {'label': '20K', 'y': '149.2'},
            {'label': '10K', 'y': '187.6'},
            {'label': '0', 'y': '226.0'},
        ],
        'sales_year': timezone.localdate().year,
        'sales_chart_labels': [point['label'] for point in points],
        'sales_chart_values': [point['value'] for point in points],
        'revenue_trend_values': [sum(point['value'] for point in points[:index + 1]) for index in range(len(points))],
        'categories': categories,
        'category_gradient': '#9b143d 0% 35%, #d9a441 35% 60%, #74569b 60% 80%, #ef4b83 80% 90%, #38aaa2 90% 100%',
        'category_chart_labels': [category['name'] for category in categories],
        'category_chart_values': [category['count'] for category in categories],
        'category_chart_colors': [category['color'] for category in categories],
        'admin_chart_data': {
            'salesLabels': [point['label'] for point in points],
            'monthlySales': [point['value'] for point in points],
            'revenueTrends': [sum(point['value'] for point in points[:index + 1]) for index in range(len(points))],
            'categoryLabels': [category['name'] for category in categories],
            'categoryValues': [category['count'] for category in categories],
            'categoryColors': [category['color'] for category in categories],
        },
    }


@register.simple_tag(takes_context=True)
def load_barkat_dashboard(context):
    try:
        from shop.admin import _admin_dashboard_context
        dashboard_context = _admin_dashboard_context()
    except Exception:
        dashboard_context = _fallback_dashboard_context()

    for key, value in dashboard_context.items():
        context[key] = value

    return ''
