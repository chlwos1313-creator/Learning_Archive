from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    AbstractUser를 상속받은 커스텀 유저 모델.
    - nickname      : 닉네임 (표시 이름)
    - interest_stocks : 관심 종목 목록 (JSONField로 문자열 리스트 저장)
    - profile_image : 프로필 이미지
    """
    nickname = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="닉네임",
    )
    # 관심 종목: 종목 코드/이름 문자열 리스트를 JSON으로 저장
    interest_stocks = models.JSONField(
        default=list,
        blank=True,
        verbose_name="관심 종목",
    )
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
        verbose_name="프로필 이미지",
    )

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자 목록"

    def __str__(self):
        return self.username

    def get_interest_stocks_display(self):
        """관심 종목 리스트를 쉼표 구분 문자열로 반환"""
        if isinstance(self.interest_stocks, list):
            return ", ".join(self.interest_stocks)
        return ""
