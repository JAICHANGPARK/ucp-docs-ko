# 체크아웃 기능 - EP 바인딩

## 소개

Embedded Checkout Protocol(ECP)은 UCP Embedded Protocol(EP) 전송 바인딩의 checkout 특화 구현입니다. **host**가 **business**의 checkout UI를 임베드하고, 구매자 상호작용 이벤트를 수신하며, 주소/결제 선택 같은 핵심 사용자 동작을 위임받아 처리할 수 있게 합니다. ECP는 REST와 같은 전송 바인딩으로, **무엇**을 담는지가 아니라 **어떻게** 통신하는지를 정의합니다.

### W3C Payment Request 개념 정렬

ECP는 **[W3C Payment Request API](https://www.w3.org/TR/payment-request/)** 에서 개념적 영감을 받아 임베디드 체크아웃 시나리오에 맞게 재해석되었습니다. Payment Request에 익숙한 개발자라면 유사한 패턴을 볼 수 있지만, 실행 모델은 다릅니다.

**W3C Payment Request:** 브라우저 주도 모델입니다. Business가 `show()`를 호출하면 브라우저가 네이티브 결제 시트를 렌더링하고, 이벤트는 payment handler에서 business 방향으로 흐릅니다.

**Embedded Checkout:** Business 주도 모델입니다. Host가 business checkout UI를 iframe/webview에 임베드하며, 이벤트는 양방향으로 흐릅니다. 선택적 delegation을 통해 특정 상호작용을 host가 네이티브로 처리할 수 있습니다.

| 개념              | W3C Payment Request             | Embedded Checkout                                                |
| ----------------- | ------------------------------- | ---------------------------------------------------------------- |
| **초기화**        | `new PaymentRequest()`          | `continue_url`로 임베디드 컨텍스트 로드                          |
| **UI 준비 완료**  | `show()`가 Promise 반환         | `ec.start` 알림                                                  |
| **결제수단 변경** | `paymentmethodchange` 이벤트    | `ec.payment.change` 알림                                         |
| **주소 변경**     | `shippingaddresschange` 이벤트  | `ec.fulfillment.change`, `ec.fulfillment.address_change_request` |
| **결제 제출**     | 사용자 수락 → `PaymentResponse` | 위임된 `ec.payment.credential_request`                           |
| **완료**          | `response.complete()`           | `ec.complete` 알림                                               |
| **오류/메시지**   | Promise reject                  | `ec.messages.change` 알림                                        |

**핵심 차이:** W3C Payment Request에서는 브라우저가 결제 흐름을 오케스트레이션합니다. Embedded Checkout에서는 business가 임베디드 컨텍스트 안에서 흐름을 오케스트레이션하며, 필요 시 특정 UI(결제수단 선택, 주소 선택)를 host에 위임해 네이티브 경험을 제공할 수 있습니다.

## 용어와 참여자

### 커머스 역할

- **Business:** 상품/서비스와 checkout 경험을 제공하는 판매자.
- **Buyer:** 실제 구매를 수행하는 최종 사용자.

### 기술 컴포넌트

- **Host:** checkout을 임베드하는 애플리케이션(예: AI Agent 앱, 슈퍼앱, 브라우저). **Payment Handler** 및 사용자 인증을 담당합니다.
- **Embedded Checkout:** iframe/webview로 렌더링되는 business checkout UI. checkout 흐름과 주문 생성을 담당합니다.
- **Payment Handler:** 사용자 인증(생체/PIN)과 credential 발급을 수행하는 보안 컴포넌트.

## 요구사항

### 디스커버리

ECP 지원 여부는 두 단계에서 신호됩니다. service-level discovery에서 capability 지원을 선언하고, checkout 응답에서 세션별 지원 여부와 허용 delegation을 확정합니다.

#### 서비스 레벨 디스커버리

Business가 `/.well-known/ucp` profile에서 `embedded` 전송을 광고하면, Embedded Checkout Protocol 지원을 선언한 것입니다.

**서비스 디스커버리 예시:**

```json
{
    "services": {
        "dev.ucp.shopping": [
            {
                "version": "2026-01-11",
                "transport": "rest",
                "schema": "https://ucp.dev/services/shopping/openapi.json",
                "endpoint": "https://merchant.example.com/ucp/v1"
            },
            {
                "version": "2026-01-11",
                "transport": "mcp",
                "schema": "https://ucp.dev/services/shopping/mcp.openrpc.json",
                "endpoint": "https://merchant.example.com/ucp/mcp"
            },
            {
                "version": "2026-01-11",
                "transport": "embedded",
                "schema": "https://ucp.dev/services/shopping/embedded.openrpc.json"
            }
        ]
    }
}
```

service 정의에 `embedded`가 없으면, business는 `continue_url` 기반 리다이렉트 checkout 연속만 지원합니다.

#### 체크아웃별 구성

service-level discovery는 business의 ECP 지원 사실만 알릴 뿐, 모든 checkout 세션에서 항상 활성화됨을 보장하지는 않습니다. Business는 특정 세션의 ECP 가능 여부와 허용 delegation을 표시하기 위해 checkout 응답에 `config.delegate`를 포함한 embedded service binding을 넣어야 합니다(**MUST**).

**Checkout 응답 예시:**

```json
{
    "id": "checkout_abc123",
    "status": "open",
    "continue_url": "https://merchant.example.com/checkout/abc123",
    "ucp": {
        "version": "2026-01-11",
        "services": {
            "dev.ucp.shopping": [
                {
                    "version": "2026-01-11",
                    "transport": "embedded",
                    "config": {
                        "delegate": ["payment.credential", "fulfillment.address_change"]
                    }
                }
            ]
        },
        "capabilities": {...},
        "payment_handlers": {...}
    }
}
```

`config.delegate` 배열은 해당 checkout 세션에서 business가 수용한 delegation을 나타냅니다. 즉, host가 `ec_delegate`로 요청한 항목과 business 허용 정책의 교집합입니다. 이 값은 다음에 따라 달라질 수 있습니다.

- **장바구니 구성**: 일부 상품은 business 처리 결제 흐름이 필요할 수 있음
- **에이전트 권한**: 인증된 에이전트는 더 많은 delegation을 받을 수 있음
- **비즈니스 정책**: 리스크 규칙, 지역 제한 등

`config.delegate`가 포함된 embedded service binding이 존재하면:

- `continue_url`을 통한 ECP checkout이 가능함
- `config.delegate`로 business 수용 delegation을 확인 가능
- 이는 `ec.ready` 핸드셰이크의 `delegate` 필드와 대응됨

checkout 응답에 embedded service binding이 없으면 (service-level discovery에서 embedded 지원을 광고했더라도), 해당 checkout은 `continue_url` 기반 리다이렉트 연속만 지원합니다.

### 임베디드 체크아웃 URL 로딩

Host가 embedded service binding이 포함된 checkout 응답을 받으면, `continue_url`을 임베디드 컨텍스트로 로드해 ECP 세션을 시작할 수 있습니다(**MAY**).

임베디드 로드 전에 host는 다음을 수행하는 것이 권장됩니다(**SHOULD**).

1. `config.delegate`에서 사용 가능한 delegation 확인
1. host가 지원하려는 delegation에 대한 handler 준비
1. business 요구 시 인증 자격증명 사전 준비

세션 시작 시 host는 `ec_` 접두사 ECP 쿼리 파라미터를 `continue_url`에 추가해야 합니다(**MUST**).

모든 ECP 파라미터는 다양한 임베딩 환경 호환성을 위해 HTTP 헤더가 아닌 URL query string으로 전달됩니다. `ec_` 접두사를 사용해 네임스페이스 오염을 피하고 business 고유 파라미터와 구분합니다.

- `ec_version`(string, **REQUIRED**): 세션 UCP 버전(`YYYY-MM-DD`), checkout 응답 버전과 일치해야 함
- `ec_auth`(string, **OPTIONAL**): business가 정의한 형식의 인증 토큰
- `ec_delegate`(string, **OPTIONAL**): host가 처리하려는 delegation의 쉼표 구분 목록. embedded service binding의 `config.delegate` 부분집합이어야 합니다(**SHOULD**).
- `ec_color_scheme`(string, **OPTIONAL**): checkout UI 색상 선호값(`light`, `dark`). 생략 시 Embedded Checkout은 시스템 선호를 따릅니다.

#### 인증(Authentication)

**토큰 형식:**

- `auth` 파라미터 형식은 business가 정의합니다.
- 일반적으로 JWT, OAuth 토큰, API 키, 세션 식별자 등을 사용합니다.
- Business는 기대 토큰 형식과 검증 절차를 문서화해야 합니다(**MUST**).

**예시(참고용 - JWT 기반):**

```json
// One possible implementation using JWT
{
  "alg": "HS256",
  "typ": "JWT"
}
{
  "iat": 1234567890,
  "exp": 1234568190,
  "jti": "unique-id",
  // ... business-specific claims ...
}
```

Business는 자체 보안 요구사항에 따라 인증을 검증해야 합니다(**MUST**).

**인증 포함 초기화 예시:**

```text
https://example.com/checkout/abc123?ec_version=2026-01-11&ec_auth=eyJ...
```

참고: 모든 쿼리 파라미터 값은 RFC 3986에 따라 URL 인코딩되어야 합니다.

#### 위임

선택 파라미터 `ec_delegate`는 구매자가 Embedded Checkout UI에서 직접 처리하는 대신 host가 네이티브로 처리하고 싶은 연산을 선언합니다. 각 delegation 식별자는 `ec.{delegation}_request` 패턴의 `_request` 메시지에 매핑됩니다.

**delegation 식별자 예시:**

| `ec_delegate` 값             | 대응 메시지                             |
| ---------------------------- | --------------------------------------- |
| `payment.instruments_change` | `ec.payment.instruments_change_request` |
| `payment.credential`         | `ec.payment.credential_request`         |
| `fulfillment.address_change` | `ec.fulfillment.address_change_request` |

확장은 자체 delegation 식별자를 정의할 수 있으며, 사용 가능한 옵션은 각 확장 명세를 참고하세요.

```text
?ec_version=2026-01-11&ec_delegate=payment.instruments_change,payment.credential,fulfillment.address_change
```

#### 컬러 스킴

선택 파라미터 `ec_color_scheme`은 host 앱과 checkout UI의 시각적 일관성을 위해 Embedded Checkout 색상 스킴을 host가 지정할 수 있게 합니다.

**허용 값:**

| 값      | 설명                                       |
| ------- | ------------------------------------------ |
| `light` | 라이트 스킴(밝은 배경, 어두운 텍스트) 사용 |
| `dark`  | 다크 스킴(어두운 배경, 밝은 텍스트) 사용   |

**기본 동작:**

`ec_color_scheme`이 없으면 Embedded Checkout은 다음 수단을 통해 구매자 시스템 선호를 사용할 수 있습니다. [`prefers-color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme) 미디어 쿼리 또는 [`Sec-CH-Prefers-Color-Scheme`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Sec-CH-Prefers-Color-Scheme) HTTP client hint를 활용할 수 있으며, 변경 감지 후 즉시 반영하는 것이 권장됩니다(**SHOULD**).

**구현 참고사항:**

- 기본적으로 Embedded Checkout은 구매자 시스템 색상 선호를 따르고 변경을 감지해 반영하는 것이 권장됩니다(**SHOULD**).
- `ec_color_scheme`이 명시되면 시스템 선호보다 우선 적용되어야 하며(**MUST**), 로드 즉시 반영되고 세션 동안 유지되어야 합니다.
- 지원하지 않는 값은 무시할 수 있습니다(**MAY**).

**예시:**

```text
https://example.com/checkout/abc123?ec_version=2026-01-11&ec_color_scheme=dark
```

#### 위임 협상

Delegation은 business 정책에서 최종 수락으로 좁혀지는 체인을 따릅니다.

```text
config.delegate ⊇ ec_delegate ⊇ ec.ready delegate
```

1. **Business 허용**(checkout 응답의 `config.delegate`): 해당 세션에서 business가 허용하는 delegation 집합
1. **Host 요청**(`ec_delegate` URL 파라미터): host가 네이티브 처리하려는 부분집합
1. **ECP 수락**(`ec.ready`의 `delegate`): Embedded Checkout이 실제 위임할 최종 부분집합

각 단계는 이전 단계의 부분집합입니다.

- host는 `config.delegate`에 있는 항목만 요청해야 합니다(**SHOULD**).
- business는 `config.delegate`에 없는 항목을 수락하지 않아야 하며(**SHOULD NOT**), 수락한 delegation을 `ec.ready`에서 확인해야 합니다(**MUST**).

### 위임 계약

Delegation은 host와 Embedded Checkout 사이의 구속력 있는 계약을 형성합니다. 다만 business 정책에 따라 Embedded Checkout은 인증/승인된 host에만 delegation을 제한할 수 있습니다(**MAY**).

#### 위임 수락

Embedded Checkout은 다음 기준으로 수용 delegation을 결정합니다.

- 인증 상태(`ec_auth` 파라미터)
- host 권한 수준
- business 정책

Embedded Checkout은 수락 delegation을 `ec.ready` 요청의 `delegate` 필드로 표시해야 합니다(**MUST**). ([`ec.ready`](#ecready) 참고) 요청 delegation이 수락되지 않으면 해당 capability는 Embedded Checkout 자체 UI로 처리해야 합니다(**MUST**).

#### 바인딩 요구사항

**delegation이 수락되면**, 양측은 구속 계약 상태에 들어갑니다.

**Embedded Checkout 책임:**

1. 해당 동작이 트리거되면 적절한 `{action}_request` 메시지를 전송해야 합니다(**MUST**).
1. 진행 전 host 응답을 대기해야 합니다(**MUST**).
1. 위임된 동작에 대해 자체 UI를 표시해서는 안 됩니다(**MUST NOT**).

**Host 책임:**

1. 수신한 모든 `{action}_request`에 응답해야 합니다(**MUST**).
1. 사용자가 취소하면 적절한 오류로 응답해야 합니다(**MUST**).
1. delegation 처리 중 로딩/처리 상태를 보여주는 것이 권장됩니다(**SHOULD**).

#### 3.3.3 위임 흐름

1. **Request**: Embedded Checkout이 현재 상태(`id` 포함)와 함께 `ec.{capability}.{action}_request` 메시지 전송
1. **Native UI**: Host가 위임 동작에 대한 네이티브 UI 제공
1. **Response**: Host가 동일 `id`를 가진 JSON-RPC `result` 또는 `error` 응답 반환
1. **Update**: Embedded Checkout이 상태를 갱신하고 후속 change 알림을 보낼 수 있음

[Payment Extension](#payment-extension) 및 [Fulfillment Extension](#fulfillment-extension)에서 capability별 delegation 상세를 확인할 수 있습니다.

### 내비게이션 제약

checkout이 embedded 모드로 렌더링될 때는 집중된 checkout 경험을 위해 checkout 외부 이동을 제한하는 것이 권장됩니다(**SHOULD**). 임베디드 뷰는 범용 브라우저가 아니라 checkout 흐름 제공이 목적입니다.

**내비게이션 요구사항:**

- embedded checkout은 checkout 흐름 외 URL로의 이동 시도를 차단/가로채는 것이 권장됩니다(**SHOULD**).
- checkout 이탈을 유도하는 UI 요소(외부 링크, 내비게이션 바 등)는 제거/비활성화하는 것이 권장됩니다(**SHOULD**).
- embedder는 컨테이너 레벨에서 추가 내비게이션 제한을 둘 수 있습니다(**MAY**).

**허용 예외:** checkout 완료를 위해 필요하면 다음 내비게이션 시나리오는 허용할 수 있습니다(**MAY**).

- 결제 제공자 리다이렉트: 오프사이트 결제 흐름
- 3D Secure 검증: 카드 인증 프레임/리다이렉트
- 은행 인가: 오픈뱅킹 등 인가 흐름
- 신원 검증: 필요 시 KYC/AML 준수 점검

이 예외 흐름은 완료 후 사용자를 checkout 흐름으로 복귀시키는 것이 권장됩니다(**SHOULD**).

## 전송 및 메시징

### 메시지 포맷

모든 ECP 메시지는 JSON-RPC 2.0 형식을 사용해야 합니다(**MUST**). ([RFC 7159](https://datatracker.ietf.org/doc/html/rfc7159)) 각 메시지는 다음을 포함해야 합니다(**MUST**).

- `jsonrpc`: **MUST** be `"2.0"`
- `method`: 메시지 이름(예: `"ec.start"`)
- `params`: 메시지별 payload(빈 객체 가능)
- `id`: (선택) 응답이 필요한 요청에서만 존재

### 메시지 타입

**요청(Request, `id` 포함):**

- 수신자의 응답이 필요함
- 고유 `id` 필드를 포함해야 함(**MUST**)
- 수신자는 동일 `id`로 응답해야 함(**MUST**)
- 응답은 `result` 또는 `error` 객체여야 함(**MUST**)
- 확인/데이터가 필요한 연산에 사용됨

**알림(Notification, `id` 없음):**

- 정보 전달용이며 응답을 기대하지 않음
- `id` 필드를 포함하면 안 됨(**MUST NOT**)
- 수신자는 응답을 보내면 안 됨(**MUST NOT**)
- 상태 업데이트 및 안내 이벤트에 사용됨

### 응답 처리

요청(`id`가 있는 메시지)의 경우 수신자는 다음 둘 중 하나로 응답해야 합니다(**MUST**).

**성공 응답:**

```json
{ "jsonrpc": "2.0", "id": "...", "result": {...} }
```

**오류 응답:**

```json
{ "jsonrpc": "2.0", "id": "...", "error": {...} }
```

### 통신 채널

#### 웹 기반 호스트 통신 채널

host가 웹 애플리케이션일 때는 host와 checkout window 간 `postMessage`로 통신이 시작됩니다. host는 임베디드 window의 `postMessage`를 수신해야 하며(**MUST**), 메시지 수신 시 origin이 checkout 시작에 사용한 `checkout_url`과 일치하는지 검증해야 합니다(**MUST**).

검증 후 host는 `MessageChannel`을 생성할 수 있으며(**MAY**), [`ec.ready` 응답](#ecready) 결과에서 포트 하나를 전달할 수 있습니다. host가 `MessagePort`로 응답한 경우 이후 모든 메시지는 해당 채널을 통해 전송되어야 합니다(**MUST**). 그렇지 않으면 host와 business는 origin 검증을 포함해 `window` 객체 간 `postMessage()`를 계속 사용해야 합니다(**MUST**).

#### 네이티브 호스트 통신 채널

host가 네이티브 앱일 때는 웹/네이티브 환경 간 `postMessage` 통신이 가능하도록 Embedded Checkout에 전역 객체를 주입해야 합니다(**MUST**). host는 다음 전역 객체 중 최소 하나를 생성해야 합니다(**MUST**).

- `window.EmbeddedCheckoutProtocolConsumer` (preferred)
- `window.webkit.messageHandlers.EmbeddedCheckoutProtocolConsumer`

이 객체는 다음 인터페이스를 구현해야 합니다(**MUST**).

```javascript
{
  postMessage(message: string): void
}
```

여기서 `message`는 JSON 문자열화된 JSON-RPC 2.0 메시지입니다. host는 처리 전에 JSON 문자열을 파싱해야 합니다(**MUST**).

host에서 Embedded Checkout으로 가는 메시지의 경우 host는 webview에 JavaScript를 주입해 `window.EmbeddedCheckoutProtocol.postMessage()`로 JSON-RPC 메시지를 전달해야 합니다(**MUST**). Embedded Checkout은 `ec.ready` 전송 전에 이 전역 객체를 초기화하고 `postMessage()` 수신 대기를 시작해야 합니다(**MUST**).

## 메시지 API 레퍼런스

### 메시지 분류

#### 코어 메시지

코어 메시지는 ECP 명세에서 정의되며 모든 구현이 지원해야 합니다(**MUST**). 모든 메시지는 Embedded Checkout에서 host 방향으로 전송됩니다.

| 분류             | 목적                               | 패턴         | 코어 메시지                                                                          |
| ---------------- | ---------------------------------- | ------------ | ------------------------------------------------------------------------------------ |
| **Handshake**    | host와 Embedded Checkout 연결 수립 | Request      | `ec.ready`                                                                           |
| **Lifecycle**    | checkout 상태 전이 알림            | Notification | `ec.start`, `ec.complete`                                                            |
| **State Change** | checkout 필드 변경 알림            | Notification | `ec.line_items.change`, `ec.buyer.change`, `ec.payment.change`, `ec.messages.change` |

#### 확장 메시지

확장은 추가 메시지 정의를 통해 Embedded 프로토콜을 확장할 수 있습니다(**MAY**). 확장 메시지는 다음 네이밍 규칙을 따라야 합니다(**MUST**).

- **알림(Notification)**: `ec.{capability}.change` - 상태 변경 알림(`id` 없음)
- **위임 요청**: `ec.{capability}.{action}_request` - 응답 필요(`id` 있음)

각 구성요소 의미:

- `{capability}`: discovery에서 합의된 capability 식별자
- `{action}`: 위임되는 구체 동작(예: `instruments_change`, `address_change`)
- `_request` 접미사: 응답이 필요한 delegation 지점임을 의미

### 핸드셰이크 메시지

#### `ec.ready`

렌더링 시 Embedded Checkout은 `ec.ready` 메시지로 상위 컨텍스트에 준비 완료를 브로드캐스트해야 합니다(**MUST**). 이 메시지는 host와 Embedded Checkout 사이의 보안 통신 채널을 초기화하고, 수락된 delegation을 전달하며, UCP checkout action으로 전달되지 않은 표시 전용 상태를 host가 제공할 수 있게 합니다.

- **방향:** Embedded Checkout → host
- **유형:** Request
- **페이로드:**
  - `delegate`(문자열 배열, **REQUIRED**): Embedded Checkout이 수락한 delegation 식별자 목록. `ec_delegate`(host 요청)와 checkout 응답의 `config.delegate`(business 허용)의 공통 부분집합이어야 합니다(**MUST**). 빈 배열은 delegation 미수락을 의미합니다.

**메시지 예시(수락 delegation 없음):**

```json
{
    "jsonrpc": "2.0",
    "id": "ready_1",
    "method": "ec.ready",
    "params": {
        "delegate": []
    }
}
```

**메시지 예시(delegation 수락):**

```json
{
    "jsonrpc": "2.0",
    "id": "ready_1",
    "method": "ec.ready",
    "params": {
        "delegate": ["payment.credential", "fulfillment.address_change"]
    }
}
```

`ec.ready`는 request이므로 host는 핸드셰이크 완료를 위해 응답해야 합니다(**MUST**).

- **방향:** host → Embedded Checkout
- **유형:** Response
- **결과 페이로드:**
  - `upgrade`(object, **OPTIONAL**): Embedded Checkout이 host와 통신할 채널을 어떻게 갱신할지 설명하는 객체
  - `checkout`(object, **OPTIONAL**): UCP checkout action으로 전달되지 않은 표시 전용 추가 상태. checkout UI 표시값 채우기에 사용되며, 조건부로 다음 필드에만 적용할 수 있습니다.
    - `payment.instruments`: host와 Embedded Checkout이 모두 `payment.instruments_change` delegation을 수락한 경우 덮어쓰기 가능

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "ready_1",
    "result": {}
}
```

host는 host-Embedded Checkout 통신 채널 갱신을 위해 `upgrade` 필드로 응답할 수 있습니다(**MAY**). 현재 이 객체는 `port` 필드만 지원하며, 이는 `MessagePort` 객체여야 하고(**MUST**), 임베디드 checkout 컨텍스트로 전달되어야 합니다(**MUST**). (예: host의 `iframe.contentWindow.postMessage()` 호출에서 `{transfer: [port2]}` 사용)

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "ready_1",
    "result": {
        "upgrade": {
            "port": "[Transferable MessagePort]"
        }
    }
}
```

host가 `upgrade` 객체로 응답하면 Embedded Checkout은 메시지 내 다른 정보는 무시하고, 업그레이드된 채널에서 새 `ec.ready`를 보내고 새 응답을 대기해야 합니다(**MUST**). 이후 모든 메시지는 업그레이드된 채널로만 전송되어야 합니다(**MUST**).

host는 `checkout` 객체로도 응답할 수 있으며(**MAY**), 해당 값은 host-business delegation 계약에 따라 checkout UI 표시값 채우기에 사용됩니다.

**메시지 예시: 표시 정보를 포함한 결제수단 제공**

```json
{
    "jsonrpc": "2.0",
    "id": "ready_1",
    "result": {
        "checkout": {
            "payment": {
                // The instrument structure is defined by the handler's instrument schema
                "instruments": [
                    {
                        "id": "payment_instrument_123",
                        "handler_id": "merchant_psp_handler_123",
                        "type": "card",
                        "selected": true,
                        "display": {
                            "brand": "visa",
                            "expiry_month": 12,
                            "expiry_year": 2026,
                            "last_digits": "1111",
                            "description": "Visa •••• 1111",
                            "card_art": "https://host.com/cards/visa-gold.png"
                        }
                    }
                ]
            }
        }
    }
}
```

### 라이프사이클 메시지

#### `ec.start`

checkout이 화면에 표시되어 상호작용 준비가 되었음을 알립니다.

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: UCP 응답의 `checkout` 객체와 동일 구조의 최신 checkout 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.start",
    "params": {
        "checkout": {
            "id": "checkout_123",
            "status": "incomplete",
            "messages": [
                {
                    "type": "error",
                    "code": "missing",
                    "path": "$.buyer.shipping_address",
                    "content": "Shipping address is required",
                    "severity": "recoverable"
                }
            ],
            "totals": [/* ... */],
            "line_items": [/* ... */],
            "buyer": {/* ... */},
            "payment": {/* ... */}
        }
    }
}
```

#### `ec.complete`

checkout이 성공적으로 완료되었음을 알립니다.

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: UCP 응답의 `checkout` 객체와 동일 구조의 최신 checkout 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.complete",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // ... other checkout fields
            "order": {
                "id": "ord_99887766",
                "permalink_url": "https://merchant.com/orders/ord_99887766"
            }
        }
    }
}
```

### 상태 변경 메시지

상태 변경 메시지는 checkout UI에서 **이미 반영된** 변경 사항을 embedder에 알립니다. 이 메시지는 정보 전달용이며, checkout은 변경 내용을 이미 적용하고 UI를 갱신한 상태입니다.

#### `ec.line_items.change`

checkout UI에서 line item이 변경되었음을 알립니다. (수량 변경, 항목 추가/삭제 등)

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.line_items.change",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the updated line items and totals
            "totals": [
                /* ... */
            ],
            "line_items": [
                /* ... */
            ]
            // ...
        }
    }
}
```

