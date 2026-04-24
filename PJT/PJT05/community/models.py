from django.db import models
from django.conf import settings


class Post(models.Model):
    """금융 자산별 토론 게시글"""
    asset_id = models.CharField(max_length=50)  # JSON 자산 id와 매칭
    title = models.CharField(max_length=200)
    content = models.TextField()
    # author: 로그인 사용자(CustomUser) 연결. 탈퇴 시 게시글은 NULL 처리
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="작성자",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
