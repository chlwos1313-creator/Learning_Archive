from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # F401: 자산 목록 출력 (메인 페이지)
    path('', views.index, name='index'), 
    
    # F403: 자산별 게시판
    path('asset/<str:asset_id>/', views.board, name='board'), 
    
    # F404: 게시글 생성
    path('asset/<str:asset_id>/create/', views.post_create, name='post_create'), 
    
    # F405: 게시글 상세 조회
    path('asset/<str:asset_id>/post/<int:post_id>/', views.post_detail, name='post_detail'), 
    
    # F406: 게시글 수정
    path('asset/<str:asset_id>/post/<int:post_id>/update/', views.post_update, name='post_update'), 
    
    # F407: 게시글 삭제
    path('asset/<str:asset_id>/post/<int:post_id>/delete/', views.post_delete, name='post_delete'), 
]