#### `ec.buyer.change`

checkout UI에서 buyer 정보가 갱신되었음을 알립니다.

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.buyer.change",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the updated buyer information
            "buyer": {
                /* ... */
            }
            // ...
        }
    }
}
```

#### `ec.messages.change`

checkout 메시지가 갱신되었음을 알립니다. 메시지에는 오류, 경고, 안내성 정보가 포함될 수 있습니다.

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.messages.change",
    "params": {
        "checkout": {
            "id": "checkout_123",
            "messages": [
                {
                    "type": "error",
                    "code": "invalid_address",
                    "path": "$.buyer.shipping_address",
                    "content": "We cannot ship to this address",
                    "severity": "recoverable"
                },
                {
                    "type": "info",
                    "code": "free_shipping",
                    "content": "Free shipping applied!"
                }
            ]
            // ...
        }
    }
}
```

#### `ec.payment.change`

결제 상태가 갱신되었음을 알립니다. 자세한 내용은 [`ec.payment.change`](#ecpaymentchange)를 참고하세요.

## 결제 확장

결제 확장은 host가 상태 변경 알림과 delegation 요청을 활용해 사용자 개입 흐름(escalation flow)을 오케스트레이션하는 방식을 정의합니다. checkout URL에 `ec_delegate=payment.instruments_change,payment.credential`가 포함되면, host가 결제수단 선택과 토큰 획득 제어권을 갖고 그 결과를 Embedded Checkout에 상태 업데이트로 전달합니다.

### 결제 개요 및 Host 선택

결제 delegation은 host와 Embedded Checkout 사이에 두 가지 오케스트레이션 패턴을 제공합니다.

**옵션 A: Host가 Embedded Checkout에 위임** host가 URL에 결제 delegation을 넣지 않습니다. Embedded Checkout이 자체 UI/흐름으로 결제수단 선택과 결제 처리를 수행합니다. 이는 표준 비위임 흐름입니다.

**옵션 B: Host가 제어권 획득** host가 checkout URL에 `ec_delegate=payment.instruments_change,payment.credential`를 포함해 결제 UI와 토큰 획득을 host로 위임하도록 Embedded Checkout에 알립니다. 위임된 경우:

- **Embedded Checkout 책임:**
  - 현재 결제수단과 변경 의도 UI(예: "결제수단 변경" 버튼) 표시
  - 결제 제출 전에 `ec.payment.credential_request` 응답 대기
- **Host 책임:**
  - `ec.payment.instruments_change_request` 수신 시 구매자용 네이티브 선택 UI를 띄우고 선택 결과로 응답
  - `ec.payment.credential_request` 수신 시 선택된 결제수단 토큰을 획득해 Embedded Checkout에 전달

### 결제 메시지 API 레퍼런스

#### `ec.payment.change`

checkout UI의 결제 섹션에서 변경이 발생했음을 host에 알립니다. (예: 새로운 결제수단 선택)

- **방향:** Embedded Checkout → host
- **유형:** Notification
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.payment.change",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the updated payment details
            "payment": {
                "instruments": [
                    {
                        "id": "payment_instrument_123",
                        "selected": true
                        /* ... */
                    }
                ]
            }
            // ...
        }
    }
}
```

#### `ec.payment.instruments_change_request`

host에 결제수단 선택 UI 제공을 요청합니다.

- **방향:** Embedded Checkout → host
- **유형:** Request
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_instruments_change_request_1",
    "method": "ec.payment.instruments_change_request",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the current payment details
            "payment": {
                /* ... */
            }
            // ...
        }
    }
}
```

