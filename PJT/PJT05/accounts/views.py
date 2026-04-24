from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse
import json

from community.llm import analyze_investment_style

from .forms import CustomUserCreationForm, CustomAuthenticationForm, CustomPasswordChangeForm

User = get_user_model()


# ──────────────────────────────────────
# [F502] 회원가입
# ──────────────────────────────────────
@require_http_methods(["GET", "POST"])
def signup(request):
    """회원가입 — 완료 후 자동 로그인 후 메인으로 이동"""
    if request.user.is_authenticated:
        return redirect("community:asset_list")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # 프로필 이미지 별도 저장 (form.save()에서 commit=True 하지 않을 경우를 대비)
            if request.FILES.get("profile_image"):
                user.profile_image = request.FILES["profile_image"]
                user.save()
            # 자동 로그인
            login(request, user)
            messages.success(request, f"환영합니다, {user.nickname or user.username}님! 회원가입이 완료되었습니다.")
            return redirect("community:asset_list")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})


# ──────────────────────────────────────
# [F503] 로그인
# ──────────────────────────────────────
@require_http_methods(["GET", "POST"])
def login_view(request):
    """로그인 — 성공 시 메인으로 이동"""
    if request.user.is_authenticated:
        return redirect("community:asset_list")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"{user.nickname or user.username}님, 로그인되었습니다.")
            # next 파라미터가 있으면 해당 URL로, 없으면 메인으로
            next_url = request.GET.get("next", "community:asset_list")
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


# ──────────────────────────────────────
# [F504] 로그아웃
# ──────────────────────────────────────
@require_http_methods(["POST"])
def logout_view(request):
    """로그아웃 — 메인 페이지로 이동"""
    logout(request)
    messages.info(request, "로그아웃 되었습니다.")
    return redirect("community:asset_list")


# ──────────────────────────────────────
# [F505] 비밀번호 변경
# ──────────────────────────────────────
@login_required
@require_http_methods(["GET", "POST"])
def password_change(request):
    """비밀번호 변경 — 완료 후 성공 페이지로 리다이렉트"""
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # 세션 유지: 비밀번호 변경 후 로그인 상태 유지
            update_session_auth_hash(request, user)
            messages.success(request, "비밀번호가 성공적으로 변경되었습니다.")
            return redirect("accounts:password_change_done")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, "accounts/password_change.html", {"form": form})


@login_required
def password_change_done(request):
    """비밀번호 변경 완료 페이지"""
    return render(request, "accounts/password_change_done.html")


# ──────────────────────────────────────
# [F507] 프로필 페이지
# ──────────────────────────────────────
def profile(request, username):
    """프로필 페이지 조회 기능
    - 닉네임, 프로필 이미지, 관심 종목, 작성 게시글 목록 표시
    """
    profile_user = get_object_or_404(User, username=username)
    # 해당 사용자가 작성한 게시글 목록 (가장 최근 글부터)
    user_posts = profile_user.posts.all().order_by("-created_at")
    
    context = {
        "profile_user": profile_user,
        "user_posts": user_posts,
    }
    return render(request, "accounts/profile.html", context)


# ──────────────────────────────────────
# [F511] 투자 성향 분석 API (Phase 5)
# ──────────────────────────────────────
@require_POST
def analyze_style(request, username):
    """
    LLM을 이용하여 사용자의 투자 성향을 분석하고 결과를 JSON으로 반환합니다.
    """
    profile_user = get_object_or_404(User, username=username)
    
    # 분석에 사용할 게시글 내용 모으기
    user_posts = profile_user.posts.all().order_by("-created_at")[:10]  # 최근 10개로 제한
    if not user_posts:
        return JsonResponse({"result": "작성한 게시글이 없어 투자 성향을 분석할 수 없습니다."})
        
    # 제목과 내용을 텍스트로 결합
    posts_text = ""
    for post in user_posts:
        posts_text += f"제목: {post.title}\n내용: {post.content}\n\n"
        
    try:
        # LLM 모듈을 통해 분석 요청
        result = analyze_investment_style(posts_text)
        return JsonResponse({"result": result})
    except Exception as e:
        return JsonResponse({"result": "분석 중 오류가 발생했습니다."}, status=500)
