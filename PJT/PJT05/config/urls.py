from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),  # 인증 관련 URL
    path("", include("community.urls")),           # 커뮤니티 메인
]

# 개발 환경에서 미디어 파일 서빙 (업로드 이미지 등)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
