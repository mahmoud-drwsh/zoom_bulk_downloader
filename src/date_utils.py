"""Date utility functions for generating month ranges."""

import datetime
from dateutil.relativedelta import relativedelta


def get_month_ranges_for_past_year():
    """Generate month ranges for the past 12 months, plus current and next month with buffer."""
    today = datetime.date.today()
    ranges = []
    current_month_start = today.replace(day=1)
    
    # Generate ranges for the past 12 months PLUS current month (13 months total)
    # This ensures we don't miss any month, especially the current month
    for i in range(13):
        # Start from 12 months ago and work forward to current month
        # When i=0: 12 months ago, i=11: 1 month ago, i=12: current month
        month_start = (today - relativedelta(months=12-i)).replace(day=1)
        
        # Last day of the month
        if month_start.month == 12:
            month_end = month_start.replace(day=31)
        else:
            month_end = (month_start + relativedelta(months=1) - datetime.timedelta(days=1))
        
        # For the current month and any future-looking months, extend to today + 7 days buffer
        # This ensures we don't miss recordings from today due to timezone or API interpretation issues
        if month_start == current_month_start:
            # Current month: extend to today + 7 days buffer
            month_end = today + datetime.timedelta(days=7)
        elif month_end > today:
            # For any month that extends past today (shouldn't happen for past months, but just in case)
            month_end = today + datetime.timedelta(days=7)
        else:
            # For past months, add 1 day buffer to catch recordings on the last day of the month
            # This helps if the API interprets date ranges as exclusive on the end date
            month_end = month_end + datetime.timedelta(days=1)
        
        ranges.append((
            month_start.strftime("%Y-%m-%d"),
            month_end.strftime("%Y-%m-%d")
        ))
    
    # Add next month range to catch any edge cases where recordings might be dated slightly in the future
    next_month_start = (current_month_start + relativedelta(months=1))
    if next_month_start.month == 12:
        next_month_end = next_month_start.replace(day=31)
    else:
        next_month_end = (next_month_start + relativedelta(months=1) - datetime.timedelta(days=1))
    
    # Add next month range
    ranges.append((
        next_month_start.strftime("%Y-%m-%d"),
        next_month_end.strftime("%Y-%m-%d")
    ))
    
    return ranges

