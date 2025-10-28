from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# API Keys (FREE APIs only - NO Pinterest for now)
FOURSQUARE_API_KEY = os.getenv('FOURSQUARE_API_KEY', '')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY', '')

# Home endpoint
@app.route('/')
def home():
    return jsonify({
        'message': 'Coffee Shop Finder API is running! ☕',
        'status': 'success',
        'apis_used': ['OpenStreetMap (FREE)', 'Foursquare (FREE)', 'Unsplash (FREE)'],
        'note': 'Pinterest integration coming soon!',
        'endpoints': {
            'nearby_cafes': '/api/cafes/nearby?lat=42.36&lng=-71.05',
            'search_cafes': '/api/cafes/search?query=starbucks&lat=42.36&lng=-71.05',
            'aesthetic_photos': '/api/aesthetic/photos?query=cozy cafe',
            'checkin': 'POST /api/checkin'
        }
    })

# Get nearby cafes using OpenStreetMap (FREE, no API key needed!)
@app.route('/api/cafes/nearby', methods=['GET'])
def get_nearby_cafes():
    lat = request.args.get('lat', '42.3601')  # Default: Boston
    lng = request.args.get('lng', '-71.0589')
    radius = request.args.get('radius', '2000')  # meters
    
    try:
        # Overpass API (OpenStreetMap) - completely FREE!
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Query for cafes within radius
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="cafe"](around:{radius},{lat},{lng});
          way["amenity"="cafe"](around:{radius},{lat},{lng});
        );
        out body;
        >;
        out skel qt;
        """
        
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
        data = response.json()
        
        cafes = []
        for element in data.get('elements', [])[:30]:  # Limit to 30 results
            if element.get('type') == 'node' and 'tags' in element:
                tags = element['tags']
                cafe = {
                    'id': str(element['id']),
                    'name': tags.get('name', 'Unknown Cafe'),
                    'address': tags.get('addr:street', '') + ' ' + tags.get('addr:housenumber', ''),
                    'lat': element['lat'],
                    'lng': element['lon'],
                    'cuisine': tags.get('cuisine', ''),
                    'opening_hours': tags.get('opening_hours', 'Unknown'),
                    'website': tags.get('website', ''),
                    'phone': tags.get('phone', ''),
                    'rating': 4.0  # Default rating
                }
                cafes.append(cafe)
        
        return jsonify({
            'success': True,
            'cafes': cafes,
            'count': len(cafes),
            'source': 'OpenStreetMap (FREE)'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Search cafes using Foursquare (FREE tier)
@app.route('/api/cafes/search', methods=['GET'])
def search_cafes():
    query = request.args.get('query', 'coffee')
    lat = request.args.get('lat', '42.3601')
    lng = request.args.get('lng', '-71.0589')
    
    if not FOURSQUARE_API_KEY:
        # Fallback to OpenStreetMap
        return get_nearby_cafes()
    
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            'Authorization': FOURSQUARE_API_KEY,
            'Accept': 'application/json'
        }
        params = {
            'query': query,
            'll': f'{lat},{lng}',
            'radius': 5000,
            'categories': '13035',  # Coffee shop category
            'limit': 30
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cafes = []
            
            for place in data.get('results', []):
                cafe = {
                    'id': place['fsq_id'],
                    'name': place['name'],
                    'address': place.get('location', {}).get('formatted_address', ''),
                    'lat': place.get('geocodes', {}).get('main', {}).get('latitude'),
                    'lng': place.get('geocodes', {}).get('main', {}).get('longitude'),
                    'categories': [cat['name'] for cat in place.get('categories', [])],
                    'rating': 4.0
                }
                cafes.append(cafe)
            
            return jsonify({
                'success': True,
                'cafes': cafes,
                'count': len(cafes),
                'source': 'Foursquare (FREE)'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Foursquare error: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get cafe details using Foursquare
@app.route('/api/cafes/<cafe_id>/details', methods=['GET'])
def get_cafe_details(cafe_id):
    if not FOURSQUARE_API_KEY:
        return jsonify({
            'success': False,
            'error': 'Foursquare API key not set'
        }), 400
    
    try:
        url = f"https://api.foursquare.com/v3/places/{cafe_id}"
        headers = {
            'Authorization': FOURSQUARE_API_KEY,
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'cafe': data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Foursquare error: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get aesthetic photos using Unsplash (INSTEAD of Pinterest for now)
@app.route('/api/aesthetic/photos', methods=['GET'])
def get_aesthetic_photos():
    query = request.args.get('query', 'cozy coffee shop aesthetic')
    
    if not UNSPLASH_ACCESS_KEY:
        return jsonify({
            'success': False,
            'error': 'Unsplash API key not set. Sign up at https://unsplash.com/developers'
        }), 400
    
    try:
        url = "https://api.unsplash.com/search/photos"
        headers = {
            'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'
        }
        params = {
            'query': query,
            'per_page': 20,
            'orientation': 'landscape'
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            photos = []
            
            for photo in data.get('results', []):
                photos.append({
                    'id': photo['id'],
                    'url': photo['urls']['regular'],
                    'thumbnail': photo['urls']['small'],
                    'photographer': photo['user']['name'],
                    'description': photo.get('description', ''),
                    'alt_description': photo.get('alt_description', '')
                })
            
            return jsonify({
                'success': True,
                'photos': photos,
                'count': len(photos),
                'source': 'Unsplash (Pinterest alternative)'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Unsplash error: {response.status_code}'
            }), response.status_code
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get aesthetic for specific cafe
@app.route('/api/cafes/<cafe_id>/aesthetic', methods=['GET'])
def get_cafe_aesthetic(cafe_id):
    """Get aesthetic photos matching the cafe's vibe"""
    # Use Unsplash instead of Pinterest for now
    query = request.args.get('query', 'cozy study coffee shop')
    return get_aesthetic_photos()

