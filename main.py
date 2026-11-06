from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import os

class SimpleProxy(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            req_json = json.loads(post_data.decode('utf-8'))
            user_messages = req_json.get("messages", [])
            
            # OpenAI API को रिक्वेस्ट भेजना
            api_key = os.getenv('PRIMARY_API_KEY', 'your-api-key-here')
            req_body = json.dumps({
                "model": "gpt-4o-mini",
                "messages": user_messages
            }).encode('utf-8')
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=req_body,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = response.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(res_data)
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = json.dumps({"error": str(e)}).encode('utf-8')
            self.wfile.write(error_response)

def run():
    # क्लाउड द्वारा दिए गए पोर्ट या डिफ़ॉल्ट 3000 का इस्तेमाल
    port = int(os.environ.get("PORT", 3000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleProxy)
    print(f"गेटवे पोर्ट {port} पर शुरू हो गया है...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
