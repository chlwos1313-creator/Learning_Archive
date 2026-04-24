# 📚 AI 기반 도서 관리 CRUD 웹 애플리케이션

> Django + Upstage Solar AI API를 활용한 도서 데이터 관리 시스템

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프레임워크 | Django 5.2 |
| 언어 | Python 3.11 |
| DB | SQLite3 (개발용) |
| AI API | Upstage Solar Pro (OpenAI SDK 호환) |
| 주요 기능 | 도서 CRUD + AI 저자 정보 자동 생성 |

---

## 2. 프로젝트 구조

```
도서/
├── venv/                        # 가상환경
├── config/                      # Django 프로젝트 설정
│   ├── settings.py              # 앱 등록, DB, 언어/시간대 설정
│   └── urls.py                  # 루트 URL (books/ 앱 연결)
├── books/                       # 도서 관리 앱
│   ├── migrations/              # DB 마이그레이션 파일
│   │   └── 0001_initial.py      # Book 테이블 생성 마이그레이션
│   ├── templates/books/         # HTML 템플릿
│   │   ├── base.html            # 공통 레이아웃 (nav, CSS)
│   │   ├── index.html           # 도서 목록
│   │   ├── create.html          # 도서 등록 폼
│   │   ├── detail.html          # 도서 상세
│   │   └── update.html          # 도서 수정 폼
│   ├── __init__.py
│   ├── apps.py                  # 앱 설정 클래스
│   ├── models.py                # Book 모델
│   ├── forms.py                 # BookForm (ModelForm)
│   ├── urls.py                  # books 앱 URL 패턴
│   └── views.py                 # CRUD 뷰 함수 + AI API 호출
├── db.sqlite3                   # SQLite 데이터베이스
└── manage.py                    # Django 관리 커맨드
```

---

## 3. 환경 설정 및 실행 방법

### Step 1. 가상환경 생성 및 패키지 설치

```bash
# 가상환경 생성
python -m venv venv

# 활성화 (Windows)
venv\Scripts\activate

# 패키지 설치
pip install django requests openai
```

### Step 2. Django 프로젝트 및 앱 생성

```bash
# 프로젝트 생성 (현재 디렉터리에)
django-admin startproject config .

# 앱 생성
python manage.py startapp books
```

### Step 3. DB 마이그레이션

```bash
python manage.py makemigrations books
python manage.py migrate
```

### Step 4. 개발 서버 실행

```bash
python manage.py runserver
# → http://127.0.0.1:8000 접속
```

---

## 4. 핵심 파일 코드 설명

---

### 4-1. `config/settings.py` — 프로젝트 설정

```python
INSTALLED_APPS = [
    ...
    'books.apps.BooksConfig',  # books 앱 등록
]

LANGUAGE_CODE = 'ko-kr'      # 한국어
TIME_ZONE = 'Asia/Seoul'     # 서울 시간대
```

**설명**
- `INSTALLED_APPS`에 앱을 등록해야 Django가 models, templates 등을 인식한다.
- `'books.apps.BooksConfig'` 형태로 앱 설정 클래스를 명시하면 앱이 확실하게 인식된다.
- `APP_DIRS: True` → Django가 각 앱의 `templates/` 폴더를 자동으로 탐색한다.

---

### 4-2. `config/urls.py` — 루트 URL

```python
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('books/', include('books.urls')),                  # books 앱 URL 위임
    path('', lambda request: redirect('books:index')),      # 루트 → 목록으로 리다이렉트
]
```

**설명**
- `include('books.urls')` : `/books/` 이하의 URL 처리를 books 앱의 urls.py에 위임한다.
- 루트(`/`) 접속 시 자동으로 도서 목록 페이지로 이동시킨다.

---

### 4-3. `books/models.py` — 데이터 모델

```python
class Book(models.Model):
    title       = models.CharField(max_length=200)    # 제목 (최대 200자)
    author      = models.CharField(max_length=100)    # 저자 (최대 100자)
    description = models.TextField()                  # 설명 (길이 제한 없음)
    author_info = models.TextField(blank=True)        # AI 생성 저자 정보 (빈 값 허용)
    created_at  = models.DateTimeField(auto_now_add=True)  # 생성 시 자동 저장
    updated_at  = models.DateTimeField(auto_now=True)      # 수정 시 자동 갱신

    class Meta:
        ordering = ['-created_at']   # 기본 정렬: 최신순
```

**필드별 설명**

| 필드 | 타입 | 옵션 | 설명 |
|------|------|------|------|
| `title` | CharField | max_length=200 | 짧은 문자열, 길이 제한 있음 |
| `author` | CharField | max_length=100 | 짧은 문자열 |
| `description` | TextField | - | 긴 텍스트, 길이 제한 없음 |
| `author_info` | TextField | blank=True | AI가 채워줌, 사용자 입력 불필요 |
| `created_at` | DateTimeField | auto_now_add=True | 생성 시 한 번만 자동 저장 |
| `updated_at` | DateTimeField | auto_now=True | 저장할 때마다 현재 시각으로 갱신 |

