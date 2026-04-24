from django.urls import path
from . import views

# NF401: app_name을 설정하여 URL 네임스페이스를 구성
# 템플릿/뷰에서 {% url 'books:index' %} 또는 redirect('books:index') 형태로 사용
# 다른 앱의 URL과 충돌 없이 유지보수가 용이해짐
app_name = "books"

urlpatterns = [
    # F404: 전체 도서 목록 조회
    path("", views.index, name="index"),
    # F405: 도서 생성 (GET: 입력 폼, POST: 데이터 저장)
    path("create/", views.create, name="create"),
    # F406: 단일 도서 상세 조회
    path("<int:pk>/", views.detail, name="detail"),
    # F407: 도서 수정 (GET: 수정 폼, POST: 수정 반영)
    path("<int:pk>/update/", views.update, name="update"),
    # F408: 도서 삭제 (POST 요청만 허용)
    path("<int:pk>/delete/", views.delete, name="delete"),
]