host는 오류 또는 새로 선택된 결제수단으로 응답해야 합니다(**MUST**). 성공 응답에서는 `checkout` 객체의 `payment.instruments`만 포함한 부분 업데이트로 응답해야 합니다(**MUST**). Embedded Checkout은 이를 병합이 아닌 PUT 스타일 교체로 처리해야 합니다(**MUST**). 즉, 제공된 필드의 기존 상태를 완전히 대체해야 합니다.

- **방향:** host → Embedded Checkout
- **유형:** Response
- **페이로드:**
  - `checkout`: checkout 객체에 적용할 업데이트

**성공 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_instruments_change_request_1",
    "result": {
        "checkout": {
            "payment": {
                // The instrument structure is defined by the handler's instrument schema
                "instruments": [
                    {
                        "id": "payment_instrument_123",
                        "handler_id": "merchant_psp_handler_123",
                        "type": "card",
                        "selected": true,
                        "display": {
                            "brand": "visa",
                            "expiry_month": 12,
                            "expiry_year": 2026,
                            "last_digits": "1111",
                            "description": "Visa •••• 1111",
                            "card_art": "https://host.com/cards/visa-gold.png"
                        }
                        // No `credential` yet; it will be attached in the `ec.payment.credential_request` response
                    }
                ]
            }
        }
    }
}
```

**오류 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_instruments_change_request_1",
    "error": {
        "code": "abort_error",
        "message": "User closed the payment sheet without authorizing."
    }
}
```

