def solution(message, spoiler_ranges):
    # 1. 메시지 내 모든 단어의 [단어 문자열, 시작 인덱스, 끝 인덱스] 추출
    words = []
    n = len(message)
    i = 0
    while i < n:
        if message[i] != ' ':
            start = i
            while i < n and message[i] != ' ':
                i += 1
            end = i - 1
            words.append((message[start:end + 1], start, end))
        else:
            i += 1

    # 2. 스포 방지 구간이 아닌 곳에 등장한 단어 집합 구하기
    # (단어의 문자 중 어떤 것도 spoiler_ranges에 포함되지 않는 단어)
    unspoiled_words = set()
    
    # 각 스포 방지 구간(index)마다 그 구간이 해제되면서 '완전히 공개되는' 단어 목록
    # key: range_idx, value: list of word_text
    revealed_at = [[] for _ in range(len(spoiler_ranges))]

    for text, w_start, w_end in words:
        # 이 단어가 걸쳐 있는 spoiler_ranges의 인덱스들을 찾음
        covering_ranges = []
        for r_idx, (r_start, r_end) in enumerate(spoiler_ranges):
            # 단어 구간 [w_start, w_end]와 스포 구간 [r_start, r_end]가 겹치는지 확인
            if not (w_end < r_start or w_start > r_end):
                covering_ranges.append(r_idx)

        if not covering_ranges:
            # 어떤 스포 방지 구간에도 걸치지 않은 단어
            unspoiled_words.add(text)
        else:
            # 스포 방지 단어인 경우, 단어에 걸친 가장 마지막 구간이 클릭될 때 전체 공개됨
            last_range_idx = covering_ranges[-1]
            revealed_at[last_range_idx].append(text)

    # 3. 0번 구간부터 순서대로 해제하며 중요한 단어 판별
    seen_spoiled_words = set()
    important_word_count = 0

    for r_idx in range(len(spoiler_ranges)):
        for word in revealed_at[r_idx]:
            # 조건 1: 일반 구간에 등장한 적이 없어야 함
            # 조건 2: 이전에 이미 공개된 스포 방지 단어와 중복되지 않아야 함
            if word not in unspoiled_words and word not in seen_spoiled_words:
                important_word_count += 1
                seen_spoiled_words.add(word)

    return important_word_count