# community/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from .utils import check_inappropriate_content
from .models import Post
from .forms import PostForm
import json, os
from django.conf import settings

# 자산 데이터 로드
def get_assets():
    json_path = os.path.join(settings.BASE_DIR, 'data', 'assets.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# F401: 자산 목록
def index(request):
    assets = get_assets()
    # 'community/index.html' 템플릿을 사용하도록 지정 [cite: 67]
    return render(request, 'community/index.html', {'assets': assets})

# F403 & F408: 자산별 게시판 및 404 처리 
def board(request, asset_id):
    assets = get_assets()
    asset = next((a for a in assets if a['id'] == asset_id), None)
    
    # F408: 잘못된 자산 ID 접근 시 404 발생 
    if not asset:
        raise Http404("해당 자산을 찾을 수 없습니다.")
    
    # F403: 해당 자산의 글을 최신순으로 정렬하여 가져오기 
    posts = Post.objects.filter(asset_id=asset_id).order_by('-created_at')
    
    return render(request, 'community/board.html', {
        'asset': asset,
        'posts': posts
    })

def post_update(request, asset_id, post_id):
    # F408: 존재하지 않는 게시글 접근 시 404 처리
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    
    if request.method == 'POST':
        # F406: 기존 게시글 데이터를 폼에 바인딩하여 수정
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            # F406: 수정 완료 후 상세 페이지로 이동
            return redirect('community:post_detail', asset_id=asset_id, post_id=post.id)
    else:
        # 기존 데이터를 폼에 채워서 사용자에게 제공
        form = PostForm(instance=post)
    
    # post_form.html을 '글쓰기'와 공유하여 사용합니다.
    return render(request, 'community/post_form.html', {
        'form': form, 
        'post': post,  # 템플릿에서 '수정'인지 '생성'인지 구분하기 위해 전달
        'asset_id': asset_id
    })

# F405: 게시글 상세 조회
def post_detail(request, asset_id, post_id):
    # F408: 잘못된 post_id 접근 시 자동으로 404 페이지 렌더링 
    post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
    return render(request, 'community/post_detail.html', {'post': post})

# F404: 게시글 생성 및 리다이렉트
def post_create(request, asset_id):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            # 필터링 검사
            if check_inappropriate_content(form.cleaned_data['title'], form.cleaned_data['content']):
                messages.error(request, "부적절한 내용이 포함되어 있습니다. 수정 후 다시 등록해 주세요.")
                return render(request, 'community/post_form.html', {'form': form, 'asset_id': asset_id})
            
            post = form.save(commit=False)
            post.asset_id = asset_id
            post.save()
            return redirect('community:board', asset_id=asset_id)
    else:
        form = PostForm()
    return render(request, 'community/post_form.html', {'form': form, 'asset_id': asset_id})

# F407: 게시글 삭제
def post_delete(request, asset_id, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id, asset_id=asset_id)
        post.delete()
        # F407: 삭제 후 게시판 목록으로 이동
        return redirect('community:board', asset_id=asset_id)