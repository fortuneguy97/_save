import geonamescache
import time

_geonames_cache = None
_cities_data = None
_countries_data = None
COUNTRY_MAPPING = {
    # Korea variations
    "korea, south": "south korea",
    "korea, north": "north korea",
    
    # Cote d'Ivoire variations
    "cote d ivoire": "ivory coast",
    "côte d'ivoire": "ivory coast",
    "cote d'ivoire": "ivory coast",
    
    # Gambia variations
    "the gambia": "gambia",
    
    # Netherlands variations
    "netherlands": "the netherlands",
    "holland": "the netherlands",
    
    # Congo variations
    "congo, democratic republic of the": "democratic republic of the congo",
    "drc": "democratic republic of the congo",
    "congo, republic of the": "republic of the congo",
    
    # Burma/Myanmar variations
    "burma": "myanmar",

    # Bonaire variations
    'bonaire': 'bonaire, saint eustatius and saba',
    
    # Additional common variations
    "usa": "united states",
    "us": "united states",
    "united states of america": "united states",
    "uk": "united kingdom",
    "great britain": "united kingdom",
    "britain": "united kingdom",
    "uae": "united arab emirates",
    "u.s.a.": "united states",
    "u.s.": "united states",
    "u.k.": "united kingdom",
}


def get_geonames_data():
    """Get cached geonames data, loading it only once."""
    global _geonames_cache, _cities_data, _countries_data
    
    if _geonames_cache is None:
        print("Loading geonames data for the first time...")
        start_time = time.time()
        _geonames_cache = geonamescache.GeonamesCache()
        _cities_data = _geonames_cache.get_cities()
        _countries_data = _geonames_cache.get_countries()
        end_time = time.time()
        print(f"Geonames data loaded in {end_time - start_time:.2f} seconds")
    
    return _cities_data, _countries_data


def check_western_sahara_cities(generated_address: str) -> bool:
    """
    Check if any Western Sahara city appears in the generated address.
    
    Args:
        generated_address: The generated address to check
        
    Returns:
        True if any Western Sahara city is found in the address, False otherwise
    """
    if not generated_address:
        return False
    
    # Western Sahara cities
    WESTERN_SAHARA_CITIES = [
        "laayoune", "dakhla", "boujdour", "es semara", "sahrawi", "tifariti", "aousserd"
    ]
    
    gen_lower = generated_address.lower()
    
    # Check if any of the cities appear in the generated address
    for city in WESTERN_SAHARA_CITIES:
        if city in gen_lower:
            return True
    
    return False


def extract_city_country(address: str, two_parts: bool = False) -> tuple:
    """
    Extract city and country from an address.
    Country is always the last part.
    City is found by checking each section from right to left (excluding country)
    and validating against geonames data to ensure it's a real city in the country.
    
    Examples:
    - "115 New Cavendish Street, London W1T 5DU, United Kingdom" -> ("London", "United Kingdom")
    - "223 William Street, Melbourne VIC 3000, Australia" -> ("Melbourne", "Australia")
    - "Rosenthaler Straße 1, 10119 Berlin, Germany" -> ("Berlin", "Germany")
    - "3 Upper Alma Road, Rosebank, Cape Town, 7700, South Africa" -> ("Cape Town", "South Africa")
    - "6 , Yemen" -> ("", "Yemen")  # No valid city found
    
    Args:
        address: The address to extract from
        two_parts: If True, treat the last two comma-separated segments as the country
                   (e.g., "congo, republic of the"). Defaults to False.

    Returns:
        Tuple of (city, country) - both strings, empty if not found
        The country is returned in its normalized form (mapped to standard name)
    """
    if not address:
        return "", ""

    address = address.lower()
    
    parts = [p.strip() for p in address.split(",")]
    if len(parts) < 2:
        return "", ""

    # Determine country and its normalized form
    # The country_checking_name is used for geonames lookups
    # The normalized_country is what we return
    
    # Always try single-part country first (just the last segment)
    last_part = parts[-1]
    single_part_normalized = COUNTRY_MAPPING.get(last_part, last_part)
    
    # If two_parts flag is set, also try two-part country
    country_checking_name = ''
    if two_parts and len(parts) >= 2:
        two_part_raw = f"{parts[-2]}, {parts[-1]}"
        two_part_normalized = COUNTRY_MAPPING.get(two_part_raw, two_part_raw)

        if two_part_raw != two_part_normalized:
            country_checking_name = two_part_normalized
            normalized_country = two_part_normalized
            used_two_parts_for_country = True

    if country_checking_name == '':
        # Single-part country
        country_checking_name = single_part_normalized
        normalized_country = single_part_normalized
        used_two_parts_for_country = False

    # If no country found, return empty
    if not normalized_country:
        return "", ""

    # Check each section from right to left (excluding the country)
    exclude_count = 2 if used_two_parts_for_country else 1
    # Start from 2 when excluding one part (country), 3 when excluding two parts
    for i in range(exclude_count + 1, len(parts) + 1):
        candidate_index = -i
        if abs(candidate_index) > len(parts):
            break
        
        candidate_part = parts[candidate_index]
        if not candidate_part:
            continue
            
        words = candidate_part.split()
        
        # Try different combinations of words (1-2 words max)
        # Start with 2 words, then 1 word for better city matching
        for num_words in range(len(words)):
            current_word = words[num_words]

            # Try current word
            candidates = [current_word]

            # Also try current + previous (if exists)
            if num_words > 0:
                prev_plus_current = words[num_words - 1] + " " + words[num_words]
                candidates.append(prev_plus_current)

            for city_candidate in candidates:
                # Skip if contains numbers or is too short
                if any(char.isdigit() for char in city_candidate):
                    continue

                # Validate the city exists in the country
                if city_in_country(city_candidate, country_checking_name):
                    return city_candidate, normalized_country

    return "", normalized_country


