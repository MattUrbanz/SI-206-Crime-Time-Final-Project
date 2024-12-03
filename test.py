API_BASE_URL = 'https://api.usa.gov/crime/fbi/cde/hate-crime/state/'
API_KEY = '1MriSHUQ3jGzF9vvb3pLRqqSinNoZ6jIElx984Ee'  # Replace with your API key from data.gov
state = 'CA'

url = f"{API_BASE_URL}{state}"
og_url = 'https://api.usa.gov/crime/fbi/cde/hate-crime/state/CA'
print(url)
print(og_url)