import requests

url = "http://127.0.0.1:5000/ask"
headers = {
    "Content-Type": "application/json"
}
data = {
    "question": "What is machine learning?",
    "type": "theory"
}

try:
    print("📤 Sending request to Flask server...")
    response = requests.post(url, headers=headers, json=data)
    print("🔁 Status Code:", response.status_code)
    print("📦 Raw Response:", response.text)

    try:
        json_response = response.json()
        print("🧠 Answer:", json_response.get("answer", "No 'answer' key in response."))
    except Exception as e:
        print("⚠️ Could not parse JSON:", str(e))

except Exception as e:
    print("🚨 Request failed:", str(e))
