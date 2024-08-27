import datetime
import pytz
import random
import string
import base64

def generate_request_id():
    # Define the timezone for Africa/Lagos
    lagos_tz = pytz.timezone('Africa/Lagos')
    
    # Get the current date and time in the Africa/Lagos timezone
    now = datetime.datetime.now(lagos_tz)
    
    # Format the date and time as YYYYMMDDHHII
    request_id_prefix = now.strftime('%Y%m%d%H%M')
    
    # Generate a random alphanumeric string to concatenate with the prefix
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Concatenate the date prefix with the random alphanumeric suffix
    request_id = request_id_prefix + random_suffix
    
    return request_id

'''
# Example usage
request_id = generate_request_id()
print("Generated Request ID:", request_id)
'''

def get_basic_auth_header(username, password):
    # Concatenate username and password with a colon
    user_pass = f"{username}:{password}"
    
    # Encode the concatenated string using base64
    encoded_credentials = base64.b64encode(user_pass.encode()).decode()
    
    # Form the Authorization header
    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json'
    }
    return headers
'''
# Example usage
username = 'your_username'
password = 'your_password'
url = 'https://www.vtpass.com/api/v1/your_endpoint'

headers = get_basic_auth_header(username, password)

# Example request with the headers
response = requests.get(url, headers=headers)

print("Status Code:", response.status_code)
print("Response Body:", response.json())
'''