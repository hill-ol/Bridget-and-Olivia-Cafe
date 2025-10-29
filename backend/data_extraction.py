import requests
import json
import time

# Your API key from Google Cloud Console
GOOGLE_API_KEY = "AIzaSyAdjPwgFROOQsvMWGrqIZaoOO_h1TX4Wq0"

def search_nearby_cafes(lat, lon, radius=2000):
    """Search for cafes near a location"""
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    params = {
        "location": f"{lat},{lon}",
        "radius": radius,
        "keyword": "coffee shop study",  
        "type": "cafe",
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] != 'OK':
        print(f"Error: {data['status']}")
        if 'error_message' in data:
            print(f"Message: {data['error_message']}")
        return []
    
    return data['results']

def get_place_details(place_id):
    """Get detailed info including reviews for a specific place"""
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "place_id": place_id,
        "fields": "name,rating,reviews,formatted_address,geometry,price_level,user_ratings_total,opening_hours",
        "key": GOOGLE_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data['status'] == 'OK':
        return data['result']
    
    return None

# Northeastern coordinates
NEU_LAT = 42.3398
NEU_LON = -71.0892

print("Searching for cafes near Northeastern...")
cafes = search_nearby_cafes(NEU_LAT, NEU_LON, radius=2000)

print(f"Found {len(cafes)} cafes\n")

# Get detailed info for each cafe
all_cafe_data = []

for i, cafe in enumerate(cafes, 1):
    print(f"{i}/{len(cafes)}: Getting details for {cafe['name']}...")
    
    details = get_place_details(cafe['place_id'])
    
    if details:
        cafe_info = {
            'name': details.get('name'),
            'address': details.get('formatted_address'),
            'lat': details['geometry']['location']['lat'],
            'lng': details['geometry']['location']['lng'],
            'rating': details.get('rating'),
            'total_ratings': details.get('user_ratings_total'),
            'price_level': details.get('price_level'),
            'reviews': []
        }
        
        # Extract reviews
        if 'reviews' in details:
            for review in details['reviews']:
                cafe_info['reviews'].append({
                    'author': review.get('author_name'),
                    'rating': review.get('rating'),
                    'text': review.get('text'),
                    'time': review.get('time')
                })
        
        all_cafe_data.append(cafe_info)
        
        print(f"  ✓ {len(cafe_info['reviews'])} reviews")
    
    # Be nice to the API - wait between requests
    time.sleep(0.5)

# Save to file
with open('northeastern_cafes.json', 'w') as f:
    json.dump(all_cafe_data, f, indent=2)

print(f"\n{'='*60}")
print(f"✓ Saved {len(all_cafe_data)} cafes to northeastern_cafes.json")

# Summary stats
total_reviews = sum(len(cafe['reviews']) for cafe in all_cafe_data)
print(f"✓ Total reviews: {total_reviews}")
if all_cafe_data:
    print(f"✓ Average reviews per cafe: {total_reviews / len(all_cafe_data):.1f}")
print(f"{'='*60}")

# Show first cafe
if all_cafe_data:
    print("\nFirst cafe:")
    print(f"Name: {all_cafe_data[0]['name']}")
    print(f"Address: {all_cafe_data[0]['address']}")
    print(f"Rating: {all_cafe_data[0]['rating']}")
    print(f"Reviews: {len(all_cafe_data[0]['reviews'])}")
    if all_cafe_data[0]['reviews']:
        print(f"\nFirst review text:")
        print(all_cafe_data[0]['reviews'][0]['text'][:200] + "...")

        