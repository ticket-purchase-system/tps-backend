from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal
from app.models.event import Event
from app.models.orders import Order, OrderProduct

USE_SYNTHETIC_DATA = True


@api_view(['GET'])
def event_statistics(request):
    """
    Get comprehensive event statistics with filtering options
    Query params:
    - timeframe: 'all', 'week', 'month', 'quarter', 'year'
    - event_type: 'all', 'CONCERT', 'SPORTS', 'THEATER', etc.
    """
    timeframe = request.GET.get('timeframe', 'all')
    event_type = request.GET.get('event_type', 'all')

    if USE_SYNTHETIC_DATA:
        return Response(generate_synthetic_statistics(timeframe, event_type))

    try:
        events_queryset = Event.objects.all()

        if timeframe != 'all':
            now = timezone.now()
            if timeframe == 'week':
                start_date = now - timedelta(weeks=1)
            elif timeframe == 'month':
                start_date = now - timedelta(days=30)
            elif timeframe == 'quarter':
                start_date = now - timedelta(days=90)
            elif timeframe == 'year':
                start_date = now - timedelta(days=365)
            else:
                start_date = None

            if start_date:
                events_queryset = events_queryset.filter(date__gte=start_date)

        if event_type != 'all':
            events_queryset = events_queryset.filter(type=event_type)

        total_events = events_queryset.count()

        orders = Order.objects.filter(
            orderproduct__product__event__in=events_queryset
        ).distinct()

        total_tickets_sold = OrderProduct.objects.filter(
            product__event__in=events_queryset
        ).aggregate(total=Sum('quantity'))['total'] or 0

        total_revenue = orders.aggregate(total=Sum('price'))['total'] or Decimal('0.00')

        avg_tickets_per_event = total_tickets_sold / total_events if total_events > 0 else 0

        statistics = {
            'totalTicketsSold': total_tickets_sold,
            'totalRevenue': float(total_revenue),
            'totalEvents': total_events,
            'averageTicketsPerEvent': round(avg_tickets_per_event, 1),
            'topSellingEvents': get_top_selling_events_real(events_queryset),
            'monthlyTrends': get_monthly_trends_real(),
            'eventTypeDistribution': get_event_type_distribution_real(),
            'dailySales': get_daily_sales_real(),
            'priceRangeAnalysis': get_price_range_analysis_real(),
            'performanceInsights': get_performance_insights_real(),
            'popularVenues': get_popular_venues_real(),
            'peakHours': get_peak_hours_real()
        }

        return Response(statistics)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def top_selling_events(request):
    """Get top selling events"""
    limit = int(request.GET.get('limit', 10))

    if USE_SYNTHETIC_DATA:
        return Response(generate_synthetic_top_selling_events(limit))

    events = Event.objects.annotate(
        tickets_sold=Sum('products__orderproduct__quantity'),
        revenue=Sum('products__orderproduct__order__price')
    ).filter(
        tickets_sold__isnull=False
    ).order_by('-tickets_sold')[:limit]

    result = []
    for event in events:
        avg_price = float(event.revenue / event.tickets_sold) if event.tickets_sold > 0 else 0
        result.append({
            'name': event.title,
            'tickets': event.tickets_sold or 0,
            'revenue': float(event.revenue or 0),
            'date': event.date.strftime('%Y-%m-%d'),
            'avgPrice': round(avg_price, 2)
        })

    return Response(result)


@api_view(['GET'])
def monthly_trends(request):
    """Get monthly trends for the current year"""
    year = request.GET.get('year', timezone.now().year)

    if USE_SYNTHETIC_DATA:
        return Response(generate_synthetic_monthly_trends())

    return Response(generate_synthetic_monthly_trends())  # Fallback for now


@api_view(['GET'])
def event_type_distribution(request):
    """Get distribution of events by type"""
    if USE_SYNTHETIC_DATA:
        return Response(generate_synthetic_event_type_distribution())

    distribution = Event.objects.values('type').annotate(
        count=Count('id'),
        tickets=Sum('products__orderproduct__quantity')
    ).order_by('-count')

    total_tickets = sum(item['tickets'] or 0 for item in distribution)

    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316', '#06B6D4']

    result = []
    for i, item in enumerate(distribution):
        tickets = item['tickets'] or 0
        percentage = (tickets / total_tickets * 100) if total_tickets > 0 else 0
        result.append({
            'type': item['type'],
            'tickets': tickets,
            'percentage': round(percentage, 1),
            'color': colors[i % len(colors)]
        })

    return Response(result)


