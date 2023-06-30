from datetime import datetime as dt
from datetime import timedelta

from dateutil.relativedelta import relativedelta


def compute_report_dates(start_date: str, end_date: str, pay_period: str, arrears: int) -> tuple[str, str]:
    """computes the dates required for the earnings report based on pay period and arrears"""
    payrun_start_date = dt.strptime(start_date, "%Y-%m-%d")
    payrun_end_date = dt.strptime(end_date, "%Y-%m-%d")
    if arrears == 0:
        earnings_period_start = start_date
        earnings_period_end = end_date
    else:
        if pay_period == "Monthly":
            report_start_date = payrun_start_date + relativedelta(months=-arrears)
            report_end_date = report_start_date + relativedelta(months=1, days=-1)
            earnings_period_start = report_start_date.strftime("%Y-%m-%d")
            earnings_period_end = report_end_date.strftime("%Y-%m-%d")
        else:
            delta = compute_timedelta(pay_period, arrears)
            report_start_date = payrun_start_date - delta
            report_end_date = payrun_end_date - delta
            earnings_period_start = report_start_date.strftime("%Y-%m-%d")
            earnings_period_end = report_end_date.strftime("%Y-%m-%d")
    return earnings_period_start, earnings_period_end


def compute_timedelta(pay_period: str, arrears: int) -> timedelta:
    """computes time deltas for various arrears and pay periods"""
    if pay_period == "Daily":
        return timedelta(days=arrears)
    elif pay_period == "Weekly":
        return timedelta(weeks=arrears)
    elif pay_period == "Fortnightly":
        return timedelta(weeks=(2 * arrears))
    elif pay_period == "Four Weekly":
        return timedelta(weeks=(4 * arrears))
    raise ValueError("Invalid pay period specified.")
