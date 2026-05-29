/**
 * main.js - 은행 검색 지도 서비스 메인 로직
 * NF1003: JS 분리 구조
 *
 * 기능:
 *  - F1002: Kakao Map API 지도 표시 (중심: 강남역)
 *  - F1003: 광역시/도, 시/군/구, 은행명 드롭다운
 *  - F1004: 은행 검색 + 마커 + 인포윈도우
 *  - F1011: Kakao Mobility API 길찾기 (멀티캠퍼스 → 선택 은행)
 */

// ── 상수 ──────────────────────────────────────────
// 멀티캠퍼스 강남 캠퍼스 좌표 (출발지)
const MULTICAMPUS = {
  lat: 37.5012743,
  lng: 127.0396597,
  name: "멀티캠퍼스 강남"
};

// 강남역 좌표 (지도 초기 중심)
const GANGNAM_STATION = {
  lat: 37.4979517,
  lng: 127.0276188
};

// ── 전역 상태 ──────────────────────────────────────
let map = null;               // 카카오 맵 인스턴스
let markers = [];             // 현재 표시된 마커 배열
let infowindows = [];         // 인포윈도우 배열
let selectedMarkerIndex = -1; // 선택된 마커 인덱스
let routePolylines = [];      // 길찾기 폴리라인 배열
let selectedPlace = null;     // 선택된 장소 정보

// ── 초기화 ────────────────────────────────────────
// index.html의 kakao.maps.load() 콜백에서 호출됨
// (Kakao SDK 완전 로드 보장 후 실행)
function initApp() {
  initMap();
  initDropdowns();
  bindEvents();
}

/**
 * F1002: 카카오 맵 초기화 (중심: 강남역)
 */
function initMap() {
  const container = document.getElementById('map');
  const options = {
    center: new kakao.maps.LatLng(GANGNAM_STATION.lat, GANGNAM_STATION.lng),
    level: 4
  };
  map = new kakao.maps.Map(container, options);

  // 지도 컨트롤 추가
  const zoomControl = new kakao.maps.ZoomControl();
  map.addControl(zoomControl, kakao.maps.ControlPosition.RIGHT);

  const mapTypeControl = new kakao.maps.MapTypeControl();
  map.addControl(mapTypeControl, kakao.maps.ControlPosition.TOPRIGHT);

  // 멀티캠퍼스 마커 (출발지 고정 표시)
  addCampusMarker();
}

/**
 * 멀티캠퍼스 고정 마커 추가
 */
function addCampusMarker() {
  const campusPos = new kakao.maps.LatLng(MULTICAMPUS.lat, MULTICAMPUS.lng);

  // 커스텀 이미지 마커 (캠퍼스)
  const campusMarker = new kakao.maps.Marker({
    position: campusPos,
    map: map,
    title: MULTICAMPUS.name,
    image: new kakao.maps.MarkerImage(
      'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
      new kakao.maps.Size(24, 35)
    ),
    zIndex: 10
  });

  const campusInfo = new kakao.maps.InfoWindow({
    content: `<div style="padding:8px 12px;font-size:13px;font-weight:700;color:#3B5BDB;white-space:nowrap;">
                📍 ${MULTICAMPUS.name}
              </div>`
  });

  kakao.maps.event.addListener(campusMarker, 'click', () => {
    campusInfo.open(map, campusMarker);
  });
}

/**
 * F1003: 드롭다운 초기화 (data.json 활용)
 */
function initDropdowns() {
  const citySelect   = document.getElementById('city-select');
  const distSelect   = document.getElementById('district-select');
  const bankSelect   = document.getElementById('bank-select');

  // 광역시/도 목록 채우기
  mapInfo.forEach((region, idx) => {
    const opt = document.createElement('option');
    opt.value = idx;
    opt.textContent = region.name;
    citySelect.appendChild(opt);
  });

  // 은행 목록 채우기
  bankInfo.forEach(bank => {
    const opt = document.createElement('option');
    opt.value = bank;
    opt.textContent = bank;
    bankSelect.appendChild(opt);
  });

  // 광역시/도 변경 시 → 시/군/구 업데이트
  citySelect.addEventListener('change', () => {
    updateDistrictOptions(citySelect.value, distSelect);
  });
}

/**
 * 시/군/구 드롭다운 업데이트
 */
