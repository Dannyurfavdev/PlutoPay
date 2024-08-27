import requests

api_url = "https://www.vtpass.com/api/v1/airtime"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "phone": "08012345678",
    "amount": "1000",
    "network": "mtn"
}

response = requests.post(api_url, json=data, headers=headers)

if response.status_code == 200:
    print("Airtime purchased successfully")
    print(response.json())
else:
    print("Error:", response.status_code)
    print(response.json())

