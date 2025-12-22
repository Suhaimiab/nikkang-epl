"""
Timezone utilities for Malaysian Time (MYT/GMT+8)
Pure Python implementation - NO external dependencies needed
Handles conversion from UTC/UK time to Malaysian time
"""

from datetime import datetime, timedelta, timezone

# Malaysian Time Zone (GMT+8, no daylight saving)
MYT_OFFSET = timedelta(hours=8)
MYT = timezone(MYT_OFFSET, 'MYT')

def is_uk_bst(dt):
    """
    Determine if UK is in British Summer Time (BST) on given date
    BST runs from last Sunday in March to last Sunday in October
    
    Args:
        dt: datetime object
    
    Returns:
        bool: True if date is in BST period
    """
    year = dt.year
    
    # Find last Sunday in March
    march_31 = datetime(year, 3, 31, tzinfo=timezone.utc)
    days_back = (march_31.weekday() + 1) % 7
    bst_start = march_31 - timedelta(days=days_back)
    bst_start = bst_start.replace(hour=1, minute=0, second=0, microsecond=0)
    
    # Find last Sunday in October
    oct_31 = datetime(year, 10, 31, tzinfo=timezone.utc)
    days_back = (oct_31.weekday() + 1) % 7
    bst_end = oct_31 - timedelta(days=days_back)
    bst_end = bst_end.replace(hour=1, minute=0, second=0, microsecond=0)
    
    return bst_start <= dt < bst_end

def get_uk_offset(dt):
    """
    Get UK timezone offset for given datetime
    Returns GMT (UTC+0) or BST (UTC+1)
    """
    if is_uk_bst(dt):
        return timedelta(hours=1)  # BST
    else:
        return timedelta(hours=0)  # GMT

def get_malaysian_time():
    """Get current time in Malaysian timezone"""
    utc_now = datetime.now(timezone.utc)
    return utc_now.astimezone(MYT)

def get_malaysian_datetime_str(format='%Y-%m-%d %H:%M:%S'):
    """Get current Malaysian time as formatted string"""
    return get_malaysian_time().strftime(format)

def get_malaysian_date():
    """Get current Malaysian date"""
    return get_malaysian_time().date()

def convert_utc_to_malaysian(utc_datetime_str):
    """
    Convert UTC datetime string to Malaysian time
    
    Args:
        utc_datetime_str: UTC datetime string (e.g., "2024-03-15T19:30:00Z")
    
    Returns:
        datetime object in Malaysian timezone
    """
    # Handle ISO format with Z
    if isinstance(utc_datetime_str, str):
        if 'Z' in utc_datetime_str:
            utc_datetime_str = utc_datetime_str.replace('Z', '+00:00')
        
        # Parse the datetime
        try:
            # Try parsing with timezone
            if '+' in utc_datetime_str or '-' in utc_datetime_str.split('T')[-1]:
                # Has timezone info
                dt = datetime.fromisoformat(utc_datetime_str)
            else:
                # No timezone info, assume UTC
                dt = datetime.fromisoformat(utc_datetime_str)
                dt = dt.replace(tzinfo=timezone.utc)
        except:
            # Fallback parsing
            dt = datetime.strptime(utc_datetime_str, '%Y-%m-%dT%H:%M:%S')
            dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = utc_datetime_str
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Malaysian time
    return dt.astimezone(MYT)

def convert_uk_to_malaysian(uk_datetime):
    """
    Convert UK time to Malaysian time (handles BST/GMT automatically)
    
    Args:
        uk_datetime: datetime object or string in UK timezone
    
    Returns:
        datetime object in Malaysian timezone
    """
    if isinstance(uk_datetime, str):
        # Parse string
        try:
            dt = datetime.fromisoformat(uk_datetime)
        except:
            dt = datetime.strptime(uk_datetime, '%Y-%m-%d %H:%M:%S')
    else:
        dt = uk_datetime
    
    # If no timezone info, determine UK offset and apply
    if dt.tzinfo is None:
        uk_offset = get_uk_offset(dt.replace(tzinfo=timezone.utc))
        uk_tz = timezone(uk_offset, 'UK')
        dt = dt.replace(tzinfo=uk_tz)
    
    # Convert to Malaysian time
    return dt.astimezone(MYT)

def format_match_time_malaysian(utc_datetime_str):
    """
    Format match time for display in Malaysian timezone
    
    Args:
        utc_datetime_str: UTC datetime string from API
    
    Returns:
        tuple: (date_str, time_str) in Malaysian timezone
    """
    myt_dt = convert_utc_to_malaysian(utc_datetime_str)
    return (
        myt_dt.strftime("%Y-%m-%d"),
        myt_dt.strftime("%H:%M")
    )

def get_time_offset_info():
    """
    Get current time offset information between UK and Malaysia
    
    Returns:
        dict with offset information
    """
    utc_now = datetime.now(timezone.utc)
    now_myt = utc_now.astimezone(MYT)
    
    # Get UK offset
    uk_offset = get_uk_offset(utc_now)
    uk_tz = timezone(uk_offset, 'BST' if uk_offset.total_seconds() > 0 else 'GMT')
    now_uk = utc_now.astimezone(uk_tz)
    
    # Calculate offset
    offset_hours = int((MYT_OFFSET - uk_offset).total_seconds() / 3600)
    
    # Check if UK is in BST or GMT
    uk_is_bst = uk_offset.total_seconds() > 0
    
    return {
        'uk_timezone': 'BST (British Summer Time)' if uk_is_bst else 'GMT (Greenwich Mean Time)',
        'malaysia_timezone': 'MYT (Malaysian Time, GMT+8)',
        'offset_hours': offset_hours,
        'offset_description': f'Malaysia is {offset_hours} hours ahead of UK',
        'uk_time': now_uk.strftime('%Y-%m-%d %H:%M:%S') + ' ' + ('BST' if uk_is_bst else 'GMT'),
        'malaysian_time': now_myt.strftime('%Y-%m-%d %H:%M:%S MYT')
    }

# Helper function for backward compatibility
def now_str(format='%Y-%m-%d %H:%M:%S'):
    """Alias for get_malaysian_datetime_str for easy replacement"""
    return get_malaysian_datetime_str(format)

def now():
    """Alias for get_malaysian_time for easy replacement"""
    return get_malaysian_time()

def today():
    """Get today's date in Malaysian timezone"""
    return get_malaysian_date()


if __name__ == "__main__":
    # Test the functions
    print("=== Malaysian Time Utilities Test ===\n")
    
    info = get_time_offset_info()
    print(f"UK Time: {info['uk_time']}")
    print(f"Malaysian Time: {info['malaysian_time']}")
    print(f"Offset: {info['offset_description']}\n")
    
    # Test UTC conversion
    utc_test = "2024-03-15T19:30:00Z"
    myt_dt = convert_utc_to_malaysian(utc_test)
    print(f"UTC: {utc_test}")
    print(f"Malaysian: {myt_dt.strftime('%Y-%m-%d %H:%M:%S MYT')}\n")
    
    # Test match time formatting
    date_str, time_str = format_match_time_malaysian(utc_test)
    print(f"Match Date: {date_str}")
    print(f"Match Time: {time_str}\n")
    
    # Test BST period
    summer_test = "2024-07-15T18:30:00Z"
    summer_myt = convert_utc_to_malaysian(summer_test)
    print(f"Summer UTC: {summer_test}")
    print(f"Summer Malaysian: {summer_myt.strftime('%Y-%m-%d %H:%M:%S MYT')}")
    print(f"(UK would be in BST, UTC+1)")
