# [D3]큐 미로의 거리 확인용

**개요**
NxN 크기의 미로에서 출발지 목적지가 주어진다.

이때 최소 몇 개의 칸을 지나면 출발지에서 도착지에 다다를 수 있는지 알아내는 프로그램을 작성하시오.

경로가 있는 경우 출발에서 도착까지 가는데 지나야 하는 최소한의 칸 수를, 경로가 없는 경우 0을 출력한다.

다음은 5x5 미로의 예이다. 1은 벽, 0은 통로를 나타내며 미로 밖으로 벗어나서는 안된다.

마지막 줄의 2에서 출발해서 0인 통로를 따라 이동하면 맨 윗줄의 3에 5개의 칸을 지나 도착할 수 있다

**[입력]**
첫 줄에 테스트 케이스 개수 T가 주어진다.  1<=T<=50

다음 줄부터 테스트 케이스의 별로 미로의 크기 N과 N개의 줄에 걸쳐 미로의 통로와 벽에 대한 정보가 주어진다. 5<=N<=100

0은 통로, 1은 벽, 2는 출발, 3은 도착이다.

**[출력]**

각 줄마다 "#T" (T는 테스트 케이스 번호)를 출력한 뒤, 답을 출력한다.


**[실습코드]**

```python
def f(N, M):
    q = []
    v = [[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if M[i][j] == 2: q.append((i, j, 0)); v[i][j] = 1
    
    p = 0
    while p < len(q):
        r, c, d = q[p]; p += 1
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < N and 0 <= nc < N and not v[nr][nc]:
                if M[nr][nc] == 3: return d
                if M[nr][nc] == 0:
                    v[nr][nc] = 1
                    q.append((nr, nc, d + 1))
    return 0

T = int(input())
for t in range(1, T + 1):
    N = int(input())
    M = [list(map(int, input().strip())) for _ in range(N)]
    print(f"#{t} {f(N, M)}")
```