# Check-in to a cafe
@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json
    
    cafe_id = data.get('cafe_id')
    noise_level = data.get('noise_level')  # 1-5
    crowdedness = data.get('crowdedness')  # 1-5
    wifi_speed = data.get('wifi_speed')  # Mbps
    outlets_available = data.get('outlets_available', False)
    
    # TODO: Save to database when we add one
    
    return jsonify({
        'success': True,
        'message': 'Check-in recorded! ✅',
        'data': {
            'cafe_id': cafe_id,
            'noise_level': noise_level,
            'crowdedness': crowdedness,
            'wifi_speed': wifi_speed,
            'outlets_available': outlets_available
        }
    })

# Get check-ins for a cafe (mock data)
@app.route('/api/cafes/<cafe_id>/checkins', methods=['GET'])
def get_checkins(cafe_id):
    # Mock data - replace with database later
    mock_checkins = [
        {
            'noise_level': 3,
            'crowdedness': 2,
            'wifi_speed': 45,
            'outlets_available': True,
            'timestamp': '2 hours ago'
        },
        {
            'noise_level': 2,
            'crowdedness': 3,
            'wifi_speed': 52,
            'outlets_available': True,
            'timestamp': '5 hours ago'
        }
    ]
    
    return jsonify({
        'success': True,
        'cafe_id': cafe_id,
        'checkins': mock_checkins,
        'averages': {
            'noise_level': 2.5,
            'crowdedness': 2.5,
            'wifi_speed': 48.5
        }
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Coffee Shop Finder API Starting...")
    print("="*50)
    print("📍 Server: http://localhost:5000")
    print("🆓 Using FREE APIs:")
    print("   - OpenStreetMap (No key needed)")
    print("   - Foursquare (99k requests/month)")
    print("   - Unsplash (50 requests/hour)")
    print("📌 Pinterest: Coming soon!")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)