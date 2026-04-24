from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST

from .forms import PostForm
from .models import Post
from .utils import load_assets, get_asset_by_id
from .llm import is_inappropriate  # [심화 Phase 5] LLM 부적절 콘텐츠 필터링


# ──────────────────────────────────────
# 자산 목록 (메인 페이지)
# ──────────────────────────────────────
def asset_list(request):
    """금융 자산 리스트 (JSON에서 로드)"""
    assets = load_assets()
    context = {"assets": assets}
    return render(request, "community/asset_list.html", context)


# ──────────────────────────────────────
# 게시판 (게시글 목록)
# ──────────────────────────────────────
def board(request, asset_id):
    """해당 자산의 토론 게시판 (게시글 목록)"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    posts = Post.objects.filter(asset_id=asset_id).select_related("author")
    context = {"asset": asset, "posts": posts}
    return render(request, "community/board.html", context)


# ──────────────────────────────────────
# 게시글 상세
# ──────────────────────────────────────
def post_detail(request, asset_id, post_id):
    """게시글 상세"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    context = {"asset": asset, "post": post}
    return render(request, "community/post_detail.html", context)


# ──────────────────────────────────────
# [F506] 게시글 작성 — 로그인 필수
# ──────────────────────────────────────
@login_required
@require_http_methods(["GET", "POST"])
def post_create(request, asset_id):
    """게시글 작성 — 로그인한 사용자만 가능"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # [심화 Phase 5] LLM 부적절 콘텐츠 필터링
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if is_inappropriate(title) or is_inappropriate(content):
                messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
                return render(request, "community/post_form.html", {"asset": asset, "form": form, "is_edit": False})

            post = form.save(commit=False)
            post.asset_id = asset_id
            post.author = request.user  # 현재 로그인 사용자 자동 저장
            post.save()
            messages.success(request, "게시글이 등록되었습니다.")
            return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)
    else:
        form = PostForm()

    context = {"asset": asset, "form": form, "is_edit": False}
    return render(request, "community/post_form.html", context)


# ──────────────────────────────────────
# [F506] 게시글 수정 — 작성자 본인만
# ──────────────────────────────────────
@login_required
@require_http_methods(["GET", "POST"])
def post_update(request, asset_id, post_id):
    """게시글 수정 — 작성자 본인만 가능"""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return render(request, "community/404.html", status=404)

    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)

    # ✅ 권한 방어 코드: 작성자 본인 여부 확인
    if post.author_id != request.user.id:
        messages.error(request, "게시글 수정 권한이 없습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            # [심화 Phase 5] LLM 부적절 콘텐츠 필터링
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if is_inappropriate(title) or is_inappropriate(content):
                messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 저장해 주세요.")
                return render(request, "community/post_form.html", {"asset": asset, "form": form, "post": post, "is_edit": True})

            form.save()
            messages.success(request, "게시글이 수정되었습니다.")
            return redirect("community:post_detail", asset_id=asset_id, post_id=post.id)
    else:
        form = PostForm(instance=post)

    context = {"asset": asset, "form": form, "post": post, "is_edit": True}
    return render(request, "community/post_form.html", context)


# ──────────────────────────────────────
# [F506] 게시글 삭제 — 작성자 본인만
# ──────────────────────────────────────
@login_required
@require_POST
def post_delete(request, asset_id, post_id):
    """게시글 삭제 — 작성자 본인만 가능"""
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)

    # ✅ 권한 방어 코드: 작성자 본인 여부 확인
    if post.author_id != request.user.id:
        messages.error(request, "게시글 삭제 권한이 없습니다.")
        return redirect("community:post_detail", asset_id=asset_id, post_id=post_id)

    post.delete()
    messages.success(request, "게시글이 삭제되었습니다.")
    return redirect("community:board", asset_id=asset_id)
