import json
import pandas as pd
import numpy as np

# Load your data
with open('northeastern_cafes.json', 'r') as f:
    cafes = json.load(f)

# Define aspect keywords
aspects = {
    'noise': {
        'positive': ['quiet', 'peaceful', 'calm', 'silent', 'tranquil', 'library',
                     'very chill', 'atmosphere is chill', 'relaxed atmosphere', 'relaxing break', 
                     'relaxed vibe', 'relaxed european coffee shop experience', 'more relaxed'],
        'negative': ['loud', 'noisy', 'chaotic', 'bustling', 'crowded noise', 'blasting music', 'busy',
                     'busyness and bustle', 'busy and bustling', 'very busy', 'can get busy', 'super fast-paced']
    },
    'wifi': {
        'positive': ['fast wifi', 'good wifi', 'great wifi', 'reliable wifi', 'strong connection', 'wifi works', 'free wifi',
                     'wifi password', 'strong wifi', 'wifi works great'],
        'negative': ['slow wifi', 'bad wifi', 'poor wifi', 'spotty wifi', 'no wifi', 'wifi down', 'do not have WiFi']
    },
    'outlets': {
        'positive': ['plenty of outlets', 'lots of outlets', 'outlets everywhere', 'charging stations', 'easy to charge', 'plugins'],
        'negative': ['no outlets', 'limited outlets', 'few outlets', 'hard to find outlets', 'need outlets']
    },
    'seating': {
        'positive': ['plenty of seating', 'lots of space', 'spacious', 'comfortable seats', 'cozy', 'comfortable', 'a lot of outdoor seating', 'ample seating',
                     'variety of seating options', 'cozy sitting chairs', 'comfortable interior', 'great outdoor seating', 
                     'good outdoor seating', 'outdoor space', 'terrace seating', 'two levels of seating', '2 levels of seating', 'well laid-out'],
        'negative': ['cramped', 'crowded', 'limited seating', 'no seats', 'hard to find seat', 'packed', 'wasnt a lot of seating','small','no seating',
                     'not a lot of seating', 'can get busy', 'hard to find a seat']
    },
    'study_friendly': {
        'positive': ['good for studying', 'study spot', 'work from here', 'laptop friendly', 'productive', 'focus', 'open late', 
                     'comfortable spot to work or study','peaceful space to work or study','perfect spot for a work session',
                     'place to meet with team members', 'great place for study groups', 'come here to study','perfect for having work done',
                     'ultimate third space for cramming studying or work','corner to work','place to study','relax yourself with reading or studying',
                     'quite enough to talk with friend or just do your work','Good spot to get some work done',
                     'people working on laptops', 'working on laptops', 'people working', 'spend an afternoon reading', 
                     'spend an afternoon journaling', 'reading or journaling', 'relax for hours', 'can relax for hours', 'spend time', 
                     'great place to spend time', 'perfect place to work','good place to work', 'work from'],
        'negative': ['not for studying', 'too social', 'distracting', 'hard to focus', 'not work friendly','not a place for studying', 
                     'not for working', 'too busy to work', 'hard to concentrate', 'not a work spot']
    },
    'atmosphere': {
        'positive': ['bright', 'sunny', 'natural light', 'gorgeous lighting', 'well-lit', 'good lighting', 'cozy atmosphere',
                     'comfortable atmosphere', 'relaxed vibe', 'chill vibe', 'lighting is gorgeous', 'bright space', 
                     'sunny windows', 'bright and airy', 'beautiful view', 'chill atmosphere', 'vibey', 'polished', 'sophisticated'],
        'negative': ['dark', 'dim', 'poor lighting', 'too bright', 'harsh lighting', 'uncomfortable atmosphere']
    }
}

def find_aspect_mentions(text, aspect_keywords):
    """Find which keywords are mentioned in a review"""
    text_lower = text.lower()
    mentions = {
        'positive': [],
        'negative': []
    }
    
    for keyword in aspect_keywords['positive']:
        if keyword in text_lower:
            mentions['positive'].append(keyword)
    
    for keyword in aspect_keywords['negative']:
        if keyword in text_lower:
            mentions['negative'].append(keyword)
    
    return mentions

def score_aspect(reviews, aspect_keywords):
    """Score an aspect based on positive/negative keyword mentions"""
    positive_count = 0
    negative_count = 0
    
    # Combine all review texts
    all_text = ' '.join([r['text'].lower() for r in reviews])
    
    # Count positive mentions
    for keyword in aspect_keywords['positive']:
        positive_count += all_text.count(keyword)
    
    # Count negative mentions
    for keyword in aspect_keywords['negative']:
        negative_count += all_text.count(keyword)
    
    # If aspect not mentioned, return None
    if positive_count + negative_count == 0:
        return None
    
    # Convert to 0-10 scale
    ratio = positive_count / (positive_count + negative_count)
    score = ratio * 10
    
    return round(score, 1)

