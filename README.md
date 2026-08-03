# 최우녕

**Production AI · Runtime Architecture · Systems**

권한 경계 · 결정론적 평가 · 운영 증거 · 재현 가능한 성능 측정
Kubernetes · C#/C++ · C · Python

[이력서·기술 기록](https://woonyong-kr.github.io) · [이메일](mailto:woonyong.kr@gmail.com)

## 대표 프로젝트

| 프로젝트 | 핵심 판단 | 검증 근거 |
|---|---|---|
| [Kyro](https://github.com/woonyong-kr/k8s-ops) | 장애 증거 → 규칙 판정 → 허용된 변경만 Draft PR · 판정 평가 **94.3% → 100%** · 안전 계약 **45종** | [Golden Path](https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md) · [규칙 판정](https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py) · [권한 경계](https://github.com/woonyong-kr/k8s-ops/blob/main/src/domains/gitops/source_patch.py) |
| [MiniDB](https://github.com/woonyong-kr/minidb) | SQL parser → B+Tree → slotted page → buffer pool · 100만 행 범위 조회 **73.9 → 3,218 ops/s** · INSERT **2,751 → 591,429 ops/s** | [측정 조건과 한계](https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md) · [B+Tree](https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c) · [Pager](https://github.com/woonyong-kr/minidb/blob/main/src/storage/pager.c) |
| [PintOS](https://github.com/woonyong-kr/pintos) | fork → Copy-on-Write · 공유 frame·swap slot 수명 → 참조 계수·소유권 | [COW fault](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c) · [Swap](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c) · [구현 기록](https://github.com/woonyong-kr/pintos/tree/main/docs/pintos) |
| [JFramework](https://github.com/woonyong-kr/dx_framework) | C++ 엔진 655개 API ↔ C# 공용 계층 ↔ 10개 협력사 콘텐츠 · 변경 경계 단일화 | [코루틴](https://github.com/woonyong-kr/dx_framework/blob/main/Sources/1.%20JEngine/2.%20EngineCore/2.%20Main/JCoroutine.cs) · [이벤트](https://github.com/woonyong-kr/dx_framework/tree/main/Sources/1.%20JEngine/2.%20EngineCore/3.%20EventSystem) · [프록시 경계](https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md) |

## 작업 기준

- 팀 기여 범위 / 종료 후 확장 분리
- 실행 환경 / 입력 규모 / 반복 횟수 포함 성능 기록
- 빈 결과 / 부분 실패 / 중복 / 권한 거부 회귀 테스트
- 미구현 범위 / 재현 불가 운영 수치 명시

## 읽을 거리

- [규칙 카탈로그를 평가 데이터로 역산한 과정](https://woonyong-kr.github.io/#/posts/rule-catalog)
- [B+Tree를 만들고도 범위 조회가 느렸던 이유](https://woonyong-kr.github.io/#/posts/pg-benchmark)
- [Copy-on-Write 이후 swap slot의 소유권 문제](https://woonyong-kr.github.io/#/posts/swap-sharing)
- [655개 엔진 함수와 10개 협력사 사이에 경계를 둔 이유](https://woonyong-kr.github.io/#/posts/cli-proxy)
