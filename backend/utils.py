def parse_numeric(s):
    """
    Convert string to the most logical numeric type.
    Returns: int, float, or original string
    """
    if not isinstance(s, str):
        return s
    
    s = s.strip()  # Remove whitespace
    
    if not s:  # Empty string
        return s
    
    try:
        # Check if it's a float with decimal point
        if '.' in s:
            result = float(s)
            # Check if it's actually a whole number (like "42.0")
            if result.is_integer():
                return int(result)
            return result
        
        # Check for scientific notation
        if 'e' in s.lower():
            result = float(s)
            if result.is_integer():
                return int(result)
            return result
        
        # Try parsing as integer
        return int(s)
        
    except (ValueError, OverflowError):
        # If parsing fails, return original string
        return s
