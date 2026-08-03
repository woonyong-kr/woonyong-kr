<div align="center">

## 최우녕

백엔드 · AI 인프라

운영 증거 · 권한 경계 · 결정론적 평가 · 재현 가능한 성능 측정

[기술 기록](https://woonyong-kr.github.io) · [이메일](mailto:woonyong.kr@gmail.com)

<img width="100%" alt="공개 GitHub 활동과 대표 저장소 언어 비중" src="./github-metrics.svg">

</div>

## 대표 작업

### [Kyro](https://github.com/woonyong-kr/k8s-ops) — 운영 증거에서 안전한 변경까지

Kubernetes 장애 증거 수집 → 규칙 판정 → 허용된 변경만 Draft PR

`Kubernetes` · `FastAPI` · `PostgreSQL` · `NATS` · 판정 평가 **94.3% → 100%** · 안전 계약 **45종** · [CI](https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml)

[Golden Path](https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md) · [규칙 판정](https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py) · [권한 경계](https://github.com/woonyong-kr/k8s-ops/blob/main/src/domains/gitops/source_patch.py)

### [MiniDB](https://github.com/woonyong-kr/minidb) — 저장 엔진을 직접 만들고 PostgreSQL과 비교

SQL parser → B+Tree → slotted page → buffer pool

100만 행 범위 조회 **73.9 → 3,218 ops/s** · INSERT **2,751 → 591,429 ops/s** · **224/224 tests** · [CI](https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml)

[측정 조건과 한계](https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md) · [B+Tree](https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c) · [Pager](https://github.com/woonyong-kr/minidb/blob/main/src/storage/pager.c)

### [PintOS](https://github.com/woonyong-kr/pintos) — Copy-on-Write와 공유 자원의 소유권

fork → Copy-on-Write · 공유 frame·swap slot → 참조 계수·소유권

thread **27/27** · VM **114/114** · 총 **141/141 tests** · [CI](https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml)

[COW fault](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c) · [Swap](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c) · [구현 기록](https://github.com/woonyong-kr/pintos/tree/main/docs/pintos)

### [JFramework](https://github.com/woonyong-kr/dx_framework) — 엔진과 콘텐츠 사이의 변경 경계

C++ 엔진 655개 API ↔ C# 공용 계층 ↔ 10개 협력사 콘텐츠

`C#` · `C++` · `P/Invoke` · 변경 경계 단일화 · [CI](https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml)

[코루틴](https://github.com/woonyong-kr/dx_framework/blob/main/Sources/1.%20JEngine/2.%20EngineCore/2.%20Main/JCoroutine.cs) · [이벤트](https://github.com/woonyong-kr/dx_framework/tree/main/Sources/1.%20JEngine/2.%20EngineCore/3.%20EventSystem) · [프록시 경계](https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md)

## 설계 기록

- [규칙 카탈로그를 평가 데이터로 역산한 과정](https://woonyong-kr.github.io/#/posts/rule-catalog)
- [B+Tree를 만들고도 범위 조회가 느렸던 이유](https://woonyong-kr.github.io/#/posts/pg-benchmark)
- [Copy-on-Write 이후 swap slot의 소유권 문제](https://woonyong-kr.github.io/#/posts/swap-sharing)
- [655개 엔진 함수와 10개 협력사 사이에 경계를 둔 이유](https://woonyong-kr.github.io/#/posts/cli-proxy)

<sub>팀 기여와 종료 후 확장 분리 · 성능 수치에 실행 환경과 입력 규모 명시 · 미구현 범위와 재현 불가 수치 제외 · [지표 자동화](./.github/PROFILE-METRICS.md)</sub>
