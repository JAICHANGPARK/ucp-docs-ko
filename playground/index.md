# UCP 플레이그라운드

전체 UCP checkout 흐름을 단계별로 체험해 보세요. 이 인터랙티브 데모는 브라우저에서 완전히 동작하며, 각 단계에서 payload를 시뮬레이션하고 실제 UCP 스키마 기준으로 검증합니다.

## 1. 플랫폼 프로필

플랫폼 capability 프로필을 선택하세요. 이 선택에 따라 협상되는 확장(예: fulfillment, discount)이 결정됩니다.

### Configuration

플랫폼 유형 표준 (코어만) 고급 (모든 확장)

기본 checkout 및 주문 조회를 지원합니다.

Capabilities (지원 기능) 복사

다음으로 →

## 2. Discovery

플랫폼이 `/.well-known/ucp`를 조회합니다. 아래 응답은 Business capability와 Platform 프로필의 교집합만 보이도록 필터링되어 있습니다.

GET 요청

```
GET /.well-known/ucp HTTP/1.1
Host: business.example.com
Accept: application/json
```

응답 (필터링됨)

← 이전 다음으로 →

## 3. Capability 협상

Platform과 Business capability의 교집합입니다. 부모가 없는(orphaned) 확장은 제거됩니다.

Business Capabilities

결과 교집합

← 이전 다음으로 →

## 4. Checkout 생성

플랫폼이 세션을 시작합니다. 아래 오류 응답은 엄격한 `message.json` 스키마를 따릅니다.

요청 Payload

Response

시뮬레이션 시나리오:

구매자 이메일 누락 배송지 누락 요청 실행

← 이전 다음 단계 →

## 5. Checkout 업데이트

검증 오류를 해소할 수 있도록 누락 정보를 채워 checkout을 업데이트합니다.

PATCH 요청 업데이트 실행

Response

← 이전 다음 단계 →

## 6. 결제 Instrument 발급

payment handler 흐름을 시뮬레이션해 결제 credential을 획득합니다.

### 핸들러 선택

**Shop Pay**\
com.shopify.shop_pay

**Google Pay**\
com.google.pay

Credential 발급

발급된 Instrument

← 이전 다음 단계 →

## 7. Checkout 완료

발급된 instrument를 제출해 거래를 최종 확정하고 주문을 생성합니다.

요청 완료 실행

응답 (주문 생성)

**성공!** 주문 ID: 생성됨.

← 이전 다음 단계 →

## 8. Webhook 시뮬레이션

백엔드 이벤트(예: 배송센터 업데이트)가 Agent로 webhook을 푸시하는 과정을 시뮬레이션합니다.

### 이벤트 트리거

이 동작은 Business 서버에서 실행되며 Platform webhook URL로 데이터를 푸시합니다.

"배송됨" 이벤트 시뮬레이션

Webhook Payload (POST) 푸시 알림

```
// 이벤트 트리거를 기다리는 중...
```

← 이전

이 데모에 대해

이 playground는 브라우저에서 동작하는 시뮬레이션입니다. UCP 프로토콜 흐름을 설명하기 위한 mock 로직을 사용하며, 프로덕션 코드 레퍼런스로 사용되도록 설계되지는 않았습니다. 실제 구현 예시와 모범 사례는 [GitHub samples](https://github.com/Universal-Commerce-Protocol/samples)를 참고하세요.
