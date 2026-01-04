import json
from check.looks_like_address import looks_like_address
from check.validate_address_region import validate_address_region

def check_addresses():
    with open("nominatim_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    checked_results = {}
    
    for country, addresses in data.items():
        valid_addresses = []
        
        for addr in addresses:
            display_name = addr.get("display_name", "")
            
            if not display_name:
                print(f"Skipped (no display_name): {country}")
                continue
            
            if not looks_like_address(display_name):
                print(f"Failed looks_like_address: {display_name[:50]}...")
                continue
            
            if not validate_address_region(display_name, country):
                print(f"Failed validate_address_region: {display_name[:50]}...")
                continue
            
            valid_addresses.append(addr)
            print(f"Valid: {display_name[:50]}...")
        
        if valid_addresses:
            checked_results[country] = valid_addresses
    
    with open("checked.json", "w", encoding="utf-8") as f:
        json.dump(checked_results, f, ensure_ascii=False, indent=2)
    
    print(f"\nChecked results saved to checked.json")

if __name__ == "__main__":
    check_addresses()