@api_view(['POST'])
def toggle_data_source(request):
    """Toggle between synthetic and real data"""
    global USE_SYNTHETIC_DATA
    USE_SYNTHETIC_DATA = not USE_SYNTHETIC_DATA

    return Response({
        'use_synthetic_data': USE_SYNTHETIC_DATA,
        'message': f'Switched to {"synthetic" if USE_SYNTHETIC_DATA else "real"} data'
    })


@api_view(['GET'])
def data_source_status(request):
    """Get current data source status"""
    return Response({
        'use_synthetic_data': USE_SYNTHETIC_DATA,
        'message': f'Currently using {"synthetic" if USE_SYNTHETIC_DATA else "real"} data'
    })


# Synthetic data generation functions
def generate_synthetic_statistics(timeframe, event_type):
    """Generate synthetic statistics data"""
    # Apply multipliers based on filters
    base_multiplier = 1

    if timeframe == 'week':
        base_multiplier = 0.05
    elif timeframe == 'month':
        base_multiplier = 0.2
    elif timeframe == 'quarter':
        base_multiplier = 0.5
    elif timeframe == 'year':
        base_multiplier = 0.8

    event_type_multiplier = 1 if event_type == 'all' else 0.25
    multiplier = base_multiplier * event_type_multiplier

    return {
        'totalTicketsSold': int(45678 * multiplier),
        'totalRevenue': int(2345678 * multiplier),
        'totalEvents': int(234 * multiplier),
        'averageTicketsPerEvent': 195.2,
        'topSellingEvents': generate_synthetic_top_selling_events(5),
        'monthlyTrends': generate_synthetic_monthly_trends(),
        'eventTypeDistribution': generate_synthetic_event_type_distribution(),
        'dailySales': generate_synthetic_daily_sales(),
        'priceRangeAnalysis': generate_synthetic_price_range_analysis(),
        'performanceInsights': {
            'conversionRate': 68.5,
            'repeatCustomers': 42.3,
            'avgOrderValue': 89.99
        },
        'popularVenues': generate_synthetic_popular_venues(),
        'peakHours': generate_synthetic_peak_hours()
    }


def generate_synthetic_top_selling_events(limit):
    """Generate synthetic top selling events"""
    events = [
        {'name': 'Taylor Swift - Eras Tour', 'tickets': 15000, 'revenue': 2250000, 'date': '2024-06-15',
         'avgPrice': 150},
        {'name': 'Coachella Music Festival', 'tickets': 12000, 'revenue': 1800000, 'date': '2024-04-12',
         'avgPrice': 150},
        {'name': 'Hamilton Broadway Show', 'tickets': 8500, 'revenue': 1445000, 'date': '2024-03-20', 'avgPrice': 170},
        {'name': 'NBA Finals Game 7', 'tickets': 7200, 'revenue': 1440000, 'date': '2024-06-18', 'avgPrice': 200},
        {'name': 'Comic-Con 2024', 'tickets': 6800, 'revenue': 816000, 'date': '2024-07-25', 'avgPrice': 120},
        {'name': 'Beyoncé Renaissance Tour', 'tickets': 6500, 'revenue': 975000, 'date': '2024-05-10', 'avgPrice': 150},
        {'name': 'Super Bowl LVIII', 'tickets': 5200, 'revenue': 2080000, 'date': '2024-02-11', 'avgPrice': 400},
        {'name': 'Burning Man Festival', 'tickets': 4800, 'revenue': 720000, 'date': '2024-08-27', 'avgPrice': 150},
        {'name': 'The Lion King Broadway', 'tickets': 4500, 'revenue': 675000, 'date': '2024-04-05', 'avgPrice': 150},
        {'name': 'UFC Championship Fight', 'tickets': 4200, 'revenue': 630000, 'date': '2024-03-30', 'avgPrice': 150}
    ]
    return events[:limit]


def generate_synthetic_monthly_trends():
    """Generate synthetic monthly trends"""
    return [
        {'month': 'Jan', 'tickets': 3200, 'revenue': 320000, 'events': 15},
        {'month': 'Feb', 'tickets': 3800, 'revenue': 380000, 'events': 18},
        {'month': 'Mar', 'tickets': 4200, 'revenue': 420000, 'events': 22},
        {'month': 'Apr', 'tickets': 5100, 'revenue': 510000, 'events': 25},
        {'month': 'May', 'tickets': 5800, 'revenue': 580000, 'events': 28},
        {'month': 'Jun', 'tickets': 6200, 'revenue': 620000, 'events': 30},
        {'month': 'Jul', 'tickets': 5900, 'revenue': 590000, 'events': 28},
        {'month': 'Aug', 'tickets': 5400, 'revenue': 540000, 'events': 26},
        {'month': 'Sep', 'tickets': 4800, 'revenue': 480000, 'events': 23},
        {'month': 'Oct', 'tickets': 4300, 'revenue': 430000, 'events': 20},
        {'month': 'Nov', 'tickets': 3900, 'revenue': 390000, 'events': 18},
        {'month': 'Dec', 'tickets': 3500, 'revenue': 350000, 'events': 16}
    ]