- `blank=True` : 폼 유효성 검사에서 빈 값을 허용 (사용자가 직접 입력하는 필드가 아니므로)
- `ordering = ['-created_at']` : `-`(마이너스)를 붙이면 내림차순(최신순) 정렬

---

### 4-4. `books/forms.py` — ModelForm

```python
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'description']  # author_info 제외!

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '...'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
```

**설명**
- `ModelForm` : 모델과 연결된 폼. DB 저장 로직을 자동으로 처리한다.
- `fields` : 사용자에게 노출할 필드만 지정. `author_info`는 AI가 자동으로 채우므로 제외.
- `widgets` : 각 필드의 HTML 렌더링 방식을 커스터마이징 (CSS 클래스, placeholder 등)

---

### 4-5. `books/urls.py` — URL 패턴

```python
app_name = 'books'   # URL 네임스페이스 선언

urlpatterns = [
    path('',               views.index,  name='index'),   # GET  /books/
    path('create/',        views.create, name='create'),  # GET/POST /books/create/
    path('<int:pk>/',      views.detail, name='detail'),  # GET  /books/1/
    path('<int:pk>/update/', views.update, name='update'),# GET/POST /books/1/update/
    path('<int:pk>/delete/', views.delete, name='delete'),# POST /books/1/delete/
]
```

**설명**
- `app_name = 'books'` : 네임스페이스 설정. 다른 앱의 URL과 이름 충돌 방지.
- `<int:pk>` : URL에서 정수형 pk 값을 캡처해 뷰 함수의 인자로 전달.
- `name='...'` : 템플릿에서 `{% url 'books:detail' book.pk %}` 형태로 역참조 가능.

---

### 4-6. `books/views.py` — 뷰 함수

#### ① AI API 클라이언트 초기화

```python
from openai import OpenAI

_upstage_client = OpenAI(
    api_key="up_qVl5...",
    base_url="https://api.upstage.ai/v1/solar",  # Upstage Solar 전용 엔드포인트
)
```

- OpenAI SDK를 그대로 사용하되 `base_url`을 Upstage 서버로 변경 (호환 인터페이스).
- 클라이언트를 모듈 레벨에서 한 번만 생성하여 요청마다 재생성하는 비용을 줄인다.

#### ② AI 저자 정보 생성 함수

```python
def get_author_info_from_ai(author_name: str) -> str:
    try:
        response = _upstage_client.chat.completions.create(
            model="solar-pro",
            messages=[
                {"role": "system", "content": "당신은 문학 전문가입니다. 3문장 이내로 저자를 소개해 주세요."},
                {"role": "user",   "content": f"다음 저자를 소개해 주세요: {author_name}"},
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI 저자 정보 생성 실패: {e}"
```

**Chat Completion 작동 원리**

```
[system 메시지] → AI의 역할/행동 방식 정의
[user 메시지]   → 실제 질문/요청
      ↓
[Upstage Solar Pro 모델 처리]
      ↓
response.choices[0].message.content → 생성된 텍스트
```

- `temperature=0.7` : 0에 가까울수록 일관된 답변, 1에 가까울수록 창의적인 답변
- `max_tokens=300` : 생성할 최대 토큰 수 제한 (비용 절감)
- `try/except` : API 오류가 나도 도서 저장 자체는 반드시 성공하도록 보호

#### ③ HTTP 메서드 데코레이터 (보안)

```python
@require_safe                          # index, detail → GET, HEAD 만 허용
@require_http_methods(["GET", "POST"]) # create, update → GET, POST 만 허용
@require_POST                          # delete → POST 만 허용
```

| 뷰 | 데코레이터 | 이유 |
|----|-----------|------|
| `index`, `detail` | `@require_safe` | 데이터를 읽기만 하는 뷰, 부작용 없음 |
| `create`, `update` | `@require_http_methods(["GET","POST"])` | GET(폼 표시) + POST(저장) 두 가지만 필요 |
| `delete` | `@require_POST` | GET으로 URL 접근만으로 삭제되는 취약점 차단 |

#### ④ create 뷰 — AI 연동 핵심 로직

```python
@require_http_methods(["GET", "POST"])
def create(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)       # ① DB 저장 보류, 인스턴스만 생성
            author_name = form.cleaned_data["author"]
            book.author_info = get_author_info_from_ai(author_name)  # ② AI 호출
            book.save()                          # ③ author_info 포함하여 최종 저장
            return redirect("books:detail", book.pk)
    else:
        form = BookForm()
    return render(request, "books/create.html", {"form": form})
```

**`commit=False` 사용 이유**

```
form.save()           → 즉시 DB에 INSERT (author_info 비어있음)
form.save(commit=False) → 인스턴스만 생성, DB 저장 안 함
                          → author_info 채운 뒤 → book.save() 로 한 번에 저장
```

#### ⑤ update 뷰

```python
def update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)  # instance=book → 기존 객체 업데이트
        if form.is_valid():
            form.save()
            return redirect("books:detail", book.pk)
    else:
        form = BookForm(instance=book)  # 기존 값으로 폼을 미리 채워서 렌더링
    return render(request, "books/update.html", {"form": form, "book": book})
```

