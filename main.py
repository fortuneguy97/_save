import json
from pymongo import MongoClient


def extract_street_and_city(fulladdress: str) -> tuple:
    """
    Extract street name and city from full_address.
    
    Args:
        full_address: Full full_address string
        
    Returns:
        Tuple of (street_name, city)
    """
    if not fulladdress:
        return "", ""
    
    parts = [p.strip() for p in fulladdress.split(",")]
    
    # Street is typically the first or second part
    street_name = parts[0] if len(parts) > 0 else ""
    
    # City is typically before the postal code and country
    # Usually 2nd or 3rd from the end (before postal code and country)
    city = ""
    if len(parts) >= 3:
        # Try to find city (usually 3rd from end, before postal code and country)
        city = parts[-3] if len(parts) >= 3 else ""
    elif len(parts) >= 2:
        city = parts[-2]
    
    return street_name, city


def save_to_mongodb(json_file: str, country_code: str, country_name: str):
    """
    Save addresses from JSON file to MongoDB.
    
    Args:
        json_file: Path to JSON file containing addresses
        country_code: Country code (e.g., 'AD' for Andorra)
        country_name: Country name (e.g., 'Andorra')
    """
    mongodb_uri = "mongodb://admin:fjkfjrj!20020415@localhost:27017/address_db?authSource=admin"
    database_name = "address_db"
    collection_name = "address"
    
    # Load addresses from JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        addresses = json.load(f)
    
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)
    db = client[database_name]
    collection = db[collection_name]
    
    added_count = 0
    skipped_count = 0
    
    for addr_data in addresses:
        fulladdress = addr_data['fulladdress']
        street_name, city = extract_street_and_city(fulladdress)
        
        # Check if address already exists to avoid duplication
        existing = collection.find_one({"fulladdress": fulladdress})
        if existing:
            skipped_count += 1
            print(f"Skipped (duplicate): {fulladdress}")
            continue
        
        # Create document
        document = {
            "country": country_code,
            "country_name": country_name,
            "street_name": street_name,
            "city": city,
            "fulladdress": fulladdress,
            "status": 0,
            "worker_id": 97
        }
        
        # Insert document
        collection.insert_one(document)
        added_count += 1
        print(f"Added: {fulladdress}")
    
    client.close()
    
    print("-" * 80)
    print(f"Results: {added_count} added, {skipped_count} skipped (duplicates)")


if __name__ == "__main__":
    save_to_mongodb("cv_addresses.json", "CV", "Cabo Verde")
