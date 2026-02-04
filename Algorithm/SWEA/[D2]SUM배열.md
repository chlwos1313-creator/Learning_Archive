# **[D2] SUM배열**

## 문제개요

다음 100X100의 2차원 배열이 주어질 때, 각 행의 합, 각 열의 합, 각 대각선의 합 중 최댓값을 구하는 프로그램을 작성하여라.
다음과 같은 5X5 배열에서 최댓값은 29이다.
[제약 사항]

총 10개의 테스트 케이스가 주어진다.
배열의 크기는 100X100으로 동일하다.
각 행의 합은 integer 범위를 넘어가지 않는다.
동일한 최댓값이 있을 경우, 하나의 값만 출력한다.

**[입력]**
각 테스트 케이스의 첫 줄에는 테스트 케이스 번호가 주어지고 그 다음 줄부터는 2차원 배열의 각 행 값이 주어진다.

**[출력]**

부호와 함께 테스트 케이스의 번호를 출력하고, 공백 문자 후 테스트 케이스의 답을 출력한다.

**실습코드**
```python
import sys

sys.stdin = open('sample_input.txt')

for _ in range(10):
    tc = int(input())
    n = 100
    box = [list(map(int, input().split())) for _ in range(n)]
    total = 0
    max_3 = 0
    max_4 = 0
    for i in range(n):
        max_1 = 0
        for j in range(n):
            max_1 += box[i][j]

        if total < max_1:
            total = max_1

    for i in range(n):
        max_1 = 0
        for j in range(n):

            max_1 += box[j][i]
        if total < max_1:
            total = max_1

    for i in range(n):
        max_3 += box[i][i]
    if total < max_3:
        total = max_3

    for i in range(n):
        max_4 += box[i][n - 1 - i]
    if total < max_4:
        total = max_4

    print(f'#{tc} {total}')
```