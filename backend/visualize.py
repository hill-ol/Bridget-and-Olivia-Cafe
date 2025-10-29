import pandas as pd
import altair as alt

# Load results
df = pd.read_csv('cafe_studyability_scores.csv')

# Remove rows with no studyability score
df = df.dropna(subset=['studyability'])

# Chart 1: Bar chart of top cafes
bar = alt.Chart(df.head(10)).mark_bar().encode(
    x=alt.X('studyability:Q', title='Studyability Score (0-10)', scale=alt.Scale(domain=[0, 10])),
    y=alt.Y('name:N', sort='-x', title=''),
    color=alt.Color('studyability:Q', scale=alt.Scale(scheme='redyellowgreen'), legend=None),
    tooltip=['name', 'studyability', 'google_rating', 'noise', 'wifi', 'outlets']
).properties(
    title='Top 10 Study Spots Near Northeastern',
    width=600,
    height=400
)

bar.save('top_study_spots.html')
print("✓ Saved top_study_spots.html")

# Chart 2: Studyability vs Google Rating
scatter = alt.Chart(df).mark_circle(size=100).encode(
    x=alt.X('google_rating:Q', title='Google Rating', scale=alt.Scale(domain=[0, 5])),
    y=alt.Y('studyability:Q', title='Studyability Score', scale=alt.Scale(domain=[0, 10])),
    color=alt.Color('studyability:Q', scale=alt.Scale(scheme='redyellowgreen')),
    tooltip=['name', 'studyability', 'google_rating']
).properties(
    title='Studyability vs Google Rating',
    width=500,
    height=400
)

scatter.save('studyability_vs_rating.html')
print("✓ Saved studyability_vs_rating.html")

print("\n🎨 Open the HTML files to see your visualizations!")