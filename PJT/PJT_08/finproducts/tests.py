import os
from rest_framework.test import APIClient
from django.test import TestCase, override_settings

from finlife.settings import BASE_DIR

# 시드 데이터 설정
DATA_FIXTURE = os.path.join(BASE_DIR, 'finproducts', 'fixture', 'deposit_products.json')


class APITestCase(TestCase):
    """
    API 테스트를 위한 기본 설정 및 Client 초기화
    """

    def setUp(self):
        """
        테스트 실행 전 호출
        """
        self.client = APIClient()

    @override_settings(DEBUG=False)
    def test_deposit_products_list(self):
        """
        GET /products/deposit/
        """
        with open(DATA_FIXTURE, 'r', encoding='utf-8') as f:
            # fixture/deposit_products.json 파일 내용 직접 로드
            self.client.post('/products/deposit/', f.read(), format='json')

        response = self.client.get('/products/deposit/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data['results'], list))
        self.assertTrue(isinstance(response.data['count'], int))
        self.assertTrue(len(response.data['results']) > 0)

    @override_settings(DEBUG=False)
    def test_deposit_products_detail(self):
        """
        GET /products/deposit/{fin_prdt_cd}/
        """
        with open(DATA_FIXTURE, 'r', encoding='utf-8') as f:
            # fixture/deposit_products.json 파일 내용 직접 로드
            self.client.post('/products/deposit/', f.read(), format='json')

        # fixture의 첫 번째 상품 fin_prdt_cd 사용
        response = self.client.get('/products/deposit/0100000108')

        self.assertEqual(response.status_code, 200)
        self.assertIn('fin_prdt_cd', response.data)
        self.assertIn('options', response.data)
        self.assertIsInstance(response.data['options'], list)

    @override_settings(DEBUG=False)
    def test_deposit_options_list(self):
        """
        GET /products/deposit/options/
        """
        with open(DATA_FIXTURE, 'r', encoding='utf-8') as f:
            # fixture/deposit_products.json 파일 내용 직접 로드
            self.client.post('/products/deposit/', f.read(), format='json')

        response = self.client.get('/products/deposit/options/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data['results'], list))
        self.assertTrue(isinstance(response.data['count'], int))
        self.assertTrue(len(response.data['results']) > 0)
    