- `instance=book` 없으면 → 수정이 아닌 **새 레코드 생성**이 된다.

#### ⑥ delete 뷰

```python
@require_POST
def delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("books:index")
```

---

### 4-7. 템플릿 구조

#### `base.html` — 공통 레이아웃

```html
<!-- 모든 페이지가 상속하는 뼈대 -->
<nav>📚 도서 관리 | 전체 목록 | + 도서 등록</nav>
<div class="container">
  {% block content %}{% endblock %}  ← 각 페이지가 이 부분을 채움
</div>
```

#### 템플릿 상속 원리

```
base.html (부모)
    ↑ {% extends 'books/base.html' %}
index.html / create.html / detail.html / update.html (자식)
    → {% block content %} ... {% endblock %} 안에 내용 작성
```

#### URL 역참조 (네임스페이스)

```html
<!-- 템플릿에서 -->
<a href="{% url 'books:detail' book.pk %}">보기</a>
<a href="{% url 'books:index' %}">목록</a>

<!-- 뷰에서 -->
return redirect('books:index')
return redirect('books:detail', book.pk)
```

---

## 5. 전체 요청-응답 흐름

### 도서 등록 (create) 전체 흐름

```
① 브라우저 → GET /books/create/
② Django → books:create 뷰 → 빈 BookForm 렌더링 → create.html 반환
③ 사용자 → 제목/저자/설명 입력 후 [등록] 버튼 클릭
④ 브라우저 → POST /books/create/ (CSRF 토큰 포함)
⑤ Django → form = BookForm(request.POST)
⑥ Django → form.is_valid() → 유효성 검사
⑦ Django → book = form.save(commit=False) → DB 저장 보류
⑧ Django → Upstage Solar API 호출 (저자명 전달)
⑨ Upstage → AI가 저자 소개 텍스트 생성 → 반환
⑩ Django → book.author_info = 생성된 텍스트
⑪ Django → book.save() → SQLite DB에 INSERT
⑫ Django → redirect('books:detail', book.pk) → 302 응답
⑬ 브라우저 → GET /books/{pk}/ → 상세 페이지 렌더링
```

### CRUD 요청 흐름 요약

| 기능 | HTTP Method | URL | 처리 결과 |
|------|-------------|-----|-----------|
| 목록 조회 | GET | `/books/` | 전체 도서 최신순 목록 |
| 등록 폼 | GET | `/books/create/` | 빈 폼 렌더링 |
| 등록 처리 | POST | `/books/create/` | AI 호출 → DB 저장 → 상세 리다이렉트 |
| 상세 조회 | GET | `/books/<pk>/` | 단일 도서 정보 |
| 수정 폼 | GET | `/books/<pk>/update/` | 기존 값 채워진 폼 |
| 수정 처리 | POST | `/books/<pk>/update/` | DB 업데이트 → 상세 리다이렉트 |
| 삭제 | POST | `/books/<pk>/delete/` | DB 삭제 → 목록 리다이렉트 |

---

## 6. 보안 설계

### CSRF (Cross-Site Request Forgery) 방어

```html
<!-- 모든 POST 폼에 반드시 포함 -->
<form method="POST">
  {% csrf_token %}   ← Django가 자동으로 숨겨진 토큰 필드를 삽입
  ...
</form>
```

- Django의 `CsrfViewMiddleware`가 POST 요청마다 토큰을 검증한다.
- 토큰이 없거나 다르면 403 응답을 반환한다.

### delete는 왜 GET이 아닌 POST인가?

```
# 만약 GET으로 삭제를 허용한다면:
<img src="/books/1/delete/">  ← 이 태그 하나로 다른 사이트에서 삭제 가능!

# POST + CSRF 토큰 방식:
반드시 올바른 폼 제출 + CSRF 토큰 일치가 필요 → 외부에서 악용 불가
```

### `get_object_or_404()` 사용 이유

```python
# 사용하지 않으면:
book = Book.objects.get(pk=pk)   # pk가 없으면 DoesNotExist 예외 → 500 오류

# 사용하면:
book = get_object_or_404(Book, pk=pk)  # pk가 없으면 깔끔하게 404 반환
```

---

## 7. URL 접속 주소

| 페이지 | URL |
|--------|-----|
| 도서 목록 | http://127.0.0.1:8000/books/ |
| 도서 등록 | http://127.0.0.1:8000/books/create/ |
| 도서 상세 | http://127.0.0.1:8000/books/1/ |
| 도서 수정 | http://127.0.0.1:8000/books/1/update/ |
| 관리자 페이지 | http://127.0.0.1:8000/admin/ |

---

## 8. 사용 기술 및 라이브러리

| 라이브러리 | 용도 |
|-----------|------|
| `django` | 웹 프레임워크 (라우팅, ORM, 템플릿, 보안) |
| `openai` | Upstage Solar AI API 호출 (OpenAI SDK 호환) |
| `requests` | HTTP 라이브러리 (설치됨, 현재 openai SDK로 대체) |
| SQLite3 | 개발용 경량 데이터베이스 (Django 기본 내장) |