#### `ec.payment.credential_request`

checkout 제출 시 선택된 결제수단에 대한 자격증명(credential)을 요청합니다.

- **방향:** Embedded Checkout → Host
- **유형:** Request
- **페이로드:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_credential_request_1",
    "method": "ec.payment.credential_request",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the current payment details
            "payment": {
                "instruments": [
                    {
                        "id": "payment_instrument_123",
                        "selected": true
                        /* ... */
                    }
                ]
            }
            // ...
        }
    }
}
```

host는 오류 또는 선택된 결제수단의 credential로 응답해야 합니다(**MUST**). 성공 응답에서는 `selected: true`인 instrument에 새 `credentials` 필드를 반영한 `checkout` 부분 업데이트를 제공해야 합니다(**MUST**). Embedded Checkout은 이를 병합이 아닌 PUT 스타일 교체로 처리해 `payment.instruments` 기존 상태를 완전히 대체해야 합니다(**MUST**).

- **방향:** host → Embedded Checkout
- **유형:** Response
- **페이로드:**
  - `checkout`: checkout 객체에 적용할 업데이트

**성공 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_credential_request_1",
    "result": {
        "checkout": {
            "payment": {
                "instruments": [
                    {
                        "id": "payment_instrument_123",
                        "handler_id": "merchant_psp_handler_123",
                        "type": "card",
                        "selected": true,
                        "display": {
                            "brand": "visa",
                            "expiry_month": 12,
                            "expiry_year": 2026,
                            "last_digits": "1111",
                            "description": "Visa •••• 1111",
                            "card_art": "https://host.com/cards/visa-gold.png"
                        },
                        // The credential structure is defined by the handler's instrument schema
                        "credential": {
                            "type": "token",
                            "token": "tok_123"
                        }
                    }
                ]
            }
        }
    }
}
```

