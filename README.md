<table width="100%">
  <tr>
    <td width="68%" valign="top">
      <h1>최우녕</h1>
      <strong>Production AI · Backend · Runtime</strong>
      <p>운영 증거와 실패 조건을 보존하고, 검증된 판단만 제한된 변경으로 연결한다.</p>
    </td>
    <td width="32%" align="right" valign="top">
      <a href="https://woonyong-kr.github.io/"><img alt="Portfolio" src="https://img.shields.io/badge/Portfolio-Technical_Notes-0969da?style=flat-square"></a><br>
      <a href="mailto:woonyong.kr@gmail.com"><img alt="Email" src="https://img.shields.io/badge/Email-woonyong.kr%40gmail.com-555?style=flat-square"></a><br>
      <a href="https://github.com/woonyong-kr/jekyll-theme-velog"><img alt="Open source template" src="https://img.shields.io/badge/Open_Source-Public_Template-238636?style=flat-square"></a>
    </td>
  </tr>
</table>

<details open>
  <summary><h2>대표 공개 프로젝트</h2></summary>

  <table width="100%">
    <tr>
      <td valign="top">
        <h3><a href="https://github.com/woonyong-kr/k8s-ops">Kyro — Kubernetes 장애 증거 기반 GitOps</a></h3>
        <p>Kubernetes 장애 증거를 규칙으로 판정하고, 허용된 manifest 변경만 Draft PR로 제안한다.</p>
        <p>
          <a href="https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml"><img alt="Kyro CI" src="https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml/badge.svg?branch=main"></a>
          <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white">
          <img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white">
          <img alt="NATS" src="https://img.shields.io/badge/NATS-27AAE1?style=flat-square&logo=natsdotio&logoColor=white">
          <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white">
        </p>
        <p><strong>검증</strong> Backend 203 tests · frontend typecheck/lint/vitest/build · Helm/RBAC · in-process/NATS 의미 동등성</p>
        <p><a href="https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md">Golden Path</a> · <a href="https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py">RCA 규칙 코드</a> · <a href="https://github.com/woonyong-kr/k8s-ops/blob/main/tests/test_golden_path_safety_contracts.py">안전 계약 테스트</a></p>
      </td>
    </tr>
    <tr>
      <td valign="top">
        <h3><a href="https://github.com/woonyong-kr/minidb">MiniDB — 디스크 기반 SQL 엔진</a></h3>
        <p>SQL parser부터 planner, B+Tree/heap, buffer pool과 디스크 페이지까지 C11로 연결한다.</p>
        <p>
          <a href="https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml"><img alt="MiniDB CI" src="https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml/badge.svg?branch=main"></a>
          <img alt="C11" src="https://img.shields.io/badge/C-11-A8B9CC?style=flat-square&logo=c&logoColor=black">
          <img alt="Tests" src="https://img.shields.io/badge/Tests-224%2F224-238636?style=flat-square">
        </p>
        <p><strong>측정</strong> 100만 행 범위 조회 73.9 → 3,218 ops/s · INSERT 2,751 → 591,429 ops/s</p>
        <p><a href="https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md">벤치마크 조건</a> · <a href="https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c">B+Tree</a> · <a href="https://github.com/woonyong-kr/minidb#어떻게-확인하나">재현 방법</a></p>
      </td>
    </tr>
    <tr>
      <td valign="top">
        <h3><a href="https://github.com/woonyong-kr/pintos">PintOS — 가상 메모리와 Copy-on-Write</a></h3>
        <p>fork Copy-on-Write, 공유 frame 참조 계수와 swap slot 수명, 우선순위 선점을 커널 코드로 검증한다.</p>
        <p>
          <a href="https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml"><img alt="PintOS CI" src="https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml/badge.svg?branch=main"></a>
          <img alt="C" src="https://img.shields.io/badge/C-x86--64-A8B9CC?style=flat-square&logo=c&logoColor=black">
          <img alt="Tests" src="https://img.shields.io/badge/Tests-141%2F141-238636?style=flat-square">
        </p>
        <p><strong>검증</strong> thread 27/27 · VM 114/114 · GitHub Actions x86-64 QEMU</p>
        <p><a href="https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c">COW fault</a> · <a href="https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c">Swap</a> · <a href="https://github.com/woonyong-kr/pintos/tree/main/docs/pintos">구현 기록</a></p>
      </td>
    </tr>
    <tr>
      <td valign="top">
        <h3><a href="https://github.com/woonyong-kr/dx_framework">JFramework — C++ 엔진과 C# 콘텐츠 사이의 변경 경계</a></h3>
        <p>C++ 엔진 655개 API의 변경을 C# 프레임워크에서 흡수해 협업사 10곳의 콘텐츠와 분리한다.</p>
        <p>
          <a href="https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml"><img alt="JFramework CI" src="https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml/badge.svg?branch=main"></a>
          <img alt="C sharp" src="https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white">
          <img alt="C plus plus" src="https://img.shields.io/badge/C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white">
          <img alt="Contract tests" src="https://img.shields.io/badge/Coroutine-Contract_Tests-238636?style=flat-square">
        </p>
        <p><a href="https://github.com/woonyong-kr/dx_framework#코드-지도">코드 지도</a> · <a href="https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md">프록시 경계</a> · <a href="https://github.com/woonyong-kr/dx_framework/tree/main/tests/JCoroutine.ContractTests">독립 계약 테스트</a></p>
      </td>
    </tr>
    <tr>
      <td valign="top">
        <h3><a href="https://github.com/woonyong-kr/jekyll-theme-velog">jekyll-theme-velog — GitHub Pages 공개 템플릿</a></h3>
        <p>설정 파일로 프로필·검색·시리즈·다크 모드를 구성하는 MIT Jekyll starter theme.</p>
        <p>
          <a href="https://github.com/woonyong-kr/jekyll-theme-velog/actions/workflows/deploy.yml"><img alt="Theme Pages" src="https://github.com/woonyong-kr/jekyll-theme-velog/actions/workflows/deploy.yml/badge.svg?branch=main"></a>
          <a href="https://github.com/woonyong-kr/jekyll-theme-velog/releases"><img alt="Release" src="https://img.shields.io/github/v/release/woonyong-kr/jekyll-theme-velog?style=flat-square"></a>
          <a href="https://github.com/woonyong-kr/jekyll-theme-velog/blob/main/LICENSE"><img alt="MIT License" src="https://img.shields.io/github/license/woonyong-kr/jekyll-theme-velog?style=flat-square"></a>
          <img alt="Public template" src="https://img.shields.io/badge/GitHub-Public_Template-238636?style=flat-square&logo=github">
        </p>
        <p><a href="https://woonyong-kr.github.io/jekyll-theme-velog/">데모</a> · <a href="https://github.com/woonyong-kr/jekyll-theme-velog#빠른-시작">설치</a> · <a href="https://github.com/woonyong-kr/jekyll-theme-velog/blob/main/CONTRIBUTING.md">기여 방법</a></p>
      </td>
    </tr>
  </table>
