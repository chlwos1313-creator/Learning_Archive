/**
 * proxy-server.js
 * Kakao Mobility API CORS 우회용 로컬 프록시 서버
 *
 * [실행 방법]
 *   node proxy-server.js
 *
 * [주의] Node.js 내장 모듈만 사용 - npm install 불필요!
 *
 * 서버 포트: 3001
 * 브라우저에서 http://localhost:3001/directions?... 으로 요청하면
 * 이 서버가 Kakao Mobility API에 인증 헤더와 함께 실제 요청을 보내고
 * 결과를 브라우저에 그대로 돌려줍니다.
 */

const http  = require('http');
const https = require('https');
const url   = require('url');

// apikey.js에서 직접 키를 가져올 수 없으므로 여기에 직접 입력
const REST_API_KEY = 'a491c4093faf6ff1903948840b8abe1f';
const PORT = 3001;

const server = http.createServer((req, res) => {

  // ── CORS 허용 헤더 (Live Server http://127.0.0.1:5500 허용) ──
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Preflight 요청(OPTIONS) 처리
  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const parsedUrl = url.parse(req.url, true);
  const pathname  = parsedUrl.pathname;

  // ── /directions 경로만 프록시 처리 ──
  if (req.method === 'GET' && pathname === '/directions') {
    const query = parsedUrl.search || '';   // ?origin=...&destination=... 부분

    const options = {
      hostname: 'apis-navi.kakaomobility.com',
      path: `/v1/directions${query}`,
      method: 'GET',
      headers: {
        'Authorization': `KakaoAK ${REST_API_KEY}`,
        'Content-Type' : 'application/json'
      }
    };

    console.log(`[프록시] 요청 전달: ${options.hostname}${options.path}`);

    const proxyReq = https.request(options, (proxyRes) => {
      let body = '';
      proxyRes.setEncoding('utf8');
      proxyRes.on('data', chunk => { body += chunk; });
      proxyRes.on('end', () => {
        console.log(`[프록시] 응답 수신 - 상태: ${proxyRes.statusCode}`);
        res.writeHead(proxyRes.statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(body);
      });
    });

    proxyReq.on('error', (err) => {
      console.error('[프록시] 요청 오류:', err.message);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    });

    proxyReq.end();

  } else {
    // 다른 경로는 404
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: '지원하지 않는 경로입니다.' }));
  }
});

server.listen(PORT, '127.0.0.1', () => {
  console.log('');
  console.log('========================================');
  console.log('  🚗 카카오 모빌리티 프록시 서버 실행 중');
  console.log(`  URL: http://127.0.0.1:${PORT}`);
  console.log('========================================');
  console.log('  Live Server와 함께 이 창을 열어두세요.');
  console.log('  종료하려면 Ctrl+C 를 누르세요.');
  console.log('========================================');
  console.log('');
});
