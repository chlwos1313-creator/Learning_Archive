[TIL] Qwen2.5-VL을 이용한 VQA 다지선다 태스크 미세 조정
1. 작업 개요
목표: 이미지와 질문이 주어졌을 때, 4개의 선택지(a, b, c, d) 중 정답을 골라내는 VQA 모델 학습.

모델: Qwen/Qwen2.5-VL-3B-Instruct (최신 멀티모달 LLM).

환경: Kaggle Dual T4 GPU (분산 처리 및 양자화 활용).

2. 주요 기술 스택 (Tech Stack)
Model: Qwen2.5-VL-3B (Vision-Language Model)

Library: transformers, peft (LoRA), bitsandbytes (4-bit Quantization)

Optimization: * LoRA (Low-Rank Adaptation): 전체 파라미터가 아닌 일부 레이어만 학습하여 메모리 효율 극대화.

4-bit NF4 Quantization: 모델 크기를 줄여 16GB GPU에서도 구동 가능하게 설정.

Gradient Accumulation: 작은 배치 사이즈의 한계를 극복하기 위해 그래디언트를 누적하여 학습.

3. 핵심 코드 (주석 간소화 버전)

```Python
import os, torch, gc
import pandas as pd
from PIL import Image
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 1. 모델 및 양자화 설정
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

# 2. 프로세서 및 모델 로드
MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
processor = AutoProcessor.from_pretrained(MODEL_ID, min_pixels=384*384, max_pixels=384*384)
base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    MODEL_ID, 
    quantization_config=bnb_config, 
    device_map="auto"
)

# 3. LoRA(Low-Rank Adaptation) 설정
lora_config = LoraConfig(
    r=32, lora_alpha=64, lora_dropout=0.1,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    task_type="CAUSAL_LM"
)
model = get_peft_model(prepare_model_for_kbit_training(base_model), lora_config)

# 4. 학습 루프 (핵심 로직)
# GradScaler 및 Autocast를 사용하여 Mixed Precision 학습 진행
scaler = torch.cuda.amp.GradScaler()
for epoch in range(1):
    model.train()
    for step, batch in enumerate(train_loader):
        batch = {k: v.to(model.device) for k, v in batch.items()}
        with torch.cuda.amp.autocast():
            loss = model(**batch).loss / 8 # Gradient Accumulation 적용
        
        scaler.scale(loss).backward()
        if (step + 1) % 8 == 0:
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()
            torch.cuda.empty_cache() # 메모리 관리
```

4. 배운 점 및 해결한 문제
Dual GPU 활용: device_map="auto" 설정을 통해 Kaggle의 T4 GPU 2개에 모델 레이어를 자동으로 분산 배치함.

메모리 최적화: 3B 규모의 모델도 4비트 양자화와 LoRA를 결합하면 단일 GPU 메모리 안에서 안정적으로 학습이 가능함을 확인.

데이터 파이프라인: apply_chat_template을 활용해 이미지와 텍스트가 섞인 멀티모달 데이터를 모델 포맷에 맞게 변환하는 과정을 익힘.