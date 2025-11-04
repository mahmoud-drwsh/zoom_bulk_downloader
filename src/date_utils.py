"""Date utility functions for generating month ranges."""

import datetime
from dateutil.relativedelta import relativedelta


def get_month_ranges_for_past_year():
    """Generate month ranges for the past 12 months."""
    today = datetime.date.today()
    ranges = []
    
    for i in range(12):
        # Start from 12 months ago and work forward
        month_start = (today - relativedelta(months=12-i)).replace(day=1)
        # Last day of the month
        if month_start.month == 12:
            month_end = month_start.replace(day=31)
        else:
            month_end = (month_start + relativedelta(months=1) - datetime.timedelta(days=1))
        
        # Don't go past today
        if month_end > today:
            month_end = today
        
        ranges.append((
            month_start.strftime("%Y-%m-%d"),
            month_end.strftime("%Y-%m-%d")
        ))
    
    return ranges

