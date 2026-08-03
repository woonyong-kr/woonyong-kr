# 최우녕

<p align="center">
  <strong>Production AI · Runtime Architecture · Systems</strong><br>
  권한 경계 · 결정론적 평가 · 운영 증거 · 재현 가능한 성능 측정
</p>

<p align="center">
  <img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white">
  <img alt="C#" src="https://img.shields.io/badge/C%23-512BD4?logo=dotnet&logoColor=white">
  <img alt="C++" src="https://img.shields.io/badge/C%2B%2B-00599C?logo=cplusplus&logoColor=white">
  <img alt="C" src="https://img.shields.io/badge/C-A8B9CC?logo=c&logoColor=111111">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white">
</p>

<p align="center">
  <a href="https://woonyong-kr.github.io"><img alt="Portfolio" src="https://img.shields.io/badge/Portfolio-기술_기록-111827"></a>
  <a href="mailto:woonyong.kr@gmail.com"><img alt="Email" src="https://img.shields.io/badge/Email-woonyong.kr-EA4335?logo=gmail&logoColor=white"></a>
</p>

## 대표 프로젝트

| 프로젝트 | 핵심 판단 | 검증 근거 |
|---|---|---|
| [Kyro](https://github.com/woonyong-kr/k8s-ops) [![CI](https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml/badge.svg)](https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml) | 장애 증거 → 규칙 판정 → 허용된 변경만 Draft PR · 판정 평가 **94.3% → 100%** · 안전 계약 **45종** | [Golden Path](https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md) · [규칙 판정](https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py) · [권한 경계](https://github.com/woonyong-kr/k8s-ops/blob/main/src/domains/gitops/source_patch.py) |
| [MiniDB](https://github.com/woonyong-kr/minidb) [![CI](https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml/badge.svg)](https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml) | SQL parser → B+Tree → slotted page → buffer pool · 100만 행 범위 조회 **73.9 → 3,218 ops/s** · INSERT **2,751 → 591,429 ops/s** | [측정 조건과 한계](https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md) · [B+Tree](https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c) · [Pager](https://github.com/woonyong-kr/minidb/blob/main/src/storage/pager.c) |
| [PintOS](https://github.com/woonyong-kr/pintos) [![CI](https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml/badge.svg)](https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml) | fork → Copy-on-Write · 공유 frame·swap slot 수명 → 참조 계수·소유권 · thread/VM **141/141 통과** | [COW fault](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c) · [Swap](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c) · [구현 기록](https://github.com/woonyong-kr/pintos/tree/main/docs/pintos) |
| [JFramework](https://github.com/woonyong-kr/dx_framework) [![CI](https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml/badge.svg)](https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml) | C++ 엔진 655개 API ↔ C# 공용 계층 ↔ 10개 협력사 콘텐츠 · 변경 경계 단일화 | [코루틴](https://github.com/woonyong-kr/dx_framework/blob/main/Sources/1.%20JEngine/2.%20EngineCore/2.%20Main/JCoroutine.cs) · [이벤트](https://github.com/woonyong-kr/dx_framework/tree/main/Sources/1.%20JEngine/2.%20EngineCore/3.%20EventSystem) · [프록시 경계](https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md) |

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

## 공개 코드 스냅샷

공개 저장소 기준 언어 분포 · 최근 활동 · 관심 주제. 매주 GitHub Actions로 갱신.

![Public GitHub metrics](./github-metrics.svg)