**오류 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "payment_credential_request_1",
    "error": {
        "code": "abort_error",
        "message": "User closed the payment sheet without authorizing."
    }
}
```

**결제 토큰 delegation 중 host 책임:**

1. **확인:** Host는 신뢰 결제 UI(Payment Sheet/생체인증 프롬프트)를 표시해야 합니다. 메시지 수신만으로 토큰을 묵시적으로 발급해서는 안 됩니다(**MUST NOT**).
1. **인증:** Host는 Payment Handler를 통해 사용자 인증을 수행합니다.
1. **AP2 통합(선택):** `ucp.ap2_mandate`가 활성화된 경우 (**[AP2 extension](https://ap2-extension.org/)** 참고), host는 신뢰 UI에서 `payment_mandate`를 생성합니다.

## 주문 이행(Fulfillment) 확장

fulfillment 확장은 host가 주소 선택을 위임받아 네이티브 주소 선택기 경험을 제공하는 방식을 정의합니다. checkout URL에 `ec_delegate=fulfillment.address_change`가 포함되면, host는 배송지 선택 제어권을 갖고 결과 주소 업데이트를 Embedded Checkout에 반환합니다.

### 주문 이행 개요 및 호스트 선택

fulfillment delegation에는 두 가지 패턴이 있습니다.

**옵션 A: Host가 Embedded Checkout에 위임** host가 URL에 fulfillment delegation을 넣지 않습니다. Embedded Checkout이 자체 주소 UI/폼으로 주소 입력을 처리합니다. 이는 표준 비위임 흐름입니다.

**옵션 B: Host가 제어권 획득** host가 checkout URL에 `ec_delegate=fulfillment.address_change`를 포함해 주소 선택 UI를 host에 위임하도록 Embedded Checkout에 알립니다. 위임된 경우:

**Embedded Checkout 책임:**

- 현재 배송지와 변경 의도 UI(예: "주소 변경" 버튼) 표시
- 구매자가 주소 변경을 트리거하면 `ec.fulfillment.address_change_request` 전송
- host가 반환한 주소를 바탕으로 배송 옵션 갱신

**Host 책임:**

- `ec.fulfillment.address_change_request`에 대해 구매자 주소 선택/입력을 위한 네이티브 UI 제공 후 응답
- 선택된 주소를 UCP PostalAddress 형식으로 응답

### 주문 이행 메시지 API 레퍼런스

#### `ec.fulfillment.change`

checkout UI에서 fulfillment 상세가 변경되었음을 host에 알립니다.

- **방향:** Embedded Checkout → Host
- **유형:** Notification
- **Payload:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "method": "ec.fulfillment.change",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the updated fulfillment details
            "fulfillment": {
                /* ... */
            }
            // ...
        }
    }
}
```

