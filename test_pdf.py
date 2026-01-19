import requests

# Login credentials
LOGIN_URL = 'http://127.0.0.1:8000/accounts/login/'
PDF_URL = 'http://127.0.0.1:8000/export/pdf/'
USERNAME = 'admin'
PASSWORD = 'admin123'

client = requests.Session()

# 1. Get CSRF token
response = client.get(LOGIN_URL)
csrftoken = client.cookies['csrftoken']

# 2. Login
login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrftoken,
    'next': '/'
}
response = client.post(LOGIN_URL, data=login_data, headers={'Referer': LOGIN_URL})

if response.status_code == 200 and "Dashboard" in response.text:
    print("Login Successful")
else:
    # It might redirect to dashboard
    if response.url == 'http://127.0.0.1:8000/':
         print("Login Successful (Redirected)")
    else:
        print(f"Login Failed: {response.status_code}")
        exit()

# 3. Request PDF
response = client.get(PDF_URL)

print(f"PDF Status Code: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")

if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
    print("SUCCESS: PDF generated successfully.")
    with open('test_report.pdf', 'wb') as f:
        f.write(response.content)
    print("Saved to test_report.pdf")
else:
    print("FAILURE: Could not generate PDF.")
