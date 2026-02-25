# TIL (Today I Learned) - 2026-02-25
## 1. CSS 상속 (Inheritance) & 우선순위
부모 요소의 스타일이 자식에게 전파되는 규칙이며, 어떤 스타일이 최종 적용될지 결정하는 핵심 논리이다.

### 상속되는 속성: color, font-family, text-align, line-height, visibility 등 주로 텍스트 가독성과 관련된 속성들이다.

### 상속되지 않는 속성: width, height, margin, padding, border, background, z-index 등 박스 모델 및 배치와 관련된 속성들이다.

### 우선순위 (Cascading): 스타일이 충돌할 때 적용되는 순위이다.

1. !important (가급적 지양)

2. 인라인 스타일 (HTML 태그 안에 직접 작성)

3. ID 선택자 (#id)

4. Class/속성/가상 선택자 (.class)

5. 태그 선택자 (div, p)

### 실무 팁: 데이터 분석 대시보드 제작 시, 공통적인 테마 컬러나 폰트는 **body**나 **root**에 선언하여 상속을 적극 활용하는 것이 코드 다이어트에 좋다.

## 2. CSS 결합자 (Combinators) & 가상 클래스
요소 간의 계층 관계를 정의하여 특정 타겟을 정교하게 타격하는 방법이다.

### 자손 결합자 (div p): div 안에 있는 모든 **p**를 선택한다.

### 자식 결합자 (div > p): div 바로 아래의 직계 자식 **p**만 선택한다.

### 형제 결합자:

h1 + p: h1 바로 뒤에 붙은 첫 번째 형제 **p**만 선택한다.

h1 ~ p: h1 뒤에 오는 모든 형제 **p**를 선택한다.

### 가상 클래스 (Pseudo-classes):

:hover: 마우스를 올렸을 때 스타일을 변경한다. (버튼 상호작용 등)

:nth-child(n): n번째 자식만 골라 스타일을 준다. (표 데이터 줄무늬 처리 등)

## 3. 현대적 레이아웃: Flexbox & Grid
Position보다 더 강력하고 유연하게 요소를 배치하는 최신 기법이다.

### Flexbox (1차원): 행 또는 열 방향으로 요소를 배치한다.

display: flex;: 부모를 Flex Container로 만든다.

justify-content: 메인축(가로) 정렬을 담당한다. (center, space-between 등)

align-items: 교차축(세로) 정렬을 담당한다.

### CSS Grid (2차원): 가로와 세로를 동시에 제어하는 바둑판 형태의 레이아웃이다.

grid-template-columns: 열의 개수와 크기를 정의한다.

gap: 요소 사이의 간격을 아주 쉽게 조절한다.

### 활용: UI/UX 디자인에서 복잡한 카드 뉴스 형태나 데이터 테이블을 만들 때 Grid를 쓰면 코드가 훨씬 직관적이다.

## 4. 반응형 웹과 미디어 쿼리 (Media Queries)
기기 화면 크기에 따라 레이아웃을 다르게 보여주는 핵심 기술이다.

### @media: @media (max-width: 768px) 처럼 작성하여 태블릿이나 모바일 환경에 맞는 스타일을 별도로 지정한다.

### 데이터 시각화 적용: PC에서는 그래프를 가로로 3개 나열하고, 모바일에서는 세로로 1개씩 나오게 조절할 때 필수적이다.

## 5. Antigravity & AI 워크플로우
### 자동 저장 (Auto Save): afterDelay 설정을 통해 Ctrl + S 압박에서 벗어나 실시간으로 코드를 반영한다.

### 브라우저 에이전트: 작성한 HTML/CSS 코드가 실제 의도대로 렌더링되는지 실시간 화면 검증을 수행한다.

### 에셋 생성: 디자인에 필요한 아이콘이나 배경 이미지는 generate_image (Nano Banana)를 통해 즉석에서 수급한다# TIL (Today I Learned) - 2026-02-25
## 1. CSS 상속 (Inheritance) & 우선순위
부모 요소의 스타일이 자식에게 전파되는 규칙이며, 어떤 스타일이 최종 적용될지 결정하는 핵심 논리이다.

### 상속되는 속성: color, font-family, text-align, line-height, visibility 등 주로 텍스트 가독성과 관련된 속성들이다.

### 상속되지 않는 속성: width, height, margin, padding, border, background, z-index 등 박스 모델 및 배치와 관련된 속성들이다.

### 우선순위 (Cascading): 스타일이 충돌할 때 적용되는 순위이다.

1. !important (가급적 지양)

2. 인라인 스타일 (HTML 태그 안에 직접 작성)

3. ID 선택자 (#id)

4. Class/속성/가상 선택자 (.class)

5. 태그 선택자 (div, p)

### 실무 팁: 데이터 분석 대시보드 제작 시, 공통적인 테마 컬러나 폰트는 **body**나 **root**에 선언하여 상속을 적극 활용하는 것이 코드 다이어트에 좋다.

## 2. CSS 결합자 (Combinators) & 가상 클래스
요소 간의 계층 관계를 정의하여 특정 타겟을 정교하게 타격하는 방법이다.

### 자손 결합자 (div p): div 안에 있는 모든 **p**를 선택한다.

### 자식 결합자 (div > p): div 바로 아래의 직계 자식 **p**만 선택한다.

### 형제 결합자:

h1 + p: h1 바로 뒤에 붙은 첫 번째 형제 **p**만 선택한다.

h1 ~ p: h1 뒤에 오는 모든 형제 **p**를 선택한다.

### 가상 클래스 (Pseudo-classes):

:hover: 마우스를 올렸을 때 스타일을 변경한다. (버튼 상호작용 등)

:nth-child(n): n번째 자식만 골라 스타일을 준다. (표 데이터 줄무늬 처리 등)

## 3. 현대적 레이아웃: Flexbox & Grid
Position보다 더 강력하고 유연하게 요소를 배치하는 최신 기법이다.

### Flexbox (1차원): 행 또는 열 방향으로 요소를 배치한다.

display: flex;: 부모를 Flex Container로 만든다.

justify-content: 메인축(가로) 정렬을 담당한다. (center, space-between 등)

align-items: 교차축(세로) 정렬을 담당한다.

### CSS Grid (2차원): 가로와 세로를 동시에 제어하는 바둑판 형태의 레이아웃이다.

grid-template-columns: 열의 개수와 크기를 정의한다.

gap: 요소 사이의 간격을 아주 쉽게 조절한다.

### 활용: UI/UX 디자인에서 복잡한 카드 뉴스 형태나 데이터 테이블을 만들 때 Grid를 쓰면 코드가 훨씬 직관적이다.

## 4. 반응형 웹과 미디어 쿼리 (Media Queries)
기기 화면 크기에 따라 레이아웃을 다르게 보여주는 핵심 기술이다.

### @media: @media (max-width: 768px) 처럼 작성하여 태블릿이나 모바일 환경에 맞는 스타일을 별도로 지정한다.

### 데이터 시각화 적용: PC에서는 그래프를 가로로 3개 나열하고, 모바일에서는 세로로 1개씩 나오게 조절할 때 필수적이다.

## 5. Antigravity & AI 워크플로우
### 자동 저장 (Auto Save): afterDelay 설정을 통해 Ctrl + S 압박에서 벗어나 실시간으로 코드를 반영한다.

### 브라우저 에이전트: 작성한 HTML/CSS 코드가 실제 의도대로 렌더링되는지 실시간 화면 검증을 수행한다.

### 에셋 생성: 디자인에 필요한 아이콘이나 배경 이미지는 generate_image (Nano Banana)를 통해 즉석에서 수급한다