#### `ec.fulfillment.address_change_request`

배송 fulfillment 방식에 대한 주소 선택 UI를 host에 요청합니다.

- **방향:** Embedded Checkout → Host
- **유형:** Request
- **Payload:**
  - `checkout`: checkout 최신 상태

**메시지 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "fulfillment_address_change_request_1",
    "method": "ec.fulfillment.address_change_request",
    "params": {
        "checkout": {
            "id": "checkout_123",
            // The entire checkout object is provided, including the current fulfillment details
            "fulfillment": {
                "methods": [
                    {
                        "id": "method_1",
                        "type": "shipping",
                        "selected_destination_id": "address_123",
                        "destinations": [
                            {
                                "id": "address_123",
                                "address_street": "456 Old Street"
                                // ...
                            }
                        ]
                        // ...
                    }
                ]
            }
            // ...
        }
    }
}
```

host는 오류 또는 새로 선택된 주소로 응답해야 합니다(**MUST**). 성공 응답에서는 `fulfillment.methods`를 갱신해 `selected_destination_id`와 `destinations`를 업데이트하고, 그 외 상태는 유지해야 합니다(**MUST**). Embedded Checkout은 이를 병합이 아닌 PUT 스타일 교체로 처리해 `fulfillment.methods` 기존 상태를 완전히 대체해야 합니다(**MUST**).

- **방향:** host → Embedded Checkout
- **유형:** Response
- **Payload:**
  - `checkout`: checkout 객체에 적용할 업데이트

**성공 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "fulfillment_address_change_request_1",
    "result": {
        "checkout": {
            "fulfillment": {
                "methods": [
                    {
                        "id": "method_1",
                        "type": "shipping",
                        "selected_destination_id": "address_789",
                        "destinations": [
                            {
                                "id": "address_789",
                                "first_name": "John",
                                "last_name": "Doe",
                                "street_address": "123 New Street"
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

**오류 응답 예시:**

```json
{
    "jsonrpc": "2.0",
    "id": "fulfillment_address_change_request_1",
    "error": {
        "code": "abort_error",
        "message": "User cancelled address selection."
    }
}
```

### 주소 포맷

주소 객체는 UCP [PostalAddress](/ucp-docs-ko/specification/checkout/#postal-address) 형식을 사용합니다.

| Name             | Type   | Required | Description                                                                                                                                                                                                                               |
| ---------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| extended_address | string | No       | An address extension such as an apartment number, C/O or alternative name.                                                                                                                                                                |
| street_address   | string | No       | The street address.                                                                                                                                                                                                                       |
| address_locality | string | No       | The locality in which the street address is, and which is in the region. For example, Mountain View.                                                                                                                                      |
| address_region   | string | No       | The region in which the locality is, and which is in the country. Required for applicable countries (i.e. state in US, province in CA). For example, California or another appropriate first-level Administrative division.               |
| address_country  | string | No       | The country. Recommended to be in 2-letter ISO 3166-1 alpha-2 format, for example "US". For backward compatibility, a 3-letter ISO 3166-1 alpha-3 country code such as "SGP" or a full country name such as "Singapore" can also be used. |
| postal_code      | string | No       | The postal code. For example, 94043.                                                                                                                                                                                                      |
| first_name       | string | No       | Optional. First name of the contact associated with the address.                                                                                                                                                                          |
| last_name        | string | No       | Optional. Last name of the contact associated with the address.                                                                                                                                                                           |
| phone_number     | string | No       | Optional. Phone number of the contact associated with the address.                                                                                                                                                                        |

## 보안 및 오류 처리

### 오류 코드

embedded checkout의 delegation 요청에 대한 응답은 오류로 귀결될 수 있습니다. 응답자는 가능하면 **[W3C DOMException](https://webidl.spec.whatwg.org/#idl-DOMException)** 이름에 매핑된 오류 코드를 사용하는 것이 권장됩니다(**SHOULD**).

| 코드                  | 설명                                                                                                              |
| --------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `abort_error`         | 사용자가 상호작용을 취소함(예: 시트 닫기)                                                                         |
| `security_error`      | host origin 검증 실패                                                                                             |
| `not_supported_error` | 요청된 결제수단을 host가 지원하지 않음                                                                            |
| `invalid_state_error` | 핸드셰이크 순서가 올바르지 않음                                                                                   |
| `not_allowed_error`   | 요청에 유효한 User Activation이 없음([비의도적 결제 요청 방지](#prevention-of-unsolicited-payment-requests) 참고) |

### 웹 기반 호스트 보안

#### 콘텐츠 보안 정책(CSP)

보안을 위해 양측은 적절한 **[Content Security Policy(CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)** 지시어를 구현해야 합니다(**MUST**).

- **Business:** 신뢰 host에서만 임베딩되도록 `frame-ancestors <host_origin>;`를 설정해야 합니다(**MUST**).

- **Host:**

  - **직접 임베딩:** host가 business 페이지를 직접 임베딩하면, 잠재 business origin이 많을 때 `frame-src`를 모두 열거하기가 비현실적일 수 있습니다. 이 경우 엄격한 `frame-src`가 이상적이지만, [Iframe Sandbox Attributes](#iframe-sandbox-attributes), [Credentialless Iframes](#credentialless-iframes) 같은 보조 보안 수단이 중요합니다.
  - **중간 Iframe:** host는 business 페이지 임베딩을 위해 중간 iframe(예: host 제어 서브도메인)을 사용할 수 있습니다(**MAY**). 이 방식은 제어성을 높입니다.
    - host 메인 페이지는 `frame-src`에서 중간 iframe origin만 허용하면 됩니다. (예: `frame-src <intermediate_iframe_origin>;`)
    - 중간 iframe은 현재 세션의 특정 `<merchant_origin>`만 허용하도록 엄격한 `frame-src` 정책을 구현해야 합니다(**MUST**). (예: `frame-src <merchant_origin>;`) 이는 중간 iframe 콘텐츠 제공 시 HTTP 헤더로 설정할 수 있습니다.

#### 아이프레임 sandbox 속성

모든 business iframe은 권한 제한을 위해 sandbox 처리되어야 합니다(**MUST**). 다음 sandbox 속성 적용이 권장되며(**SHOULD**), host와 business는 추가 권한을 협상할 수 있습니다(**MAY**).

```html
<iframe sandbox="allow-scripts allow-forms allow-same-origin"></iframe>
```

#### 크리덴셜리스(credentialless) 아이프레임

host는 iframe에 `credentialless` 속성을 사용해 새 임시 컨텍스트로 로드하는 것이 권장됩니다(**SHOULD**). 이를 통해 business가 컨텍스트 간 사용자 활동을 연계하거나 기존 세션에 접근하는 것을 방지해 사용자 프라이버시를 보호할 수 있습니다.

```html
<iframe credentialless src="https://business.example.com/checkout"></iframe>
```

#### 엄격한 origin 검증

프레임 간 모든 `postMessage` 통신에 대해 `origin`을 엄격히 검증해야 합니다.

### 비의도적 결제 요청 방지

**취약점:** 악의적이거나 침해된 business가 사용자 상호작용 없이 `ec.payment.credential_request`를 프로그램적으로 트리거할 수 있습니다.

**대응(Host 제어 실행):** 이 위험을 제거하기 위해 host를 결제 실행의 유일 신뢰 시작자로 지정합니다. host는 토큰 발급 전에 사용자 확인 UI를 표시하는 것이 권장됩니다(**SHOULD**). 트리거가 Embedded Checkout에서 시작된 경우 무음 토큰화는 엄격히 금지됩니다.

## 스키마 정의

아래 스키마는 Embedded Checkout 프로토콜과 확장에서 사용하는 데이터 구조를 정의합니다.

### 체크아웃(Checkout)

line item, totals, buyer 정보를 포함한 거래의 현재 상태를 나타내는 핵심 객체입니다.

| Name         | Type                                                                                              | Required | Description                                                                                                                                                                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ucp          | [UCP Response Checkout Schema](/ucp-docs-ko/specification/checkout/#ucp-response-checkout-schema) | **Yes**  | Protocol metadata for discovery profiles and responses. Uses slim schema pattern with context-specific required fields.                                                                                                                                         |
| id           | string                                                                                            | **Yes**  | Unique identifier of the checkout session.                                                                                                                                                                                                                      |
| line_items   | Array\[[Line Item Response](/ucp-docs-ko/specification/checkout/#line-item-response)\]            | **Yes**  | List of line items being checked out.                                                                                                                                                                                                                           |
| buyer        | [Buyer](/ucp-docs-ko/specification/checkout/#buyer)                                               | No       | Representation of the buyer.                                                                                                                                                                                                                                    |
| status       | string                                                                                            | **Yes**  | Checkout state indicating the current phase and required action. See Checkout Status lifecycle documentation for state transition details. **Enum:** `incomplete`, `requires_escalation`, `ready_for_complete`, `complete_in_progress`, `completed`, `canceled` |
| currency     | string                                                                                            | **Yes**  | ISO 4217 currency code reflecting the merchant's market determination. Derived from address, context, and geo IP—buyers provide signals, merchants determine currency.                                                                                          |
| totals       | Array\[[Total Response](/ucp-docs-ko/specification/checkout/#total-response)\]                    | **Yes**  | Different cart totals.                                                                                                                                                                                                                                          |
| messages     | Array\[[Message](/ucp-docs-ko/specification/checkout/#message)\]                                  | No       | List of messages with error and info about the checkout session state.                                                                                                                                                                                          |
| links        | Array\[[Link](/ucp-docs-ko/specification/checkout/#link)\]                                        | **Yes**  | Links to be displayed by the platform (Privacy Policy, TOS). Mandatory for legal compliance.                                                                                                                                                                    |
| expires_at   | string                                                                                            | No       | RFC 3339 expiry timestamp. Default TTL is 6 hours from creation if not sent.                                                                                                                                                                                    |
| continue_url | string                                                                                            | No       | URL for checkout handoff and session recovery. MUST be provided when status is requires_escalation. See specification for format and availability requirements.                                                                                                 |
| payment      | [Payment](/ucp-docs-ko/specification/checkout/#payment)                                           | No       | Payment configuration containing handlers.                                                                                                                                                                                                                      |
| order        | [Order Confirmation](/ucp-docs-ko/specification/checkout/#order-confirmation)                     | No       | Details about an order created for this checkout session.                                                                                                                                                                                                       |

### 주문(Order)

checkout이 성공적으로 완료되었을 때 반환되는 확인 정보 객체입니다.

| Name          | Type                                                                                     | Required | Description                                                                                                                                  |
| ------------- | ---------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ucp           | [UCP Response Order Schema](/ucp-docs-ko/specification/order/#ucp-response-order-schema) | **Yes**  | Protocol metadata for discovery profiles and responses. Uses slim schema pattern with context-specific required fields.                      |
| id            | string                                                                                   | **Yes**  | Unique order identifier.                                                                                                                     |
| checkout_id   | string                                                                                   | **Yes**  | Associated checkout ID for reconciliation.                                                                                                   |
| permalink_url | string                                                                                   | **Yes**  | Permalink to access the order on merchant site.                                                                                              |
| line_items    | Array\[[Order Line Item](/ucp-docs-ko/specification/order/#order-line-item)\]            | **Yes**  | Immutable line items — source of truth for what was ordered.                                                                                 |
| fulfillment   | object                                                                                   | **Yes**  | Fulfillment data: buyer expectations and what actually happened.                                                                             |
| adjustments   | Array\[[Adjustment](/ucp-docs-ko/specification/order/#adjustment)\]                      | No       | Append-only event log of money movements (refunds, returns, credits, disputes, cancellations, etc.) that exist independently of fulfillment. |
| totals        | Array\[[Total Response](/ucp-docs-ko/specification/order/#total-response)\]              | **Yes**  | Different totals for the order.                                                                                                              |

### 결제(Payment)

| Name        | Type                                                                                                              | Required | Description                                                                                                                                                                                                                |
| ----------- | ----------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| instruments | Array\[[Selected Payment Instrument](/ucp-docs-ko/specification/embedded-checkout/#selected-payment-instrument)\] | No       | The payment instruments available for this payment. Each instrument is associated with a specific handler via the handler_id field. Handlers can extend the base payment_instrument schema to add handler-specific fields. |

### 결제 수단(Payment Instrument)

구매자가 사용할 수 있는 특정 결제 수단(예: 특정 카드, 계좌, 지갑 credential)을 나타냅니다.

| Name            | Type                                                                                   | Required | Description                                                                                                                                                  |
| --------------- | -------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| id              | string                                                                                 | **Yes**  | A unique identifier for this instrument instance, assigned by the platform.                                                                                  |
| handler_id      | string                                                                                 | **Yes**  | The unique identifier for the handler instance that produced this instrument. This corresponds to the 'id' field in the Payment Handler definition.          |
| type            | string                                                                                 | **Yes**  | The broad category of the instrument (e.g., 'card', 'tokenized_card'). Specific schemas will constrain this to a constant value.                             |
| billing_address | [Postal Address](/ucp-docs-ko/specification/embedded-checkout/#postal-address)         | No       | The billing address associated with this payment method.                                                                                                     |
| credential      | [Payment Credential](/ucp-docs-ko/specification/embedded-checkout/#payment-credential) | No       | The base definition for any payment credential. Handlers define specific credential types.                                                                   |
| display         | object                                                                                 | No       | Display information for this payment instrument. Each payment instrument schema defines its specific display properties, as outlined by the payment handler. |

### 결제 핸들러 응답

특정 결제 수단을 인증/처리하는 processor 또는 wallet provider(예: Google Pay, Stripe, 은행 앱)의 응답 구조를 나타냅니다.

*No properties defined.*
