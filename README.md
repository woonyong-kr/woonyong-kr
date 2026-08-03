<img width="100%" alt="GitHub 활동, 공개 저장소, 언어 비중과 기여 달력" src="./github-metrics.svg?v=20260804-2">

<p align="right"><a href="https://woonyong-kr.github.io">기술 기록</a> · <a href="mailto:woonyong.kr@gmail.com">이메일</a></p>

## 프로젝트

<table>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/woonyong-kr/k8s-ops">Kyro</a></h3>
      Kubernetes · FastAPI · PostgreSQL · NATS<br><br>
      장애 증거 → 규칙 판정 → 제한된 Draft PR<br>
      <strong>판정 94.3% → 100% · 안전 계약 45종</strong><br><br>
      <a href="https://github.com/woonyong-kr/k8s-ops/blob/main/docs/GOLDEN-PATH.md">설계</a> · <a href="https://github.com/woonyong-kr/k8s-ops/blob/main/src/services/ai/agent/pipeline/causes.py">판정 코드</a> · <a href="https://github.com/woonyong-kr/k8s-ops/actions/workflows/ci.yml">CI</a>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/woonyong-kr/minidb">MiniDB</a></h3>
      C · B+Tree · Slotted Page · Buffer Pool<br><br>
      100만 행 범위 조회 <strong>73.9 → 3,218 ops/s</strong><br>
      INSERT <strong>2,751 → 591,429 ops/s · 224/224</strong><br><br>
      <a href="https://github.com/woonyong-kr/minidb/blob/main/docs/benchmark-postgres.md">벤치마크</a> · <a href="https://github.com/woonyong-kr/minidb/blob/main/src/storage/bptree.c">B+Tree</a> · <a href="https://github.com/woonyong-kr/minidb/actions/workflows/ci.yml">CI</a>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/woonyong-kr/pintos">PintOS</a></h3>
      C/C++ · Virtual Memory · Copy-on-Write<br><br>
      공유 frame·swap slot → 참조 계수·소유권<br>
      <strong>thread 27/27 · VM 114/114 · 141/141</strong><br><br>
      <a href="https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/vm.c">COW fault</a> · <a href="https://github.com/woonyong-kr/pintos/blob/main/pintos/vm/anon.c">Swap</a> · <a href="https://github.com/woonyong-kr/pintos/actions/workflows/ci.yml">CI</a>
    </td>
    <td width="50%" valign="top">
      <h3><a href="https://github.com/woonyong-kr/dx_framework">JFramework</a></h3>
      C# · C++ · P/Invoke · Runtime Architecture<br><br>
      엔진 655개 API ↔ 공용 계층 ↔ 10개 협력사<br>
      <strong>콘텐츠 변경 경계 단일화</strong><br><br>
      <a href="https://github.com/woonyong-kr/dx_framework/tree/main/Sources/1.%20JEngine/2.%20EngineCore/3.%20EventSystem">이벤트</a> · <a href="https://github.com/woonyong-kr/dx_framework/blob/main/docs/examples/CliProxyExample.md">프록시 경계</a> · <a href="https://github.com/woonyong-kr/dx_framework/actions/workflows/ci.yml">CI</a>
    </td>
  </tr>
</table>

<details>
  <summary><strong>설계 기록</strong></summary>
  <br>
  <a href="https://woonyong-kr.github.io/#/posts/rule-catalog">규칙 카탈로그를 평가 데이터로 역산</a> ·
  <a href="https://woonyong-kr.github.io/#/posts/pg-benchmark">B+Tree 범위 조회 병목</a> ·
  <a href="https://woonyong-kr.github.io/#/posts/swap-sharing">Copy-on-Write 이후 swap 소유권</a> ·
  <a href="https://woonyong-kr.github.io/#/posts/cli-proxy">엔진과 협력사 사이의 변경 경계</a>
</details>

<sub>팀 기여와 후속 확장 분리 · 실행 환경과 입력 규모를 포함한 성능 수치 · [지표 자동화](./.github/PROFILE-METRICS.md)</sub>
