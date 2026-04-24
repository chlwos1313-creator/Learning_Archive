from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model

User = get_user_model()

# 관심 종목 선택지 (주요 국내외 종목 예시)
STOCK_CHOICES = [
    ("삼성전자",   "삼성전자 (005930)"),
    ("SK하이닉스", "SK하이닉스 (000660)"),
    ("LG에너지솔루션", "LG에너지솔루션 (373220)"),
    ("현대차",    "현대차 (005380)"),
    ("카카오",    "카카오 (035720)"),
    ("네이버",    "네이버 (035420)"),
    ("셀트리온",  "셀트리온 (068270)"),
    ("POSCO홀딩스", "POSCO홀딩스 (005490)"),
    ("Apple",   "Apple (AAPL)"),
    ("Tesla",   "Tesla (TSLA)"),
    ("NVIDIA",  "NVIDIA (NVDA)"),
    ("Microsoft", "Microsoft (MSFT)"),
    ("Bitcoin", "Bitcoin (BTC)"),
    ("Ethereum", "Ethereum (ETH)"),
]


class CustomUserCreationForm(UserCreationForm):
    """[F502] 회원가입 폼 — 닉네임, 프로필 이미지, 관심 종목 포함"""

    nickname = forms.CharField(
        max_length=50,
        required=False,
        label="닉네임",
        widget=forms.TextInput(attrs={"placeholder": "표시될 닉네임을 입력하세요"}),
    )
    profile_image = forms.ImageField(
        required=False,
        label="프로필 이미지",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )
    interest_stocks = forms.MultipleChoiceField(
        choices=STOCK_CHOICES,
        required=False,
        label="관심 종목",
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2",
                  "nickname", "profile_image", "interest_stocks")
        labels = {
            "username": "아이디",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 비밀번호 관련 help_text를 한글로 교체
        self.fields["password1"].help_text = (
            "비밀번호는 8자 이상이며, 숫자만으로 이루어질 수 없습니다."
        )
        self.fields["password2"].label = "비밀번호 확인"
        self.fields["password2"].help_text = "위와 동일한 비밀번호를 입력하세요."

    def save(self, commit=True):
        user = super().save(commit=False)
        user.nickname = self.cleaned_data.get("nickname", "")
        # 관심 종목은 리스트 형태로 JSONField에 저장
        user.interest_stocks = self.cleaned_data.get("interest_stocks", [])
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """[F503] 로그인 폼 — 한글 레이블"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "아이디"
        self.fields["username"].widget.attrs["placeholder"] = "아이디를 입력하세요"
        self.fields["password"].label = "비밀번호"
        self.fields["password"].widget.attrs["placeholder"] = "비밀번호를 입력하세요"

    # Django 기본 AuthenticationForm 오류 메시지를 한글로 재정의
    error_messages = {
        "invalid_login": (
            "아이디 또는 비밀번호가 올바르지 않습니다. "
            "대소문자를 확인하세요."
        ),
        "inactive": "이 계정은 비활성화되어 있습니다.",
    }


class CustomPasswordChangeForm(PasswordChangeForm):
    """[F505] 비밀번호 변경 폼 — 오류 메시지 한글화"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = "현재 비밀번호"
        self.fields["old_password"].widget.attrs["placeholder"] = "현재 비밀번호를 입력하세요"
        self.fields["new_password1"].label = "새 비밀번호"
        self.fields["new_password1"].widget.attrs["placeholder"] = "새 비밀번호를 입력하세요"
        self.fields["new_password1"].help_text = (
            "새 비밀번호는 8자 이상이며, 숫자만으로 이루어질 수 없습니다."
        )
        self.fields["new_password2"].label = "새 비밀번호 확인"
        self.fields["new_password2"].widget.attrs["placeholder"] = "새 비밀번호를 다시 입력하세요"

    # 현재 비밀번호 오류 메시지 한글화
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "현재 비밀번호가 올바르지 않습니다. 다시 확인해 주세요.",
        "password_mismatch": "새 비밀번호가 일치하지 않습니다. 다시 확인해 주세요.",
    }