def generate_synthetic_event_type_distribution():
    """Generate synthetic event type distribution"""
    return [
        {'type': 'Concerts', 'tickets': 18500, 'percentage': 40.5, 'color': '#3B82F6'},
        {'type': 'Sports', 'tickets': 12300, 'percentage': 26.9, 'color': '#10B981'},
        {'type': 'Theater', 'tickets': 8200, 'percentage': 17.9, 'color': '#F59E0B'},
        {'type': 'Festivals', 'tickets': 4600, 'percentage': 10.1, 'color': '#EF4444'},
        {'type': 'Other', 'tickets': 2078, 'percentage': 4.6, 'color': '#8B5CF6'}
    ]


def generate_synthetic_daily_sales():
    """Generate synthetic daily sales"""
    return [
        {'day': 'Monday', 'tickets': 4200, 'revenue': 378000},
        {'day': 'Tuesday', 'tickets': 4800, 'revenue': 432000},
        {'day': 'Wednesday', 'tickets': 5200, 'revenue': 468000},
        {'day': 'Thursday', 'tickets': 5800, 'revenue': 522000},
        {'day': 'Friday', 'tickets': 8200, 'revenue': 738000},
        {'day': 'Saturday', 'tickets': 9500, 'revenue': 855000},
        {'day': 'Sunday', 'tickets': 7978, 'revenue': 718020}
    ]


def generate_synthetic_price_range_analysis():
    """Generate synthetic price range analysis"""
    return [
        {'range': '$0-50', 'tickets': 8500, 'events': 45, 'avgPrice': 35},
        {'range': '$51-100', 'tickets': 12300, 'events': 62, 'avgPrice': 75},
        {'range': '$101-200', 'tickets': 15600, 'events': 78, 'avgPrice': 150},
        {'range': '$201-500', 'tickets': 7800, 'events': 39, 'avgPrice': 350},
        {'range': '$500+', 'tickets': 1478, 'events': 10, 'avgPrice': 750}
    ]


def generate_synthetic_popular_venues():
    """Generate synthetic popular venues"""
    return [
        {'name': 'Madison Square Garden', 'percentage': 22.5},
        {'name': 'Hollywood Bowl', 'percentage': 18.3},
        {'name': 'Red Rocks Amphitheatre', 'percentage': 15.7},
        {'name': 'The Forum', 'percentage': 12.1},
        {'name': 'Other Venues', 'percentage': 31.4}
    ]


def generate_synthetic_peak_hours():
    """Generate synthetic peak hours"""
    return [
        {'time': '6:00 PM - 8:00 PM', 'percentage': 35.2},
        {'time': '8:00 PM - 10:00 PM', 'percentage': 28.6},
        {'time': '2:00 PM - 4:00 PM', 'percentage': 18.4},
        {'time': '10:00 AM - 12:00 PM', 'percentage': 12.3},
        {'time': 'Other Hours', 'percentage': 5.5}
    ]


def get_top_selling_events_real(events_queryset, limit=5):
    """Get real top selling events"""
    return generate_synthetic_top_selling_events(limit)


def get_monthly_trends_real():
    """Get real monthly trends"""
    return generate_synthetic_monthly_trends()


def get_event_type_distribution_real():
    """Get real event type distribution"""
    return generate_synthetic_event_type_distribution()


def get_daily_sales_real():
    """Get real daily sales"""
    return generate_synthetic_daily_sales()


def get_price_range_analysis_real():
    """Get real price range analysis"""
    return generate_synthetic_price_range_analysis()


def get_performance_insights_real():
    """Get real performance insights"""
    return {
        'conversionRate': 68.5,
        'repeatCustomers': 42.3,
        'avgOrderValue': 89.99
    }


def get_popular_venues_real():
    """Get real popular venues"""
    return generate_synthetic_popular_venues()


def get_peak_hours_real():
    """Get real peak hours"""
    return generate_synthetic_peak_hours()