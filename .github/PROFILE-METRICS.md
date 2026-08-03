# 프로필 지표 자동화

프로필의 `github-metrics.svg`는 매주 월요일과 수동 실행 시 갱신됩니다.

## 기본 지표

- GitHub 공개 활동: 고정한 `lowlighter/metrics` v3.34 소스에서 생성
- 대표 저장소 언어 비중: GitHub REST API의 Linguist 바이트를 네 저장소에서 직접 합산
- 출력: 두 결과를 하나의 SVG로 병합한 뒤 변경이 있을 때만 커밋

대표 저장소를 바꾸려면 [metrics.yml](./workflows/metrics.yml)의 `PROFILE_REPOSITORIES`만 수정합니다. 언어 색상은 [append_repository_languages.py](../scripts/append_repository_languages.py)의 `LANGUAGE_COLORS`에서 관리합니다.

## 선택 지표

Actions의 `Profile metrics`를 수동 실행하고 `extended=true`를 선택하면 다음 지표가 활성화됩니다.

- 팔로워
- 별을 받은 저장소
- 활동 배지
- 코딩 습관 차트
- 반년 기여 달력
- PR·이슈 후속 활동
- 코드 변경량
- AniList 애니·만화·캐릭터

AniList는 저장소 변수 `ANILIST_USERNAME`이 있을 때만 켜집니다. 사용자 범위 지표가 필요하면 저장소 secret `METRICS_TOKEN`을 추가하고, 기본 실행은 저장소 전용 `GITHUB_TOKEN`만 사용합니다.

## 수치 해석

언어 비중은 기여도나 숙련도를 뜻하지 않습니다. 지정한 공개 저장소의 GitHub Linguist 바이트 합계를 주 1회 스냅샷으로 보여주는 색인입니다.
