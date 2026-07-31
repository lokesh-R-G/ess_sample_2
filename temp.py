import urllib.request, json, urllib.error
try:
    data = {"employeeCode": "EMP1234", "systemAccessEnabled": False, "essStatus": "Not Invited"}
    req = urllib.request.Request('http://localhost:8000/api/v2/employee/employees/', data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.code)
    print(e.read().decode())