</details>

<details open>
  <summary><h2>공개 저장소 상태</h2></summary>

<!-- repository_health:start -->
| 저장소 | 상태 | 주 언어 | 검증 | 최근 변경 |
|---|---|---|---|---|
| [Kyro](https://github.com/woonyong-kr/k8s-ops) | [![Kyro CI](https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml) | Python | Backend 203 tests | [fix: 평가로 찾은 규칙 판별 결함 5건 개선](https://github.com/woonyong-kr/k8s-ops/commit/8c9e546fece4345fbac01c07c3d71f49c9b1da46) |
| [MiniDB](https://github.com/woonyong-kr/minidb) | [![MiniDB CI](https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml) | C | 224/224 tests | [build: sanitizer 선택 / 224개 테스트 / CI 게이트](https://github.com/woonyong-kr/minidb/commit/7b7c43ff93e350a8feecc6d049d4e8e2828937bc) |
| [PintOS](https://github.com/woonyong-kr/pintos) | [![PintOS CI](https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml) | C++ | 141/141 CI | [fix: 실제 우선순위 선점 / 141개 회귀 검증 / checkout v6](https://github.com/woonyong-kr/pintos/commit/ea154f87730d9d3ac492bb234166382ca3531493) |
| [JFramework](https://github.com/woonyong-kr/dx_framework) | [![JFramework CI](https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml) | C# | Coroutine contracts | [test: 코루틴 계약 / 독립 실행 / CI 게이트](https://github.com/woonyong-kr/dx_framework/commit/78c917a276b69c8746dcfb73c08803f698798ab9) |
| [Jekyll Theme](https://github.com/woonyong-kr/jekyll-theme-velog) | [![Jekyll Theme CI](https://github.com/woonyong-kr/jekyll-theme-velog/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/woonyong-kr/jekyll-theme-velog/actions/workflows/deploy.yml) | HTML | MIT · Public template | [fix: Pages canonical URL / 배포 경로 재현 / SEO 검증](https://github.com/woonyong-kr/jekyll-theme-velog/commit/927e76eb627b391354879342b477d64013c54cdd) |
<!-- repository_health:end -->
</details>

<details open>
  <summary><h2>협업 저장소 기여</h2></summary>

<!-- collaboration:start -->
- **Jungle-303-04/demo-game** · [fix: pin working admission toggle console](https://github.com/Jungle-303-04/demo-game/pull/22) · 2026-07-25
- **Jungle-303-04/demo-game** · [[복구] api-server - 로비 replicas 원복 PR](https://github.com/Jungle-303-04/demo-game/pull/21) · 2026-07-24
- **Jungle-303-04/demo-game** · [perf: 게임 파드 예약량 / 게임 노드 용량 / 스케줄링 여유](https://github.com/Jungle-303-04/demo-game/pull/20) · 2026-07-24
- **Jungle-303-04/final** · [fix: AI 입력창 고정 / 패널 스크롤 경계 / viewport 높이](https://github.com/Jungle-303-04/final/pull/662) · 2026-07-24
- **Jungle-303-04/final** · [파드 상세 원인 표시와 사이드 패널 UX 통합](https://github.com/Jungle-303-04/final/pull/661) · 2026-07-24
- **Jungle-303-04/final** · [fix: 위험 파드 클릭을 리소스 상세로 연결](https://github.com/Jungle-303-04/final/pull/660) · 2026-07-24
<!-- collaboration:end -->
</details>

<details open>
  <summary><h2>최근 공개 작업</h2></summary>

<!-- recent_work:start -->
- **Jekyll Theme** · [fix: Pages canonical URL / 배포 경로 재현 / SEO 검증](https://github.com/woonyong-kr/jekyll-theme-velog/commit/927e76eb627b391354879342b477d64013c54cdd) · 2026-08-03
- **Jekyll Theme** · [feat: 공식 Pages 배포 / 템플릿 검증 / 설정 하드코딩 제거](https://github.com/woonyong-kr/jekyll-theme-velog/commit/df36b865b4079574f6ee6bc8e6fed4bbb7f81441) · 2026-08-03
- **PintOS** · [fix: 실제 우선순위 선점 / 141개 회귀 검증 / checkout v6](https://github.com/woonyong-kr/pintos/commit/ea154f87730d9d3ac492bb234166382ca3531493) · 2026-08-03
- **PintOS** · [fix: MLFQS 고정소수점 / 전체 스레드 갱신 / CI 분리](https://github.com/woonyong-kr/pintos/commit/09df7c8e83a5c5a46d0c0b8aa36a3fa7ce59745d) · 2026-08-03
- **JFramework** · [test: 코루틴 계약 / 독립 실행 / CI 게이트](https://github.com/woonyong-kr/dx_framework/commit/78c917a276b69c8746dcfb73c08803f698798ab9) · 2026-08-03
- **JFramework** · [fix: 부모 비활성 판정 / Enum 검색 / 코루틴 정리](https://github.com/woonyong-kr/dx_framework/commit/e622a6115e2d66d587af59e19b7827d5e82286d0) · 2026-08-03
<!-- recent_work:end -->
</details>

<details>
  <summary><h2>사용하는 오픈소스</h2></summary>
  <br>
  <table width="100%">
    <tr>
      <th align="left">운영·데이터</th>
      <td>
        <a href="https://kubernetes.io/"><img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white"></a>
        <a href="https://nats.io/"><img alt="NATS" src="https://img.shields.io/badge/NATS-27AAE1?style=flat-square&logo=natsdotio&logoColor=white"></a>
        <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"></a>
        <a href="https://prometheus.io/"><img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white"></a>
        <a href="https://grafana.com/oss/loki/"><img alt="Loki" src="https://img.shields.io/badge/Loki-F46800?style=flat-square&logo=grafana&logoColor=white"></a>
      </td>
    </tr>
    <tr>
      <th align="left">백엔드·런타임</th>
      <td>
        <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"></a>
        <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"></a>
        <a href="https://isocpp.org/"><img alt="C plus plus" src="https://img.shields.io/badge/C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white"></a>
        <a href="https://dotnet.microsoft.com/"><img alt="Dotnet" src="https://img.shields.io/badge/.NET-512BD4?style=flat-square&logo=dotnet&logoColor=white"></a>
      </td>
    </tr>
    <tr>
      <th align="left">자동화·배포</th>
      <td>
        <a href="https://github.com/features/actions"><img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white"></a>
        <a href="https://helm.sh/"><img alt="Helm" src="https://img.shields.io/badge/Helm-0F1689?style=flat-square&logo=helm&logoColor=white"></a>
        <a href="https://www.docker.com/"><img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"></a>
        <a href="https://jekyllrb.com/"><img alt="Jekyll" src="https://img.shields.io/badge/Jekyll-CC0000?style=flat-square&logo=jekyll&logoColor=white"></a>
      </td>
    </tr>
  </table>
</details>

<sub>공개 저장소 상태·커밋·merged PR은 GitHub API에서 매일 수집한다. README에는 최근 항목만 표시하고 최소 메타데이터 원장은 저장소에 누적한다.</sub>
