"""
proxy_server.py
Kakao Mobility API CORS 우회용 로컬 프록시 서버

[실행 방법]
  python proxy_server.py

[주의] Python 3 내장 모듈만 사용 - pip install 불필요!

서버 포트: 3001
브라우저에서 http://localhost:3001/directions?... 로 요청하면
이 서버가 Kakao Mobility API에 인증 헤더와 함께 실제 요청을 보내고
결과를 브라우저에 그대로 돌려줍니다.
"""

import http.server
import urllib.request
import urllib.parse
import json
from urllib.error import HTTPError, URLError

# ──────────────────────────────────────────
REST_API_KEY = "a491c4093faf6ff1903948840b8abe1f"
PORT = 3001
# ──────────────────────────────────────────


class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """로그 포맷 커스텀"""
        print(f"[프록시] {self.address_string()} - {format % args}")

    def _send_cors_headers(self, status=200, content_type="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_OPTIONS(self):
        """Preflight 요청 처리"""
        self._send_cors_headers(204)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path != "/directions":
            self._send_cors_headers(404)
            self.wfile.write(json.dumps({"error": "지원하지 않는 경로입니다."}).encode("utf-8"))
            return

        # Kakao Mobility API로 프록시
        query = parsed.query
        target_url = f"https://apis-navi.kakaomobility.com/v1/directions?{query}"
        print(f"[프록시] → {target_url}")

        req = urllib.request.Request(
            target_url,
            headers={
                "Authorization": f"KakaoAK {REST_API_KEY}",
                "Content-Type": "application/json",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(req) as response:
                body = response.read()
                status = response.status
                print(f"[프록시] ← 응답 상태: {status}")
                self._send_cors_headers(status)
                self.wfile.write(body)

        except HTTPError as e:
            body = e.read()
            print(f"[프록시] ← HTTP 에러: {e.code}")
            self._send_cors_headers(e.code)
            self.wfile.write(body)

        except URLError as e:
            print(f"[프록시] ← 연결 오류: {e.reason}")
            self._send_cors_headers(500)
            self.wfile.write(json.dumps({"error": str(e.reason)}).encode("utf-8"))


if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", PORT), ProxyHandler)
    print()
    print("=" * 45)
    print("  [Kakao Mobility Proxy Server]")
    print(f"  URL: http://127.0.0.1:{PORT}")
    print("=" * 45)
    print("  Live Server와 함께 이 창을 열어두세요.")
    print("  종료하려면 Ctrl+C 를 누르세요.")
    print("=" * 45)
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[프록시] 서버를 종료합니다.")
        server.shutdown()
