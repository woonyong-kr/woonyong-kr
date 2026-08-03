# 프로필 자동화

## 기본 원칙

- README의 모든 프로젝트·코드·문서·CI 항목은 실제 URL로 연결한다.
- GitHub가 기본 제공하는 기여 달력과 Pinned 저장소를 README에서 다시 그리지 않는다.
- 언어 비중·커밋 수·streak처럼 채용 판단과 직접 연결되지 않는 지표는 첫 화면에서 제외한다.
- 자동화는 문장을 새로 쓰지 않고 `최근 작업` 영역의 실제 커밋 링크만 갱신한다.

## 자동 갱신

`scripts/update_recent_work.py`가 `.github/profile-projects.json`에 등록된 저장소의 최신 사람 커밋을 가져와 README의 다음 마커 사이를 교체한다.

```text
<!-- recent_work:start -->
<!-- recent_work:end -->
```

GitHub Actions는 매주 월요일과 수동 실행 시 동작한다. `dependabot[bot]`과 `github-actions[bot]` 커밋은 제외한다.

## 선택 지표

`Refresh profile index` workflow의 `extended_metrics` 입력을 켜면 lowlighter 확장 SVG를 별도 생성한다. 팔로워·별·업적·습관·애니 설정은 삭제하지 않았지만 기본 README에서는 노출하지 않는다. SVG 내부 링크는 GitHub 프로필에서 신뢰할 수 있는 탐색 수단이 아니므로 시각 참고용으로만 사용한다.