def city_in_country(city_name: str, country_name: str) -> bool:
    """
    Check if a city is actually in the specified country using geonamescache.
    
    Args:
        city_name: Name of the city
        country_name: Name of the country
        
    Returns:
        True if city is in country, False otherwise
    """
    if not city_name or not country_name:
        return False
    
    try:
        cities, countries = get_geonames_data()
        
        city_name_lower = city_name.lower()
        country_name_lower = country_name.lower()
        
        # Find country code
        country_code = None
        for code, data in countries.items():
            if data.get('name', '').lower().strip() == country_name_lower.strip():
                country_code = code
                break
        
        if not country_code:
            return False
        
        # Only check cities that are actually in the specified country
        city_words = city_name_lower.split()
        
        for city_id, city_data in cities.items():
            # Skip cities not in the target country
            if city_data.get("countrycode", "") != country_code:
                continue
                
            city_data_name = city_data.get("name", "").lower()
            
            # Check exact match first
            if city_data_name.strip() == city_name_lower.strip():
                return True
            # Check first word match
            elif len(city_words) >= 2 and city_data_name.startswith(city_words[0]):
                return True
            # Check second word match
            elif len(city_words) >= 2 and city_words[1] in city_data_name:
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking city '{city_name}' in country '{country_name}': {str(e)}")
        return False


def validate_address_region(generated_address: str, seed_address: str) -> bool:
    """
    Validate that generated address has correct region from seed address.
    
    Special handling for disputed regions not in geonames:
    - Luhansk, Crimea, Donetsk, West Sahara
    
    Args:
        generated_address: The generated address to validate
        seed_address: The seed address to match against
        
    Returns:
        True if region is valid, False otherwise
    """
    if not generated_address or not seed_address:
        return False
    
    # Special handling for disputed regions not in geonames
    seed_lower = seed_address.lower()
    
    # Special handling for Western Sahara - check for cities instead of region name
    if seed_lower in ["west sahara", "western sahara"]:
        return check_western_sahara_cities(generated_address)
    
    # Other special regions
    OTHER_SPECIAL_REGIONS = ["luhansk", "crimea", "donetsk"]
    if seed_lower in OTHER_SPECIAL_REGIONS:
        # If seed is a special region, check if that region appears in generated address
        gen_lower = generated_address.lower()
        return seed_lower in gen_lower
    
    # Extract city and country from both addresses
    gen_city, gen_country = extract_city_country(generated_address, two_parts=(',' in seed_address))
    seed_address_lower = seed_address.lower()
    seed_address_mapped = COUNTRY_MAPPING.get(seed_address.lower(), seed_address.lower())

    
    # If no city was extracted from generated address, it's an error
    if not gen_city:
        print("-------city")
        return False
    
    # If no country was extracted from generated address, it's an error
    if not gen_country:
        print("-------country")
        return False
    
    # Check if either city or country matches
    city_match = gen_city and seed_address_lower and gen_city == seed_address_lower
    country_match = gen_country and seed_address_lower and gen_country == seed_address_lower
    mapped_match = gen_country and seed_address_mapped and gen_country == seed_address_mapped

    
    if not (city_match or country_match or mapped_match):
        return False
    
    return True


if __name__ == "__main__":
    print(validate_address_region("Musée Océanographique, Avenue Saint-Martin, Monaco, 98000, Monaco", "Monaco"))