function updateDistrictOptions(regionIdx, distSelect) {
  distSelect.innerHTML = '<option value="">-- 시/군/구 선택 --</option>';
  distSelect.disabled = true;

  if (regionIdx === '') return;

  const region = mapInfo[parseInt(regionIdx)];
  region.countries.forEach(dist => {
    const opt = document.createElement('option');
    opt.value = dist;
    opt.textContent = dist;
    distSelect.appendChild(opt);
  });
  distSelect.disabled = false;
}

/**
 * 이벤트 바인딩
 */
function bindEvents() {
  document.getElementById('search-btn').addEventListener('click', handleSearch);
  document.getElementById('route-btn').addEventListener('click', handleRoute);
  document.getElementById('route-close').addEventListener('click', closeRoutePanel);
}

// ── F1004: 은행 검색 & 마커 표시 ──────────────────

/**
 * 검색 버튼 핸들러
 */
function handleSearch() {
  const cityIdx  = document.getElementById('city-select').value;
  const district = document.getElementById('district-select').value;
  const bank     = document.getElementById('bank-select').value;

  if (!cityIdx) { showToast('광역시/도를 선택해주세요.', 'error'); return; }
  if (!district) { showToast('시/군/구를 선택해주세요.', 'error'); return; }
  if (!bank)    { showToast('은행을 선택해주세요.', 'error'); return; }

  const cityName = mapInfo[parseInt(cityIdx)].name;
  const keyword  = `${cityName} ${district} ${bank}`;

  clearMarkers();
  clearRoutePanel();
  selectedPlace = null;
  document.getElementById('route-btn').disabled = true;

  showLoading(true);
  searchPlaces(keyword);
}

/**
 * Kakao 장소 검색 API 호출
 */
function searchPlaces(keyword) {
  const ps = new kakao.maps.services.Places();
  ps.keywordSearch(keyword, (data, status) => {
    showLoading(false);
    if (status === kakao.maps.services.Status.OK) {
      displayResults(data);
    } else if (status === kakao.maps.services.Status.ZERO_RESULT) {
      showToast('검색 결과가 없습니다.', 'error');
      showEmptyResults();
    } else {
      showToast('검색 중 오류가 발생했습니다.', 'error');
    }
  }, { size: 15 });
}

/**
 * 검색 결과 표시 (마커 + 사이드바 리스트)
 */
function displayResults(places) {
  const bounds = new kakao.maps.LatLngBounds();
  const resultList = document.getElementById('result-list');
  const resultHeader = document.getElementById('result-header');

  resultList.innerHTML = '';
  resultHeader.innerHTML = `
    <span>검색 결과</span>
    <span class="result-count">${places.length}개</span>
  `;

  places.forEach((place, idx) => {
    const pos = new kakao.maps.LatLng(place.y, place.x);
    bounds.extend(pos);

    // 마커 생성
    const marker = createMarker(pos, idx + 1);
    markers.push(marker);

    // 인포윈도우 생성
    const iw = createInfoWindow(place, idx + 1);
    infowindows.push(iw);

    // 마커 클릭 이벤트
    kakao.maps.event.addListener(marker, 'click', () => {
      openInfoWindow(idx);
      highlightResultItem(idx);
      scrollToResultItem(idx);
    });

    // 결과 카드 생성
    const item = createResultItem(place, idx);
    resultList.appendChild(item);
  });

  // 지도 범위 조정
  map.setBounds(bounds);
  showToast(`${places.length}개의 은행을 찾았습니다.`, 'success');
}

/**
 * 번호 마커 이미지 생성
 */
function createMarker(position, number) {
  const imageSrc = `https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_number_blue.png`;
  const imageSize = new kakao.maps.Size(36, 37);
  const spriteSize = new kakao.maps.Size(36, 691);
  const spriteOrigin = new kakao.maps.Point(0, (number - 1) * 46 + 10);

  // 번호 마커 이미지 (스프라이트)
  const markerImg = new kakao.maps.MarkerImage(imageSrc, imageSize, {
    spriteSize, spriteOrigin
  });

  return new kakao.maps.Marker({
    position,
    map,
    image: markerImg,
    zIndex: 5
  });
}

/**
 * 인포윈도우 생성
 */
