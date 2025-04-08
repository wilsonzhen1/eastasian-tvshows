import requests
import csv
import time
import os

# Read API key from environment variable
API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL_DISCOVER = 'https://api.themoviedb.org/3/discover/tv'
BASE_URL_DETAIL = 'https://api.themoviedb.org/3/tv/'

# Target languages: Korean, Chinese, Japanese
LANG_CODES = {
    'Korean': 'ko',
    'Chinese': 'zh',
    'Japanese': 'ja'
}

START_YEAR = '1980-01-01'  # Only shows first aired since Jan 1, 1980

all_shows = []

for lang_name, lang_code in LANG_CODES.items():
    page = 1
    while True:
        discover_params = {
            'api_key': API_KEY,
            'with_original_language': lang_code,
            'sort_by': 'popularity.desc',
            'first_air_date.gte': START_YEAR,
            'page': page
        }
        response = requests.get(BASE_URL_DISCOVER, params=discover_params)
        if response.status_code != 200:
            print(f"❌ Failed to fetch page {page} for {lang_name}: {response.text}")
            break
        data = response.json()

        shows = data.get('results', [])
        if not shows:
            break  # No more shows

        for show in shows:
            tv_id = show['id']
            name = show.get('name', '')
            original_lang = show.get('original_language', '')
            overview = show.get('overview', '')
            popularity = show.get('popularity', 0)
            first_air_date = show.get('first_air_date', '')

            # Get detailed info
            detail_params = {'api_key': API_KEY}
            detail_resp = requests.get(f"{BASE_URL_DETAIL}{tv_id}", params=detail_params)
            if detail_resp.status_code != 200:
                print(f"❌ Failed to fetch detail for TV ID {tv_id}: {detail_resp.text}")
                continue
            detail = detail_resp.json()

            episode_count = sum(season.get('episode_count', 0) for season in detail.get('seasons', []))
            season_count = len(detail.get('seasons', []))

            all_shows.append({
                'id': tv_id,
                'name': name,
                'language': lang_name,
                'original_language': original_lang,
                'first_air_date': first_air_date,
                'overview': overview,
                'popularity': popularity,
                'episode_count': episode_count,
                'season_count': season_count
            })

            time.sleep(0.25)  # Respect TMDB rate limits

        page += 1  # Next page

# Write results to CSV
output_filename = 'east_asian_tvshows.csv'
with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'name', 'language', 'original_language', 'first_air_date',
                  'overview', 'popularity', 'episode_count', 'season_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for show in all_shows:
        writer.writerow(show)

print(f"✅ CSV file created: {output_filename}")

