# 금융상품 통합 비교 공시 API 서버

금융감독원 정기예금 API를 활용하여 데이터를 수집·가공·저장·조회하는 RESTful 서비스입니다.  
Upstage AI(Solar Pro)를 연동하여 더미 금융상품 데이터를 자동 생성하는 기능도 포함합니다.

## 기술 스택

| 항목 | 내용 |
| --- | --- |
| Language | Python 3.x |
| Framework | Django, Django REST Framework (DRF) |
| Database | SQLite3 |
| 환경 변수 관리 | django-environ |
| AI 연동 | Upstage AI (solar-pro) |

---

## 환경 설정 및 실행 방법

### 1. 패키지 설치

```bash
pip install django djangorestframework django-environ requests openai
```

### 2. `.env` 파일 생성 (NF801, NF802)

프로젝트 루트(`manage.py`와 같은 위치)에 `.env` 파일을 생성합니다.  
> ⚠️ `.env` 파일은 `.gitignore`에 등록되어 있으며, **절대 Git에 커밋하지 마세요.**

```env
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
API_KEY=발급받은_금융감독원_API_KEY
UPSTAGE_API_KEY=up_qVl5yEKdGy7vRfIsiKScygdmrjs7O
UPSTAGE_BASE_URL=https://api.upstage.ai/v1
```

### 3. 데이터베이스 마이그레이션

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 서버 실행

```bash
python manage.py runserver
```

---

## API 명세 (NF803 - 코드 구조화 기반)

### 기본 URL

- 테스트/표준: `http://127.0.0.1:8000/products/`
- 레거시 호환: `http://127.0.0.1:8000/finlife/`

### 엔드포인트 목록

| 기능 | 요구사항 | Method | URL | 설명 |
| :--- | :---: | :---: | :--- | :--- |
| 금감원 데이터 수집 및 저장 | F801 | GET | `/products/save-deposit-products/` | 금감원 API 호출 후 DB 저장 |
| 전체 상품 목록 조회 | F802 | GET | `/products/deposit/` | DB의 모든 정기예금 상품 반환 |
| 신규 상품 추가 | F803 | POST | `/products/deposit/` | 요청 본문으로 새 상품 추가 |
| 특정 상품 단건 조회 | F804 | GET | `/products/deposit/<fin_prdt_cd>` | 상품 + 옵션 리스트 함께 반환 |
| 특정 상품 옵션만 조회 | F804 | GET | `/products/deposit-product-options/<fin_prdt_cd>/` | 옵션 리스트만 반환 |
| 전체 옵션 목록 조회 | - | GET | `/products/deposit/options/` | 모든 옵션 리스트 반환 |
| 최고 우대금리 상품 조회 | F805 | GET | `/products/top-rate-product/` | 최고 우대금리 상품 + 옵션 반환 |
| AI 더미 데이터 생성 | F811 | GET | `/products/generate-dummy-data/` | Upstage AI 생성 더미 데이터 |

---

## 주요 기능 설명

### F801 - 금감원 데이터 수집

- `http://finlife.fss.or.kr` API를 호출하여 `baseList`(상품)와 `optionList`(옵션)를 각각 파싱
- 이미 존재하는 `fin_prdt_cd`는 중복 저장하지 않음

### F802 / F803 - 목록 조회 및 입력

- GET 응답: `{ "count": N, "results": [...] }` 형식으로 반환
- POST 요청: `options` 배열이 포함된 경우 상품과 옵션을 동시에 저장

### F805 - 최고 우대금리 상품 분석

- `DepositOptions.intr_rate2` 필드에서 MAX 값을 집계
- 해당 옵션과 연결된 상품 정보와 옵션 리스트를 **함께** 반환

### F811 - AI 더미 데이터 생성

- Upstage AI `solar-pro` 모델을 streaming 방식으로 호출
- 실제 은행 상품과 유사한 형태의 JSON 더미 데이터를 생성하여 반환

---

## 구현 과정에서 느낀 점

이번 금융상품API 서버를 구축하면서 Django REST Framework의 강력함과 유용성을 느낄 수 있었습니다.
특히, DRF는 1:N 관계 설계를 통해 상품과 옵션을 분리하고 ForeignKey로 연결하여 상품 조회 시 옵션을 함께 포함하는 구조를 구현할 수 있었습니다.
VUE와 DRF를 함께 사용하여 금융상품을 제공하는 웹 서비스를 구현해보고 싶습니다.