function createInfoWindow(place, number) {
  const content = `
    <div style="
      padding: 10px 14px;
      min-width: 200px;
      font-family: 'Noto Sans KR', sans-serif;
      line-height: 1.6;
    ">
      <div style="
        font-size: 14px;
        font-weight: 700;
        color: #1A1F36;
        margin-bottom: 4px;
        display:flex;
        align-items:center;
        gap:6px;
      ">
        <span style="
          background:#3B5BDB;
          color:#fff;
          border-radius:50%;
          width:20px;height:20px;
          display:inline-flex;
          align-items:center;justify-content:center;
          font-size:11px;font-weight:700;
          flex-shrink:0;
        ">${number}</span>
        ${place.place_name}
      </div>
      <div style="font-size:12px;color:#5A6478;margin-bottom:2px;">
        📍 ${place.road_address_name || place.address_name}
      </div>
      ${place.phone ? `<div style="font-size:12px;color:#5A6478;">📞 ${place.phone}</div>` : ''}
    </div>
  `;
  return new kakao.maps.InfoWindow({ content, removable: true });
}

/**
 * 인포윈도우 열기 (하나만 열리도록)
 */
function openInfoWindow(idx) {
  infowindows.forEach((iw, i) => {
    if (i === idx) {
      iw.open(map, markers[idx]);
      map.panTo(markers[idx].getPosition());
    } else {
      iw.close();
    }
  });
  selectedMarkerIndex = idx;
}

/**
 * 결과 카드 아이템 생성
 */
function createResultItem(place, idx) {
  const item = document.createElement('div');
  item.className = 'result-item';
  item.id = `result-item-${idx}`;
  item.innerHTML = `
    <div class="result-name">${place.place_name}</div>
    <div class="result-address">${place.road_address_name || place.address_name}</div>
    ${place.phone ? `<div class="result-address">📞 ${place.phone}</div>` : ''}
    <span class="result-badge">${idx + 1}</span>
  `;
  item.addEventListener('click', () => {
    openInfoWindow(idx);
    highlightResultItem(idx);
    selectedPlace = place;
    document.getElementById('route-btn').disabled = false;
    showToast(`${place.place_name} 선택됨. 길찾기를 눌러보세요!`, 'success');
  });
  return item;
}

/**
 * 선택된 결과 카드 강조
 */
function highlightResultItem(idx) {
  document.querySelectorAll('.result-item').forEach((el, i) => {
    el.classList.toggle('active', i === idx);
  });
  selectedMarkerIndex = idx;
}

