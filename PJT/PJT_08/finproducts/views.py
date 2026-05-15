import requests
import environ
from django.db.models import Max
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from openai import OpenAI

from .models import DepositProducts, DepositOptions
from .serializers import DepositProductsSerializer, DepositOptionsSerializer

# .env 환경변수 읽기
env = environ.Env()
environ.Env.read_env()

# 1. F801: 데이터 수집 (금융감독원 API 호출 및 저장)
@api_view(['GET'])
def save_deposit_products(request):
    api_key = env('API_KEY')
    url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={api_key}&topFinGrpNo=020000&pageNo=1'
    
    response = requests.get(url).json()
    
    # 상품 정보 저장
    for base in response.get('result').get('baseList'):
        fin_prdt_cd = base.get('fin_prdt_cd')
        
        # 이미 존재하는 상품인지 확인 후 저장
        if not DepositProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).exists():
            save_data = {
                'fin_prdt_cd': base.get('fin_prdt_cd'),
                'kor_co_nm': base.get('kor_co_nm'),
                'fin_prdt_nm': base.get('fin_prdt_nm'),
                'etc_note': base.get('etc_note'),
                'join_deny': int(base.get('join_deny')),
                'join_member': base.get('join_member'),
                'join_way': base.get('join_way'),
                'spcl_cnd': base.get('spcl_cnd'),
            }
            serializer = DepositProductsSerializer(data=save_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

    # 옵션 정보 저장
    for option in response.get('result').get('optionList'):
        fin_prdt_cd = option.get('fin_prdt_cd')
        product = DepositProducts.objects.get(fin_prdt_cd=fin_prdt_cd)
        
        # 중복 저장 방지 (상품 코드와 기간이 같은 옵션이 있는지 확인)
        if not DepositOptions.objects.filter(product=product, save_trm=option.get('save_trm'), intr_rate_type_nm=option.get('intr_rate_type_nm')).exists():
            save_data = {
                'fin_prdt_cd': option.get('fin_prdt_cd'),
                'intr_rate_type_nm': option.get('intr_rate_type_nm'),
                'intr_rate': option.get('intr_rate'),
                'intr_rate2': option.get('intr_rate2'),
                'save_trm': int(option.get('save_trm')),
            }
            serializer = DepositOptionsSerializer(data=save_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(product=product)
                
    return Response({"message": "저장 완료!"}, status=status.HTTP_201_CREATED)


# 2. F802 (조회) & 3. F803 (입력)
class DepositProductList(APIView):
    # F802: 전체 정기예금 상품 목록 조회
    def get(self, request):
        products = DepositProducts.objects.all()
        serializer = DepositProductsSerializer(products, many=True)
        # 테스트 코드 호환: count + results 형식으로 반환
        return Response({
            'count': products.count(),
            'results': serializer.data,
        })

    # F803: 새로운 금융상품 데이터 추가 (options 중첩 데이터도 함께 처리)
    def post(self, request):
        data = request.data
        options_data = data.pop('options', []) if isinstance(data, dict) else []

        # 상품 저장
        serializer = DepositProductsSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            product = serializer.save()

            # 옵션 저장 (요청 본문에 options 가 포함된 경우)
            for option in options_data:
                option_serializer = DepositOptionsSerializer(data=option)
                if option_serializer.is_valid():
                    option_serializer.save(product=product)

            # 저장된 상품을 다시 직렬화하여 options 포함 반환
            result_serializer = DepositProductsSerializer(product)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)


# 4. F804: 특정 상품의 옵션 리스트 조회
@api_view(['GET'])
def deposit_product_options(request, fin_prdt_cd):
    try:
        product = DepositProducts.objects.get(fin_prdt_cd=fin_prdt_cd)
        options = product.options.all()
        serializer = DepositOptionsSerializer(options, many=True)
        return Response(serializer.data)
    except DepositProducts.DoesNotExist:
        return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 5. F805: 최고 우대금리가 가장 높은 상품과 그 옵션을 함께 조회
@api_view(['GET'])
def top_rate_product(request):
    # 가장 높은 최고 우대금리 찾기
    max_rate = DepositOptions.objects.aggregate(Max('intr_rate2'))['intr_rate2__max']
    if max_rate is None:
        return Response({"error": "데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 해당 금리를 가진 옵션과 연결된 상품 조회
    top_option = DepositOptions.objects.filter(intr_rate2=max_rate).select_related('product').first()
    product = top_option.product

    # F805 요구사항: 상품 + 옵션 리스트를 함께 반환
    product_serializer = DepositProductsSerializer(product)
    return Response({
        'product': product_serializer.data,
        'options': product_serializer.data.get('options', []),
    })


# 6. F811: AI 더미 데이터 생성 (Upstage AI - solar-pro3 활용)
@api_view(['GET'])
def generate_dummy_data(request):
    client = OpenAI(
        api_key=env('UPSTAGE_API_KEY'),
        base_url=env('UPSTAGE_BASE_URL')
    )

    prompt = """
    실제 은행의 정기예금 상품과 유사한 더미 데이터 1개를 JSON 형식으로 만들어줘.
    반드시 아래 JSON 형식만 출력하고, 설명이나 마크다운 없이 순수 JSON만 응답해줘:
    {
        "fin_prdt_cd": "DUMMY_001",
        "kor_co_nm": "AI 은행",
        "fin_prdt_nm": "AI 파워 정기예금",
        "etc_note": "중도해지 시 우대금리 미적용",
        "join_deny": 1,
        "join_member": "실명의 개인",
        "join_way": "인터넷, 스마트폰",
        "spcl_cnd": "급여이체 고객 우대"
    }
    """

    # streaming 방식으로 응답 수신
    stream = client.chat.completions.create(
        model="solar-pro",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        temperature=0.8,
        max_tokens=1024,
    )

    result = ""
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            result += delta

    return Response({"dummy_data": result})


# F804 심화: 특정 상품 코드로 상품 단건 + 옵션 함께 조회
@api_view(['GET'])
def deposit_product_detail(request, fin_prdt_cd):
    try:
        product = DepositProducts.objects.get(fin_prdt_cd=fin_prdt_cd)
        serializer = DepositProductsSerializer(product)
        return Response(serializer.data)
    except DepositProducts.DoesNotExist:
        return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)


# 전체 옵션 목록 조회 (페이지네이션 지원)
class DepositOptionList(APIView):
    def get(self, request):
        options = DepositOptions.objects.all()
        serializer = DepositOptionsSerializer(options, many=True)
        # 테스트 코드에서 response.data['results'], response.data['count'] 를 기대함
        return Response({
            'count': options.count(),
            'results': serializer.data,
        })
