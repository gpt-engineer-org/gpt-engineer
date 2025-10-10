import phonenumbers
from phonenumbers import geocoder, carrier

def get_phone_info(phone_number):
    """
    Get location and carrier information for a phone number.
    
    Args:
        phone_number (str): Phone number in international format (e.g., "+923000087356")
    
    Returns:
        dict: Dictionary containing phone number details
    """
    try:
        # Parse phone number
        parsed_number = phonenumbers.parse(phone_number)
        
        # Validate phone number
        if not phonenumbers.is_valid_number(parsed_number):
            return {
                "phone_number": phone_number,
                "valid": False,
                "error": "Invalid phone number"
            }
        
        # Get location
        location = geocoder.description_for_number(parsed_number, "en")
        
        # Get carrier
        service_provider = carrier.name_for_number(parsed_number, "en")
        
        # Return results
        return {
            "phone_number": phone_number,
            "valid": True,
            "location": location if location else "Unknown",
            "service_provider": service_provider if service_provider else "Unknown",
            "country_code": parsed_number.country_code,
            "national_number": parsed_number.national_number
        }
    
    except phonenumbers.phonenumberutil.NumberParseException as e:
        return {
            "phone_number": phone_number,
            "valid": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Example usage
    phone_number = "+923000087356"
    
    result = get_phone_info(phone_number)
    
    # Output results
    print(f"Phone Number: {result['phone_number']}")
    if result['valid']:
        print(f"Location: {result['location']}")
        print(f"Service Provider: {result['service_provider']}")
        print(f"Country Code: +{result['country_code']}")
        print(f"National Number: {result['national_number']}")
    else:
        print(f"Error: {result['error']}")