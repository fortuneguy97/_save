import re

def looks_like_address(address: str) -> bool:
    address = address.strip().lower()

    # Keep all letters (Latin and non-Latin) and numbers
    # Using a more compatible approach for Unicode characters
    address_len = re.sub(r'[^\w]', '', address.strip(), flags=re.UNICODE)
    if len(address_len) < 30:
        return False
    if len(address_len) > 300:  # maximum length check
        return False

    # Count letters (both Latin and non-Latin) - using \w which includes Unicode letters
    letter_count = len(re.findall(r'[^\W\d]', address, flags=re.UNICODE))
    if letter_count < 20:
        return False

    if re.match(r"^[^a-zA-Z]*$", address):  # no letters at all
        return False
    if len(set(address)) < 5:  # all chars basically the same
        return False
        
    # Has at least one digit in a comma-separated section
    # Replace hyphens and semicolons with empty strings before counting numbers
    address_for_number_count = address.replace('-', '').replace(';', '')
    # Split address by commas and check for numbers in each section
    sections = [s.strip() for s in address_for_number_count.split(',')]
    sections_with_numbers = []
    for section in sections:
        # Only match ASCII digits (0-9), not other numeric characters
        number_groups = re.findall(r"[0-9]+", section)
        if len(number_groups) > 0:
            sections_with_numbers.append(section)
    # Need at least 1 section that contains numbers
    if len(sections_with_numbers) < 1:
        return False

    if address.count(",") < 2:
        return False
    
    # Check for special characters that should not be in addresses
    special_chars = ['`', ':', '%', '$', '@', '*', '^', '[', ']', '{', '}', '_', '«', '»']
    if any(char in address for char in special_chars):
        return False
    
    # # Contains common address words or patterns
    # common_words = ["st", "street", "rd", "road", "ave", "avenue", "blvd", "boulevard", "drive", "ln", "lane", "plaza", "city", "platz", "straße", "straße", "way", "place", "square", "allee", "allee", "gasse", "gasse"]
    # # Also check for common patterns like "1-1-1" (Japanese addresses) or "Unter den" (German)
    # has_common_word = any(word in address for word in common_words)
    # has_address_pattern = re.search(r'\d+-\d+-\d+', address) or re.search(r'unter den|marienplatz|champs|place de', address)
    
    # if not (has_common_word or has_address_pattern):
    #     return False
    
    return True


if __name__ == "__main__":
    address = "Musée Océanographique, Avenue Saint-Martin, Monaco, 98000, Monaco"
    print(looks_like_address(address))