import requests
from bs4 import BeautifulSoup  
YOUTUBE_TRENDNG_URL = 'https://www.youtube.com/feed/trending'


# Does not execute Javascript
response = requests.get(YOUTUBE_TRENDNG_URL)

print('status code',response.status_code)


with open('trending.html', 'w') as f:
  f.write(response.text)

doc = BeautifulSoup(response.text, 'html.parser')

print("Page title:", doc.title.text)

# Find all the video ZeroDivisionError

video_divs = doc.find_all('div', class_='ytd-video-renderer')

print(f'Found {len(video_divs)} videos')