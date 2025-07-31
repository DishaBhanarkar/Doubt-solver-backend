from flask import Flask, request, jsonify
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
TOGETHER_HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID")

@app.route('/ask', methods=['POST'])
def ask():
    try:
        print("📩 Received JSON:", request.json)
        user_question = request.json.get('question')
        question_type = request.json.get('type')

        if not user_question or not question_type:
            return jsonify({"answer": "Missing 'question' or 'type' in request."}), 400

        if question_type == "theory":
            print("🧠 Processing with Together.ai")

            payload = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI tutor."},
                    {"role": "user", "content": user_question}
                ],
                "temperature": 0.7
            }

            response = requests.post(TOGETHER_API_URL, headers=TOGETHER_HEADERS, json=payload)
            print("📡 Together Response:", response.status_code)

            if response.status_code != 200:
                return jsonify({"answer": f"Together.ai API error ({response.status_code}): {response.text}"}), 500

            try:
                result = response.json()
                answer = result['choices'][0]['message']['content']
            except Exception as e:
                answer = f"Error decoding Together.ai response: {str(e)}"

            return jsonify({"answer": answer})


        elif question_type == "equation":
            print("➗ Processing with Wolfram Alpha")
            wolfram_url = "http://api.wolframalpha.com/v2/query"
            params = {
                "input": f"step by step solution of {user_question}",  
                "appid": WOLFRAM_APP_ID,
                "output": "json"
            }

            response = requests.get(wolfram_url, params=params)

            if response.status_code != 200:
                return jsonify({"answer": f"Wolfram error ({response.status_code})"}), 500

            try:
                pods = response.json()['queryresult']['pods']
                output = ""

            
                for pod in pods:
                    if "step-by-step" in pod.get('title', '').lower():
                        for sub in pod.get('subpods', []):
                            output += sub.get('plaintext', '') + "\n"

            
                if not output.strip():
                    for pod in pods:
                        if pod.get('title', '').lower() in ["result", "solution", "definite integral"]:
                            for sub in pod.get('subpods', []):
                                output += sub.get('plaintext', '') + "\n"

                return jsonify({"answer": output.strip() or "Couldn't find a proper result."})
            except Exception as e:
                return jsonify({"answer": f"Error decoding Wolfram JSON: {str(e)}"}), 500


        else:
            return jsonify({"answer": "Invalid question type."}), 400

    except Exception as e:
        return jsonify({"answer": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)