from django import template
import jdatetime

register = template.Library()


@register.filter
def jalali_datetime(value, fmt="%Y/%m/%d %H:%M"):
    """Convert a datetime to Jalali formatted string using jdatetime."""
    if not value:
        return ''
    try:
        gregorian = value
        jdt = jdatetime.datetime.fromgregorian(datetime=gregorian)
        return jdt.strftime(fmt)
    except Exception:
        return str(value)
