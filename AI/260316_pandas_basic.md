# Pandas 핵심 요약 (Data Analysis TIL)

## 1. Pandas 개요 및 설치
Pandas는 파이썬에서 표 형태의 데이터(Structured Data)를 다루기 위한 가장 강력한 라이브러리입니다.

Series: 1차원 배열 형태 (컬럼 1개)

DataFrame: 2차원 표 형태 (Series들의 모임)

```Python
import pandas as pd
import numpy as np
```

# 데이터 로드 (CSV 기준)

df = pd.read_csv('filename.csv')

## 2. 데이터 선택 및 필터링 (Indexing)
데이터프레임에서 원하는 부분만 골라내는 가장 기초적이면서 중요한 과정입니다.

컬럼 선택: df['column_name'] 또는 df[['col1', 'col2']] (여러 개일 땐 대괄호 두 번)

조건 필터링: df[df['age'] >= 20]

위치 기반 선택:

df.loc[행_이름, 열_이름]: 레이블 기반 (명칭)

df.iloc[행_번호, 열_번호]: 인덱스 번호 기반 (숫자)

## 3. 데이터 전처리 (Pre-processing)
분석 전 데이터를 깔끔하게 다듬는 과정입니다.

결측치 처리:

df.isnull().sum(): 결측치 개수 확인

df.dropna(): 결측치 삭제

df.fillna(값): 결측치를 특정 값으로 채우기

파생 변수 생성: df['total'] = df['a'] + df['b']

중복 제거: df.drop_duplicates()

## 4. 데이터 집계 및 그룹화 (Aggregation)
데이터의 통계적 특성을 파악할 때 사용합니다.

기본 통계: df.describe(), df.mean(), df.value_counts()

Groupby (분할-적용-결합): 특정 컬럼을 기준으로 그룹화하여 통계 산출

```Python
df.groupby('category')['price'].mean()
```

## 5. 데이터 재구조화 (Reshaping)
표의 형태를 바꾸어 분석하기 쉬운 구조로 만듭니다.

Pivot Table: 엑셀의 피벗 테이블과 동일한 기능

```Python
df.pivot_table(index='date', columns='city', values='temp', aggfunc='mean')
Melt: 가로로 긴 데이터를 세로로 길게 (Wide to Long)
```

```Python
df.melt(id_vars=['id'], value_vars=['math', 'eng'], var_name='subject', value_name='score')
```

## 6. 데이터 결합 (Merging)
여러 개의 테이블을 하나로 합치는 작업입니다.

Concat: 단순히 위아래나 옆으로 이어 붙이기

Merge: SQL의 Join처럼 공통된 키(Key)를 기준으로 합치기

```Python
pd.merge(left_df, right_df, on='key_column', how='inner')
```