def calculate_studyability(aspect_scores, google_rating):
    """
    Calculate overall studyability score combining aspect analysis and Google rating
    
    Weighting:
    - 70% from aspect scores (study-specific features)
    - 30% from Google rating (general quality/experience)
    """
    valid_scores = [s for s in aspect_scores.values() if s is not None]
    
    # If we have aspect scores, use weighted combination
    if valid_scores and google_rating:
        aspect_avg = np.mean(valid_scores)
        google_normalized = (google_rating / 5.0) * 10  # Convert 5-star to 10-point scale
        
        # Weighted average: 70% aspects, 30% Google rating
        studyability = (0.7 * aspect_avg) + (0.3 * google_normalized)
        return round(studyability, 1)
    
    # If only aspect scores available
    elif valid_scores:
        return round(np.mean(valid_scores), 1)
    
    # If only Google rating available
    elif google_rating:
        return round((google_rating / 5.0) * 10, 1)
    
    # No data at all
    return None

def analyze_review(review_text):
    """Analyze a single review for all aspects"""
    analysis = {}
    
    for aspect_name, keywords in aspects.items():
        mentions = find_aspect_mentions(review_text, keywords)
        
        # Only include if there are mentions
        if mentions['positive'] or mentions['negative']:
            analysis[aspect_name] = mentions
    
    return analysis

# Analyze all cafes
results = []
detailed_results = []

print("Analyzing cafes...\n")

for cafe in cafes:
    print(f"Analyzing: {cafe['name']}")
    
    # Calculate aspect scores
    scores = {}
    for aspect_name, keywords in aspects.items():
        scores[aspect_name] = score_aspect(cafe['reviews'], keywords)
    
    # Calculate overall studyability including Google rating
    studyability = calculate_studyability(scores, cafe.get('rating'))
    
    # Analyze individual reviews
    analyzed_reviews = []
    for review in cafe['reviews']:
        review_analysis = analyze_review(review['text'])
        
        analyzed_reviews.append({
            'author': review['author'],
            'rating': review['rating'],
            'text': review['text'],
            'time': review['time'],
            'aspect_mentions': review_analysis
        })
    
    # Store summary results for CSV
    results.append({
        'name': cafe['name'],
        'address': cafe['address'],
        'studyability': studyability,
        'noise': scores['noise'],
        'wifi': scores['wifi'],
        'outlets': scores['outlets'],
        'seating': scores['seating'],
        'study_friendly': scores['study_friendly'],
        'atmosphere': scores['atmosphere'],
        'google_rating': cafe['rating'],
        'num_reviews': len(cafe['reviews']),
        'lat': cafe['lat'],
        'lng': cafe['lng']
    })
    
    # Store detailed results with reviews for JSON
    detailed_results.append({
        'name': cafe['name'],
        'address': cafe['address'],
        'lat': cafe['lat'],
        'lng': cafe['lng'],
        'google_rating': cafe['rating'],
        'total_ratings': cafe.get('total_ratings'),
        'studyability_score': studyability,
        'aspect_scores': {
            'noise': scores['noise'],
            'wifi': scores['wifi'],
            'outlets': scores['outlets'],
            'seating': scores['seating'],
            'study_friendly': scores['study_friendly'],
            'atmosphere': scores['atmosphere']
        },
        'reviews': analyzed_reviews,
        'review_count': len(analyzed_reviews)
    })

# Create DataFrame for CSV
df = pd.DataFrame(results)

# Sort by studyability score
df_sorted = df.sort_values('studyability', ascending=False, na_position='last')

# Save CSV (summary scores)
df_sorted.to_csv('cafe_studyability_scores.csv', index=False)

# Sort detailed results by studyability too
detailed_sorted = sorted(
    detailed_results, 
    key=lambda x: x['studyability_score'] if x['studyability_score'] is not None else -1,
    reverse=True
)

# Save JSON (full data with reviews)
with open('cafe_studyability_detailed.json', 'w') as f:
    json.dump(detailed_sorted, f, indent=2)

print("\n" + "="*60)
print("ANALYSIS COMPLETE!")
print("="*60)

# Show top 10
print("\n🏆 TOP 10 STUDY SPOTS:\n")
top_10 = df_sorted.head(10)

for i, row in enumerate(top_10.itertuples(), 1):
    if pd.notna(row.studyability):
        print(f"{i:2d}. {row.name:40s} Score: {row.studyability}/10 (Google: {row.google_rating}⭐)")
    else:
        print(f"{i:2d}. {row.name:40s} Score: N/A (not enough data)")

print(f"\n✓ Summary scores saved to: cafe_studyability_scores.csv")
print(f"✓ Detailed data with reviews saved to: cafe_studyability_detailed.json")

# Show scoring breakdown for top cafe
print("\n" + "="*60)
print("SCORING BREAKDOWN (Top Cafe):")
print("="*60)

if detailed_sorted:
    sample = detailed_sorted[0]
    print(f"\nCafe: {sample['name']}")
    print(f"Overall Studyability Score: {sample['studyability_score']}/10")
    print(f"\nScore Components:")
    print(f"  Google Rating: {sample['google_rating']}/5 ⭐")
    print(f"\n  Aspect Scores:")
    for aspect, score in sample['aspect_scores'].items():
        if score is not None:
            print(f"    {aspect.capitalize():15} {score}/10")
        else:
            print(f"    {aspect.capitalize():15} No data")
    
    print(f"\n  Formula: 70% aspect scores + 30% Google rating")
    print(f"  Reviews analyzed: {sample['review_count']}")