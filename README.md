# 최우녕

AI가 프로덕션을 바꿀 때 필요한 권한 경계와 평가 기준을 코드로 만든다.
게임사에서 3D·XR 콘텐츠와 공용 엔진 계층을 개발하고 프로젝트 7건을 이끌었다. 크래프톤 정글에서는 운영체제·데이터베이스·Kubernetes 장애 복구 시스템을 직접 구현하며 설계 판단을 테스트와 측정으로 검증했다.

[이력서·기술 기록](https://woonyong-kr.github.io) · [이메일](mailto:woonyong.kr@gmail.com)

## 대표 프로젝트

| 프로젝트 | 해결한 문제 | 확인할 근거 |
|---|---|---|
| [Kyro](https://github.com/woonyong-kr/k8s-ops) | Kubernetes 장애 증거를 규칙으로 판정하고, 허용된 변경만 Draft PR로 제안한다. 판정 평가 **94.3% → 100%**, 안전 계약 테스트 **45종** | [Golden Path](https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md) · [규칙 판정](https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py) · [권한 경계](https://github.com/woonyong-kr/k8s-ops/blob/main/src/domains/gitops/source_patch.py) |
| [MiniDB](https://github.com/woonyong-kr/minidb) | C11로 SQL parser부터 B+Tree·slotted page·buffer pool까지 연결했다. 100만 행에서 범위 조회 **73.9 → 3,218 ops/s**, INSERT **2,751 → 591,429 ops/s** | [측정 조건과 한계](https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md) · [B+Tree](https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c) · [Pager](https://github.com/woonyong-kr/minidb/blob/main/src/storage/pager.c) |
| [PintOS](https://github.com/woonyong-kr/pintos) | fork를 Copy-on-Write로 바꾸고, 공유 프레임과 swap slot의 수명을 참조 계수와 소유권으로 관리했다 | [COW fault](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c) · [Swap](https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c) · [구현 기록](https://github.com/woonyong-kr/pintos/tree/main/docs/pintos) |
| [JFramework](https://github.com/woonyong-kr/dx_framework) | 개발 중인 C++ 엔진과 10개 협력사 콘텐츠 사이에 C# 프레임워크를 두어 변경 경계를 한곳으로 모았다 | [코루틴](https://github.com/woonyong-kr/dx_framework/blob/main/Sources/1.%20JEngine/2.%20EngineCore/2.%20Main/JCoroutine.cs) · [이벤트](https://github.com/woonyong-kr/dx_framework/tree/main/Sources/1.%20JEngine/2.%20EngineCore/3.%20EventSystem) · [프록시 경계](https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md) |

## 작업 기준

- 팀 프로젝트는 맡은 범위와 종료 후 확장을 구분한다.
- 성능 수치는 실행 환경·입력 규모·반복 횟수와 함께 남긴다.
- 성공 경로뿐 아니라 빈 결과·부분 실패·중복·권한 거부를 테스트한다.
- 구현하지 않은 범위와 재현할 수 없는 운영 수치는 한계로 명시한다.

## 읽을 거리

- [규칙 카탈로그를 평가 데이터로 역산한 과정](https://woonyong-kr.github.io/#/posts/rule-catalog)
- [B+Tree를 만들고도 범위 조회가 느렸던 이유](https://woonyong-kr.github.io/#/posts/pg-benchmark)
- [Copy-on-Write 이후 swap slot의 소유권 문제](https://woonyong-kr.github.io/#/posts/swap-sharing)
- [655개 엔진 함수와 10개 협력사 사이에 경계를 둔 이유](https://woonyong-kr.github.io/#/posts/cli-proxy)