function scrollToResultItem(idx) {
  const el = document.getElementById(`result-item-${idx}`);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showEmptyResults() {
  const resultList = document.getElementById('result-list');
  const resultHeader = document.getElementById('result-header');
  resultHeader.innerHTML = '';
  resultList.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">🏦</div>
      <div class="empty-text">검색 결과가 없습니다.<br>다른 조건으로 검색해보세요.</div>
    </div>
  `;
}

// ── F1011: Kakao Mobility API 길찾기 ──────────────

/**
 * 길찾기 버튼 핸들러
 * 로컬 프록시 서버(proxy-server.js, port 3001)를 경유해 Kakao Mobility API 호출
 * → node proxy-server.js 를 먼저 실행해야 합니다.
 */
function handleRoute() {
  if (!selectedPlace) {
    showToast('먼저 결과에서 은행을 선택해주세요.', 'error');
    return;
  }

  const origin = `${MULTICAMPUS.lng},${MULTICAMPUS.lat}`;
  const dest   = `${selectedPlace.x},${selectedPlace.y}`;

  // 로컬 프록시 서버 URL (proxy-server.js가 3001 포트에서 실행되어야 함)
  const proxyUrl = `http://127.0.0.1:3001/directions?origin=${origin}&destination=${dest}&priority=RECOMMEND`;

  showLoading(true);
  console.log('[길찾기] 로컬 프록시 서버 경유 호출:', proxyUrl);

  fetch(proxyUrl)
    .then(res => {
      if (!res.ok) {
        return res.json().then(err => { throw err; });
      }
      return res.json();
    })
    .then(data => handleRouteData(data))
    .catch(err => {
      showLoading(false);
      console.error('[길찾기] 프록시 서버 호출 실패:', err);
      drawStraightRoute();
      showToast(
        '⚠️ 프록시 서버가 실행되지 않았습니다!\n터미널에서 "node proxy-server.js" 를 먼저 실행해주세요.',
        'error'
      );
    });
}

/**
 * 길찾기 API 응답 처리
 */
function handleRouteData(data) {
  showLoading(false);
  console.log('[길찾기] API 응답:', data);

  if (data.routes && data.routes.length > 0) {
    const route = data.routes[0];
    // result_code: 0=성공, 101=경로없음, 104=출발지/목적지 동일 등
    if (route.result_code === 0) {
      drawRoute(route);
      showRoutePanel(route, selectedPlace.place_name);
      showToast('🚗 자동차 경로를 불러왔습니다!', 'success');
    } else {
      console.warn('[길찾기] result_code:', route.result_code, route.result_msg);
      drawStraightRoute();
      showToast(`길찾기 실패 (${route.result_msg || 'code:' + route.result_code}) - 직선 경로 표시`, 'error');
    }
  } else {
    console.error('[길찾기] 예상치 못한 응답 구조:', data);
    drawStraightRoute();
    showToast('길찾기 응답 파싱 실패 - 직선 경로를 표시합니다.', 'error');
  }
}

/**
 * 경로 폴리라인 그리기
 */
function drawRoute(route) {
  clearRoutePolylines();

  const sections = route.sections;
  sections.forEach(section => {
    section.roads.forEach(road => {
      const path = [];
      for (let i = 0; i < road.vertexes.length; i += 2) {
        path.push(new kakao.maps.LatLng(road.vertexes[i + 1], road.vertexes[i]));
      }

      const polyline = new kakao.maps.Polyline({
        path,
        strokeWeight: 6,
        strokeColor: '#3B5BDB',
        strokeOpacity: 0.85,
        strokeStyle: 'solid',
        map
      });
      routePolylines.push(polyline);
    });
  });

  // 지도 범위 조정
  const bounds = new kakao.maps.LatLngBounds();
  bounds.extend(new kakao.maps.LatLng(MULTICAMPUS.lat, MULTICAMPUS.lng));
  bounds.extend(new kakao.maps.LatLng(selectedPlace.y, selectedPlace.x));
  map.setBounds(bounds);
}

/**
 * 직선 경로 폴백
 */
function drawStraightRoute() {
  clearRoutePolylines();

  const path = [
    new kakao.maps.LatLng(MULTICAMPUS.lat, MULTICAMPUS.lng),
    new kakao.maps.LatLng(selectedPlace.y, selectedPlace.x)
  ];

  const polyline = new kakao.maps.Polyline({
    path,
    strokeWeight: 5,
    strokeColor: '#F03E3E',
    strokeOpacity: 0.8,
    strokeStyle: 'dashed',
    map
  });
  routePolylines.push(polyline);
}

/**
 * 길찾기 결과 패널 표시
 */
function showRoutePanel(route, destName) {
  const summary = route.summary;
  const duration = summary.duration;   // 초
  const distance = summary.distance;   // 미터
  const fare = summary.fare || { taxi: 0, toll: 0 }; // 요금 정보

  const min = Math.floor(duration / 60);
  const km  = (distance / 1000).toFixed(1);

  document.getElementById('route-duration').textContent = min;
  document.getElementById('route-distance').textContent = km;
  
  // 요금 포맷 (천 단위 콤마)
  document.getElementById('route-taxi').textContent = fare.taxi.toLocaleString();
  document.getElementById('route-toll').textContent = fare.toll.toLocaleString();

  document.getElementById('route-dest-name').textContent = destName;
  document.getElementById('route-origin-name').textContent = MULTICAMPUS.name;

  document.getElementById('route-panel').classList.add('visible');
}

function closeRoutePanel() {
  document.getElementById('route-panel').classList.remove('visible');
  clearRoutePolylines();
}

// ── 유틸리티 ──────────────────────────────────────

function clearMarkers() {
  markers.forEach(m => m.setMap(null));
  markers = [];
  infowindows.forEach(iw => iw.close());
  infowindows = [];
  selectedMarkerIndex = -1;
  document.getElementById('result-list').innerHTML = '';
  document.getElementById('result-header').innerHTML = '';
}

function clearRoutePolylines() {
  routePolylines.forEach(p => p.setMap(null));
  routePolylines = [];
}

function clearRoutePanel() {
  document.getElementById('route-panel').classList.remove('visible');
  clearRoutePolylines();
}

function showLoading(show) {
  document.getElementById('loading').style.display = show ? 'flex' : 'none';
}

/**
 * 토스트 알림
 */
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}
