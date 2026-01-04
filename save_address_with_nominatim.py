import requests
import json

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
        else:
            result = "failed"
    except Exception:
        result = "failed"
    
    with open("nominatim_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("Result saved to nominatim_result.json")
    return result

if __name__ == "__main__":
    address = "Regency Palace Hotel, Tarsheeha Street, Amman, Amman Sub-District, Amman Qasabah District, Amman, 11187, Jordan"
    save_address_with_nominatim(address)
