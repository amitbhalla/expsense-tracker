from django import template

register = template.Library()

@register.filter
def indian_currency(value):
    """
    Format a number as Indian currency (with commas every 2 digits except the first 3)
    e.g., 12345678 becomes 1,23,45,678
    """
    if value is None:
        return "0.00"
    
    # Convert to float or int if it's a string
    try:
        value = float(value)
    except ValueError:
        return value
    
    # Format with 2 decimal places
    value = '{:.2f}'.format(value)
    
    # Split the decimal part
    parts = str(value).split('.')
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else "00"
    
    # Add commas to the integer part
    result = ""
    
    # Handle negative numbers
    is_negative = False
    if integer_part.startswith('-'):
        is_negative = True
        integer_part = integer_part[1:]
    
    # Group digits
    if len(integer_part) <= 3:
        result = integer_part
    else:
        # Add the first group (rightmost 3 digits)
        result = integer_part[-3:]
        # Add the remaining groups (2 digits each)
        remaining = integer_part[:-3]
        
        while remaining:
            # Take the rightmost 2 digits of the remaining part
            if len(remaining) >= 2:
                result = remaining[-2:] + "," + result
                remaining = remaining[:-2]
            else:
                result = remaining + "," + result
                remaining = ""
    
    # Add negative sign back if needed
    if is_negative:
        result = "-" + result
    
    return result + "." + decimal_part