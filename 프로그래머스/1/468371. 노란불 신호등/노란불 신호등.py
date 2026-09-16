import math

def solution(signals):
    # 각 신호등의 전체 주기 (초록 + 노란 + 빨간)
    periods = [g + y + r for g, y, r in signals]
    
    # 모든 신호등 주기의 최소공배수(LCM) 계산
    max_t = periods[0]
    for p in periods[1:]:
        max_t = (max_t * p) // math.gcd(max_t, p)
        
    # 1초부터 전체 주기가 반복되는 최대 시간(max_t)까지 탐색
    for t in range(1, max_t + 1):
        all_yellow = True
        
        for i, (g, y, r) in enumerate(signals):
            # t초일 때, 해당 신호등의 주기 내 위치 (0-based)
            rem = (t - 1) % periods[i]
            
            # 노란불 구간: 초록불(g) 시간 이후부터 초록+노란(g+y) 시간 이전까지
            if not (g <= rem < g + y):
                all_yellow = False
                
                
        # 모든 신호등이 노란불 조건을 만족한 경우 현재 시간 반환
        if all_yellow:
            return t
            
    # 전체 주기(최소공배수)를 다 돌았음에도 없다면 영원히 발생하지 않음
    return -1