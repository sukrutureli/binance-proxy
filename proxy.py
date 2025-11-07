from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    # İstek "fapi/..." veya "api/..." ile başlıyorsa doğru Binance endpoint’ine yönlendir
    if path.startswith("fapi/"):
        base_url = "https://fapi.binance.com"
        sub_path = path[len("fapi/"):]
    elif path.startswith("api/"):
        base_url = "https://api.binance.com"
        sub_path = path[len("api/"):]
    else:
        return {"error": "Invalid path"}, 400

    target_url = f"{base_url}/{sub_path}"

    try:
        resp = requests.request(
            method=request.method,
            url=target_url,
            params=request.args,
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            timeout=10,
        )
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(resp.content, resp.status_code, headers)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
