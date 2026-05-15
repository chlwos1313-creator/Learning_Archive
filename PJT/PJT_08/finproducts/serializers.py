from rest_framework import serializers
from .models import DepositProducts, DepositOptions

class DepositOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOptions
        fields = '__all__'
        read_only_fields = ('product',)

class DepositProductsSerializer(serializers.ModelSerializer):
    # F804 등에서 상품 정보를 조회할 때 옵션 리스트도 함께 포함하여 반환할 수 있도록 설정
    options = DepositOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProducts
        fields = '__all__'
