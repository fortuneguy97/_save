import requests
import json
import time

def save_address_with_nominatim(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "accept-language": "en",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "address/1.0 (Windows; Contact: declemon0907@gmail.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data:
            item = data[0]
            address_details = item.get("address", {})
            result = {
                "display_name": item.get("display_name"),
                "city": address_details.get("city") or address_details.get("town") or address_details.get("village") or address_details.get("state"),
                "street": address_details.get("road") or address_details.get("street")
            }
            return result
        else:
            return None
    except Exception:
        return None

if __name__ == "__main__":
    with open("addresses.json", "r", encoding="utf-8") as f:
        addresses_data = json.load(f)
    
    results = {}
    
    for country, addresses in addresses_data.items():
        if not addresses:
            continue
        
        country_results = []
        for addr_obj in addresses:
            address = addr_obj.get("address", "")
            result = save_address_with_nominatim(address)
            
            if result and result.get("display_name"):
                country_results.append(result)
                print(f"Saved: {address[:50]}...")
            else:
                print(f"Skipped (no result): {address[:50]}...")
            
            time.sleep(1)  # Respect Nominatim rate limit
        
        if country_results:
            results[country] = country_results
    
    with open("nominatim_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\nResults saved to nominatim_result.json")
