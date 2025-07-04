import random, string
from datetime import datetime, timedelta

def generate_shortcode(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def calculate_expiry(minutes=30):
    return datetime.utcnow() + timedelta(minutes=minutes)

def format_iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
