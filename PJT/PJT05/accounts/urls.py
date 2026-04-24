from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # [F502] 회원가입
    path("signup/", views.signup, name="signup"),
    # [F503] 로그인
    path("login/", views.login_view, name="login"),
    # [F504] 로그아웃
    path("logout/", views.logout_view, name="logout"),
    # [F505] 비밀번호 변경
    path("password/change/", views.password_change, name="password_change"),
    path("password/change/done/", views.password_change_done, name="password_change_done"),
    # [F507] 프로필 페이지
    path("profile/<str:username>/", views.profile, name="profile"),
    # [F511] 투자 성향 분석 API
    path("profile/<str:username>/analyze/", views.analyze_style, name="analyze_style"),
]
