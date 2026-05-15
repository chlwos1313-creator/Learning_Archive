from django.urls import path
from . import views

urlpatterns = [
    # F801: 금융감독원 API 데이터 수집 및 저장
    path('save-deposit-products/', views.save_deposit_products),

    # F802 (GET) & F803 (POST): 상품 목록 조회 및 신규 상품 추가
    # 테스트 코드 URL: /products/deposit/
    path('deposit/', views.DepositProductList.as_view()),

    # F804: 특정 상품 코드로 단건 상품 + 옵션 함께 조회
    # 테스트 코드 URL: /products/deposit/<fin_prdt_cd>
    path('deposit/<str:fin_prdt_cd>', views.deposit_product_detail),

    # F804 (기존): fin_prdt_cd 기준으로 옵션 리스트만 조회
    path('deposit-product-options/<str:fin_prdt_cd>/', views.deposit_product_options),

    # 전체 옵션 목록 조회
    # 테스트 코드 URL: /products/deposit/options/
    path('deposit/options/', views.DepositOptionList.as_view()),

    # F805: 최고 우대금리 상품 + 옵션 함께 조회
    path('top-rate-product/', views.top_rate_product),

    # F811: Upstage AI를 활용한 더미 데이터 생성
    path('generate-dummy-data/', views.generate_dummy_data),
]
