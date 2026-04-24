import requests
from openai import OpenAI

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import (
    require_safe,
    require_http_methods,
    require_POST,
)

from .models import Book
from .forms import BookForm


# ---------------------------------------------------------------------------
# F409: Upstage Solar AI API를 활용한 저자 정보 생성 함수
# ---------------------------------------------------------------------------

# Upstage API 클라이언트를 모듈 레벨에서 한 번만 생성 (재사용)
# - api_key: Upstage에서 발급받은 API 키
# - base_url: Upstage Solar API 엔드포인트 (OpenAI SDK 호환)
_upstage_client = OpenAI(
    api_key="up_qVl5yEKdGy7vRfIsiKScygdmrjs7O",
    base_url="https://api.upstage.ai/v1/solar",  # Solar Chat Completion 전용 엔드포인트
)


def get_author_info_from_ai(author_name: str) -> str:
    """
    저자명을 받아 Upstage Solar 모델에 저자 소개를 요청하고 결과 텍스트를 반환한다.

    - OpenAI SDK 호환 인터페이스를 사용하므로 client.chat.completions.create() 그대로 사용
    - system 프롬프트로 역할을 정의하고 user 프롬프트에 저자명 전달
    - 네트워크 오류나 API 오류가 발생해도 메인 저장 로직이 중단되지 않도록 try/except 처리
    """
    try:
        response = _upstage_client.chat.completions.create(
            model="solar-pro",  # Upstage 고성능 Solar 모델
            messages=[
                {
                    "role": "system",
                    "content": (
                        "당신은 문학 전문가입니다. "
                        "사용자가 저자명을 제공하면 해당 저자에 대한 핵심 정보를 "
                        "한국어로 3문장 이내로 간결하게 작성해 주세요."
                    ),
                },
                {
                    "role": "user",
                    "content": f"다음 저자를 소개해 주세요: {author_name}",
                },
            ],
            # 저자 소개는 짧은 텍스트이므로 토큰을 제한하여 비용 절감
            max_tokens=300,
            temperature=0.7,  # 약간의 창의성 허용
        )

        # Chat Completion 응답에서 생성된 텍스트 추출
        return response.choices[0].message.content.strip()

    except Exception as e:
        # API 오류가 도서 저장 자체를 막으면 안 되므로 에러 메시지를 필드에 저장
        return f"AI 저자 정보 생성 실패: {e}"



# ---------------------------------------------------------------------------
# F404: 전체 도서 목록 조회 (index)
# ---------------------------------------------------------------------------

# NF402: @require_safe → GET, HEAD 요청만 허용 (읽기 전용 뷰에 적합)
@require_safe
def index(request):
    """전체 도서를 최신 생성순으로 조회하여 목록 페이지를 렌더링한다."""

    # Model의 Meta.ordering = ['-created_at']에 의해 자동으로 최신순 정렬됨
    books = Book.objects.all()
    context = {"books": books}
    return render(request, "books/index.html", context)


# ---------------------------------------------------------------------------
# F405: 도서 생성 (create)
# ---------------------------------------------------------------------------

# NF402: @require_http_methods(["GET", "POST"]) → GET(폼 렌더링) / POST(데이터 저장)만 허용
# PUT, PATCH, DELETE 등 불필요한 메서드를 차단하여 의도치 않은 접근을 방지
@require_http_methods(["GET", "POST"])
def create(request):
    """
    GET : 빈 BookForm을 렌더링한다.
    POST: 폼 데이터의 유효성을 검사하고,
          통과하면 AI API로 저자 정보를 가져온 뒤 DB에 저장한다. (F409)
    """

    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            # ── F409: AI API 호출 ──────────────────────────────────────
            # commit=False로 인스턴스만 생성하고 DB 저장은 보류
            # → author_info 필드를 채운 뒤 최종 저장하기 위해
            book = form.save(commit=False)

            # 폼에서 검증된 저자명으로 AI API를 호출하여 저자 정보를 가져옴
            author_name = form.cleaned_data["author"]
            book.author_info = get_author_info_from_ai(author_name)

            # author_info가 채워진 완전한 인스턴스를 DB에 저장
            book.save()
            # ─────────────────────────────────────────────────────────

            # NF401: URL 네임스페이스를 사용하여 리다이렉트
            return redirect("books:detail", book.pk)

    else:  # GET
        form = BookForm()

    context = {"form": form}
    return render(request, "books/create.html", context)


# ---------------------------------------------------------------------------
# F406: 단일 도서 상세 조회 (detail)
# ---------------------------------------------------------------------------

# NF402: @require_safe → GET, HEAD 요청만 허용
@require_safe
def detail(request, pk):
    """pk에 해당하는 도서를 조회하여 상세 페이지를 렌더링한다."""

    # pk에 해당하는 객체가 없으면 자동으로 404 응답 반환
    book = get_object_or_404(Book, pk=pk)
    context = {"book": book}
    return render(request, "books/detail.html", context)


# ---------------------------------------------------------------------------
# F407: 도서 수정 (update)
# ---------------------------------------------------------------------------

# NF402: @require_http_methods(["GET", "POST"])
@require_http_methods(["GET", "POST"])
def update(request, pk):
    """
    GET : 기존 데이터가 채워진 BookForm을 렌더링한다.
    POST: 수정된 데이터의 유효성을 검사하고 DB에 반영한다.
    """

    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        # instance=book → 새로 생성하지 않고 기존 객체를 업데이트
        form = BookForm(request.POST, instance=book)

        if form.is_valid():
            form.save()
            # NF401: URL 네임스페이스로 상세 페이지로 리다이렉트
            return redirect("books:detail", book.pk)

    else:  # GET
        # instance=book → 기존 값으로 폼을 미리 채워서 렌더링
        form = BookForm(instance=book)

    context = {"form": form, "book": book}
    return render(request, "books/update.html", context)


# ---------------------------------------------------------------------------
# F408: 도서 삭제 (delete)
# ---------------------------------------------------------------------------

# NF402: @require_POST → POST 요청만 허용
# GET 요청으로 URL에 직접 접근하는 것만으로 데이터가 삭제되는 CSRF 취약점을 방지
# 반드시 <form method="POST">로만 삭제 요청을 보낼 수 있게 강제
@require_POST
def delete(request, pk):
    """pk에 해당하는 도서를 삭제하고 목록 페이지로 리다이렉트한다."""

    book = get_object_or_404(Book, pk=pk)
    book.delete()

    # NF401: URL 네임스페이스로 목록 페이지로 리다이렉트
    return redirect("books:index")
