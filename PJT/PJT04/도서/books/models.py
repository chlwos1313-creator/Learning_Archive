from django.db import models


class Book(models.Model):
    """
    도서 데이터를 저장하는 모델 (F402)
    - title: 도서 제목
    - author: 저자명
    - description: 도서 설명/줄거리
    - author_info: AI가 생성한 저자 정보 (입력 필수 아님 → blank=True)
    - created_at: 생성 일시 (자동 저장)
    - updated_at: 수정 일시 (자동 갱신)
    """

    title = models.CharField(max_length=200, verbose_name="제목")
    author = models.CharField(max_length=100, verbose_name="저자")
    description = models.TextField(verbose_name="설명")

    # AI가 생성한 저자 정보 필드
    # blank=True: 폼 유효성 검사 시 빈 값 허용 (사용자가 직접 입력하는 필드가 아닌 AI가 채워주는 필드이므로)
    author_info = models.TextField(
        blank=True,
        verbose_name="저자 정보 (AI 생성)",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        verbose_name = "도서"
        verbose_name_plural = "도서 목록"
        # 기본 정렬: 최신 생성순 (index 뷰에서도 동일하게 적용)
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.pk}] {self.title} - {self.author}"
