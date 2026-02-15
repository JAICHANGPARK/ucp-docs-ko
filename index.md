# Universal Commerce Protocol

플랫폼, 에이전트, 비즈니스를 위한 공통 언어.

UCP는 탐색과 구매부터 구매 이후 경험까지 에이전트 커머스를 위한 구성 요소를 정의하여, 생태계가 개별 맞춤 통합 없이 하나의 표준으로 상호운용되도록 합니다.

### 학습하기

프로토콜 개요, 핵심 개념, 설계 원칙

[문서 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/overview/index.md)

### 구현하기

GitHub 저장소, 기술 명세, SDK, 레퍼런스 구현

[GitHub에서 보기](https://github.com/Universal-Commerce-Protocol/ucp)

## 업계 리더들과 공동 개발 및 채택

UCP는 업계가 업계를 위해 만들었습니다. 장바구니 이탈과 사용자 불편을 유발하는 파편화된 커머스 여정을 해결하고, 에이전트 커머스를 가능하게 하기 위함입니다.

Google

Shopify

Etsy

Wayfair

Target

Walmart

## 유연성, 보안, 확장성을 위한 설계

에이전트 커머스는 상호운용성을 요구합니다. UCP는 업계 표준인 REST 및 JSON-RPC 전송을 기반으로 구축되었고, [Agent Payments Protocol (AP2)](https://ap2-protocol.org/), [Agent2Agent (A2A)](https://a2a-protocol.org/latest/), 및 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs/getting-started/intro) 을 기본 지원하므로 서로 다른 시스템이 별도 커스텀 통합 없이 함께 동작할 수 있습니다.

### 확장 가능하고 범용적

어떤 커머스 주체(소상공인부터 엔터프라이즈까지)와 모든 상호작용 방식(채팅, 비주얼 커머스, 음성 등)을 지원하도록 확장 가능한 서피스 독립 설계입니다.

### 비즈니스 중심 설계

커머스를 원활하게 지원하도록 설계되어, 리테일러가 비즈니스 규칙 통제권을 유지하고 고객 관계의 완전한 소유권을 가진 Merchant of Record로 남을 수 있습니다.

### 개방형 및 확장형

설계 단계부터 개방성과 확장성을 갖추어, 다양한 산업 영역에서 커뮤니티 주도의 capability 및 extension 개발을 가능하게 합니다.

### 안전하고 프라이버시 중심

계정 연동(OAuth 2.0)과 안전한 결제(AP2)를 위한 검증된 보안 표준(결제 mandate 및 검증 가능한 자격증명 기반) 위에 구축되었습니다.

### 마찰 없는 결제

제공자 간 상호운용이 가능한 개방형 지갑 생태계를 통해 사용자가 선호하는 결제 수단으로 결제할 수 있게 합니다.

## 동작 예시 보기

UCP는 초기 상품 탐색과 검색부터 최종 판매 및 구매 후 지원까지, 커머스 전체 라이프사이클을 지원하도록 설계되었습니다. 프로토콜의 초기 릴리스는 Checkout, Identity Linking, Order Management의 세 가지 핵심 capability에 집중합니다.

Checkout Identity Linking Order

동작 예시

### Checkout

통합 checkout 세션을 통해 수백만 비즈니스에 걸쳐 복잡한 cart 로직, 동적 가격, 세금 계산 등을 지원합니다.

[자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/checkout-rest/index.md)

```json
{
  "ucp": { ... },
  "id": "chk_123456789",
  "status": "ready_for_complete",
  "currency": "USD",
  "buyer": {
    "email": "e.beckett@example.com",
    "first_name": "Elisa",
    "last_name": "Beckett"
  },
  "line_items": [
    {
      "id": "li_1",
      "item": {
        "id": "item_123",
        "title": "Monos Carry-On Pro suitcase",
        "price": 26550
      },
      "quantity": 1,
      ...
    }
  ],
  "totals": [ ... ],
  "links": [ ... ],
  "payment": { ... },
  "fulfillment": {
    "methods": [
      {
        "id": "method_1",
        "type": "shipping",
        "line_item_ids": ["li_1"],
        "selected_destination_id": "dest_1",
        "destinations": [
          {
            "id": "dest_1",
            "first_name": "Elisa",
            "last_name": "Beckett",
            "street_address": "1600 Amphitheatre Pkwy",
            "address_locality": "Mountain View",
            "address_region": "CA",
            "postal_code": "94043",
            "address_country": "US"
          }
        ],
        "groups": [
          {
            "id": "group_1",
            "line_item_ids": ["li_1"],
            "selected_option_id": "free-shipping",
            "options": [
              {
                "id": "free-shipping",
                "title": "Free Shipping",
                "totals": [ {"type": "total", "amount": 0} ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

동작 예시

### Identity Linking

OAuth 2.0 표준을 통해 에이전트는 자격증명을 공유하지 않고도 안전하고 권한이 부여된 관계를 유지할 수 있습니다.

[자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/identity-linking/index.md)

```json
Sample of /.well-known/oauth-authorization-server

{
  "issuer": "https://example.com",
  "authorization_endpoint": "https://example.com/oauth2/authorize",
  "token_endpoint": "https://example.com/oauth2/token",
  "revocation_endpoint": "https://example.com/oauth2/revoke",
  "scopes_supported": [
    "ucp:scopes:checkout_session",
  ],
  "response_types_supported": [
    "code"
  ],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token"
  ],
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic"
  ],
  "service_documentation": "https://example.com/docs/oauth2"
}
```

동작 예시

### Order

구매 확정부터 배송까지. 실시간 webhook으로 상태 업데이트, 배송 추적, 반품 처리를 모든 채널에서 지원합니다.

[자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/order/index.md)

```json
{
  "ucp": { ... },
  "id": "order_123456789",
  "checkout_id": "chk_123456789",
  "permalink_url": ...,
  "line_items": [ ... ],
  "fulfillment": {
    "expectations": [
      {
        "id": "exp_1",
        "line_items": [{ "id": "li_1", "quantity": 1 }],
        "method_type": "shipping",
        "destination": {
          "first_name": "Elisa",
          "last_name": "Beckett",
          "street_address": "1600 Amphitheatre Pkwy",
          "address_locality": "Mountain View",
          "address_region": "CA",
          "postal_code": "94043",
          "address_country": "US"
        },
        "description": "Arrives in 2-3 business days",
        "fulfillable_on": "now"
      }
      ...
    ],
    "events": [
      {
        "id": "evt_1",
        "occurred_at": "2026-01-11T10:30:00Z",
        "type": "delivered",
        "line_items": [{ "id": "li_1", "quantity": 1 }],
        "tracking_number": "123456789",
        "tracking_url": "https://fedex.com/track/123456789",
        "description": "Delivered to front door"
      }
    ]
  },
  "adjustments": [
    {
      "id": "adj_1",
      "type": "refund",
      "occurred_at": "2026-01-12T14:30:00Z",
      "status": "completed",
      "line_items": [{ "id": "li_1", "quantity": 1 }],
      "amount": 26550,
      "description": "Defective item"
    }
  ],
  "totals": [ ... ]
}
```

### 네이티브 checkout 구현

판매자의 checkout API와 직접 연동 및 협상하여, 플랫폼에 맞는 네이티브 UI와 워크플로를 구현할 수 있습니다.

[작동 방식 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/checkout-rest/index.md)

### 비즈니스 checkout 임베드

비즈니스 checkout UI를 임베드/렌더링하여, 양방향 통신, 결제 및 배송 주소 위임 같은 고급 capability가 필요한 복잡한 checkout 흐름을 지원합니다.

[자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/embedded-checkout/index.md)

## 커머스 생태계 전체를 위한 설계

### 개발자용

개방형 기반 위에서 커머스의 미래를 구축하세요. 차세대 디지털 커머스를 위한 오픈소스 표준을 함께 발전시키는 커뮤니티에 참여하세요.

[기술 명세 보기](https://jaichangpark.github.io/ucp-docs-ko/specification/overview/index.md)

### 비즈니스용

UCP는 리테일러가 AI 어시스턴트, 쇼핑 에이전트, 임베디드 경험 등 어디서든 고객을 만날 수 있게 하며, 채널마다 checkout을 다시 만들 필요가 없습니다. Merchant of Record 지위와 비즈니스 로직을 그대로 유지할 수 있습니다.

[UCP 연동하기](https://developers.google.com/merchant/ucp/)

### AI 플랫폼용

표준화된 API로 비즈니스 온보딩을 단순화하고, 사용자에게 통합 쇼핑 경험을 제공합니다. MCP, A2A, 기존 에이전트 프레임워크와 호환됩니다.

[UCP 핵심 개념 자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/documentation/core-concepts/index.md)

### 결제 제공자용

검증 가능한 유니버설 결제: 모든 승인은 사용자 동의의 암호학적 증명으로 뒷받침됩니다. 개방형 모듈식 payment handler 설계로 상호운용성과 결제수단 선택권을 보장합니다.

[UCP와 AP2 자세히 보기](https://jaichangpark.github.io/ucp-docs-ko/documentation/ucp-and-ap2/index.md)

## 생태계 전반의 지지

Adyen

Affirm

Amex

Ant International

Best Buy

Block

Carrefour

Chewy

Commerce

Fiserv

Flipkart

Gap

Klarna

Kroger

Lowe's

Macy's

Mastercard

Paypal

Salesforce

Sephora

Shopee

Splitit

Stripe

The Home Depot

Ulta

Visa

Worldpay

Zalando

iv class="partner-logo"> GitHub 저장소 방문
