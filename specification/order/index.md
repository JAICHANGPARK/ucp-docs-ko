# 주문 기능

- **기능 이름:** `dev.ucp.shopping.order`

## 개요

주문은 체크아웃 제출이 성공적으로 완료된 뒤 확정된 거래를 나타냅니다. 무엇을 구매했는지, 어떻게 전달될 예정인지, 주문 생성 이후 어떤 일이 있었는지를 하나의 완전한 기록으로 제공합니다.

### 핵심 개념

주문은 크게 3가지 구성요소를 가집니다.

**라인 아이템(Line Items)** - 체크아웃에서 무엇을 구매했는지:

- 현재 수량 카운트(총 수량, 이행 수량)를 포함

**이행(Fulfillment)** - 아이템이 어떻게 전달되는지:

- **기대치(Expectations)** - 구매자에게 보여지는 "언제/어떻게 도착하는지"에 대한 *약속*
- **이벤트(append-only log)** - 실제로 어떤 일이 발생했는지 (예: 👕 배송됨)

**조정(Adjustments, append-only log)** - 이행과 독립적인 주문 이후 이벤트:

- 보통 금액 이동(환불, 반품, 크레딧, 분쟁, 취소)
- 주문 이후 발생하는 어떤 변경도 가능
- 이행 이전/중간/이후 어느 시점에도 발생 가능

## 데이터 모델

### 라인 아이템

라인 아이템은 체크아웃에서 구매한 항목과 현재 상태를 나타냅니다.

- 아이템 상세(상품, 가격, 주문 수량)
- 수량 카운트와 상태는 파생(derived)됨

### 이행(Fulfillment)

이행은 아이템이 구매자에게 전달되는 방식을 추적합니다.

#### 기대치(Expectations)

**기대치**는 구매자 관점의 아이템 묶음(예: "패키지 📦")으로, 다음을 나타냅니다.

- 어떤 아이템이 함께 묶였는지
- 어디로 가는지(`destination`)
- 어떤 방식으로 전달되는지(`method_type`)
- 언제 도착하는지(`description`, `fulfillable_on`)

기대치는 주문 이후 분할/병합/조정될 수 있습니다. 예를 들면:

- 배송일 기준으로 묶기: "무엇이 언제 오는지"
- 유연성을 위해 넓은 날짜 범위의 단일 기대치 사용
- 목표는 **구매자 기대치 설정**이며, 이는 좋은 구매 경험을 위한 핵심입니다.

#### 이행 이벤트(Fulfillment Events)

**이행 이벤트**는 실제 배송 상태를 추적하는 append-only 로그입니다.

- 라인 아이템 ID와 수량을 참조
- 트래킹 정보를 포함
- `type`은 개방형 문자열 필드로, 비즈니스가 필요에 맞게 정의 가능 (일반 예시: `processing`, `shipped`, `in_transit`, `delivered`, `failed_attempt`, `canceled`, `undeliverable`, `returned_to_sender`)

### 조정(Adjustments)

**조정**은 이행과 독립적으로 존재하는 append-only 이벤트 로그입니다.

- `type`은 개방형 문자열 필드로, 비즈니스가 필요에 맞게 정의 가능 (보통 `refund`, `return`, `credit`, `price_adjustment`, `dispute`, `cancellation` 같은 금액 이동)
- 주문 이후 변경이면 어떤 것이든 포함 가능
- 필요 시 라인 아이템에 연결 가능(또는 배송비 환불 같은 주문 단위 이벤트)
- 관련 시 금액(`amount`) 포함
- 이행 상태와 무관하게 어느 시점에나 발생 가능

## 스키마

### 주문(Order)

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

### 주문 라인 아이템(Order Line Item)

라인 아이템은 체크아웃에서 구매한 내용과 현재 상태를 반영합니다. 상태 및 수량 카운트는 이벤트 로그를 기준으로 계산되어야 합니다.

| Name      | Type                                                      | Required | Description                                                                                                                                                                |
| --------- | --------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id        | string                                                    | **Yes**  | Line item identifier.                                                                                                                                                      |
| item      | [Item](/ucp-docs-ko/specification/order/#item)            | **Yes**  | Product data (id, title, price, image_url).                                                                                                                                |
| quantity  | object                                                    | **Yes**  | Quantity tracking. Both total and fulfilled are derived from events.                                                                                                       |
| totals    | Array\[[Total](/ucp-docs-ko/specification/order/#total)\] | **Yes**  | Line item totals breakdown.                                                                                                                                                |
| status    | string                                                    | **Yes**  | Derived status: fulfilled if quantity.fulfilled == quantity.total, partial if quantity.fulfilled > 0, otherwise processing. **Enum:** `processing`, `partial`, `fulfilled` |
| parent_id | string                                                    | No       | Parent line item identifier for any nested structures.                                                                                                                     |

**수량 구조:**

```json
{
  "total": 3,      // Current total quantity
  "fulfilled": 2   // What has been fulfilled
}
```

**상태 파생 규칙:**

```text
if (fulfilled == total) → "fulfilled"
else if (fulfilled > 0) → "partial"
else → "processing"
```

### 기대치(Expectation)

기대치는 아이템이 언제/어떻게 전달되는지에 대한 구매자 관점의 묶음입니다. 이는 구매자에게 제공하는 현재 약속을 나타내며, 주문 이후 분할/병합/조정될 수 있습니다.

| Name           | Type                                                               | Required | Description                                                                                                 |
| -------------- | ------------------------------------------------------------------ | -------- | ----------------------------------------------------------------------------------------------------------- |
| id             | string                                                             | **Yes**  | Expectation identifier.                                                                                     |
| line_items     | Array[object]                                                      | **Yes**  | Which line items and quantities are in this expectation.                                                    |
| method_type    | string                                                             | **Yes**  | Delivery method type (shipping, pickup, digital). **Enum:** `shipping`, `pickup`, `digital`                 |
| destination    | [Postal Address](/ucp-docs-ko/specification/order/#postal-address) | **Yes**  | Delivery destination address.                                                                               |
| description    | string                                                             | No       | Human-readable delivery description (e.g., 'Arrives in 5-8 business days').                                 |
| fulfillable_on | string                                                             | No       | When this expectation can be fulfilled: 'now' or ISO 8601 timestamp for future date (backorder, pre-order). |

### 이행 이벤트(Fulfillment Event)

이벤트는 실제 배송 과정을 기록하는 append-only 레코드입니다. `type` 필드는 개방형 문자열로, 비즈니스가 이행 프로세스에 맞춰 값을 정의할 수 있습니다.

| Name            | Type          | Required | Description                                                                                                                                                                                                                                                                                                                             |
| --------------- | ------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id              | string        | **Yes**  | Fulfillment event identifier.                                                                                                                                                                                                                                                                                                           |
| occurred_at     | string        | **Yes**  | RFC 3339 timestamp when this fulfillment event occurred.                                                                                                                                                                                                                                                                                |
| type            | string        | **Yes**  | Fulfillment event type. Common values include: processing (preparing to ship), shipped (handed to carrier), in_transit (in delivery network), delivered (received by buyer), failed_attempt (delivery attempt failed), canceled (fulfillment canceled), undeliverable (cannot be delivered), returned_to_sender (returned to merchant). |
| line_items      | Array[object] | **Yes**  | Which line items and quantities are fulfilled in this event.                                                                                                                                                                                                                                                                            |
| tracking_number | string        | No       | Carrier tracking number (required if type != processing).                                                                                                                                                                                                                                                                               |
| tracking_url    | string        | No       | URL to track this shipment (required if type != processing).                                                                                                                                                                                                                                                                            |
| carrier         | string        | No       | Carrier name (e.g., 'FedEx', 'USPS').                                                                                                                                                                                                                                                                                                   |
| description     | string        | No       | Human-readable description of the shipment status or delivery information (e.g., 'Delivered to front door', 'Out for delivery').                                                                                                                                                                                                        |

예시: `processing`, `shipped`, `in_transit`, `delivered`, `failed_attempt`, `canceled`, `undeliverable`, `returned_to_sender` 등.

### 조정(Adjustment)

조정은 이행과 독립적으로 존재하는 다형성(polymorphic) 이벤트입니다. `type` 필드는 개방형 문자열로, 비즈니스 요구에 맞게 정의할 수 있습니다.

| Name        | Type          | Required | Description                                                                                                                                                                                     |
| ----------- | ------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id          | string        | **Yes**  | Adjustment event identifier.                                                                                                                                                                    |
| type        | string        | **Yes**  | Type of adjustment (open string). Typically money-related like: refund, return, credit, price_adjustment, dispute, cancellation. Can be any value that makes sense for the merchant's business. |
| occurred_at | string        | **Yes**  | RFC 3339 timestamp when this adjustment occurred.                                                                                                                                               |
| status      | string        | **Yes**  | Adjustment status. **Enum:** `pending`, `completed`, `failed`                                                                                                                                   |
| line_items  | Array[object] | No       | Which line items and quantities are affected (optional).                                                                                                                                        |
| amount      | integer       | No       | Amount in minor units (cents) for refunds, credits, price adjustments (optional).                                                                                                               |
| description | string        | No       | Human-readable reason or description (e.g., 'Defective item', 'Customer requested').                                                                                                            |

예시: `refund`, `return`, `credit`, `price_adjustment`, `dispute`, `cancellation` 등.

## 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": {
      "dev.ucp.shopping.order": [{"version": "2026-01-11"}]
    }
  },
  "id": "order_abc123",
  "checkout_id": "checkout_xyz789",
  "permalink_url": "https://business.com/orders/abc123",
  "line_items": [
    {
      "id": "li_shoes",
      "item": { "id": "prod_shoes", "title": "Running Shoes", "price": 3000 },
      "quantity": { "total": 3, "fulfilled": 3 },
      "totals": [
        {"type": "subtotal", "amount": 9000},
        {"type": "total", "amount": 9000}
      ],
      "status": "fulfilled"
    },
    {
      "id": "li_shirts",
      "item": { "id": "prod_shirts", "title": "Cotton T-Shirt", "price": 2000 },
      "quantity": { "total": 2, "fulfilled": 0 },
      "totals": [
        {"type": "subtotal", "amount": 4000},
        {"type": "total", "amount": 4000}
      ],
      "status": "processing"
    }
  ],
  "fulfillment": {
    "expectations": [
      {
        "id": "exp_1",
        "line_items": [{ "id": "li_shoes", "quantity": 3 }],
        "method_type": "shipping",
        "destination": {
          "street_address": "123 Main St",
          "address_locality": "Austin",
          "address_region": "TX",
          "address_country": "US",
          "postal_code": "78701"
        },
        "description": "Arrives in 2-3 business days",
        "fulfillable_on": "now"
      },
      {
        "id": "exp_2",
        "line_items": [{ "id": "li_shirts", "quantity": 2 }],
        "method_type": "shipping",
        "destination": {
          "street_address": "123 Main St",
          "address_locality": "Austin",
          "address_region": "TX",
          "address_country": "US",
          "postal_code": "78701"
        },
        "description": "Backordered - ships Jan 15, arrives in 7-10 days",
        "fulfillable_on": "2025-01-15T00:00:00Z"
      }
    ],
    "events": [
      {
        "id": "evt_1",
        "occurred_at": "2025-01-08T10:30:00Z",
        "type": "delivered",
        "line_items": [{ "id": "li_shoes", "quantity": 3 }],
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
      "occurred_at": "2025-01-10T14:30:00Z",
      "status": "completed",
      "line_items": [{ "id": "li_shoes", "quantity": 1 }],
      "amount": 3000,
      "description": "Defective item"
    }
  ],
  "totals": [
    { "type": "subtotal", "amount": 13000 },
    { "type": "shipping", "amount": 1200 },
    { "type": "tax", "amount": 1142 },
    { "type": "total", "amount": 15342 }
  ]
}
```

## 이벤트

비즈니스는 주문 생성 이후 주문 상태 변경을 이벤트로 전송합니다.

| 이벤트 메커니즘                             | 메서드 | 엔드포인트      | 설명                                                  |
| ------------------------------------------- | ------ | --------------- | ----------------------------------------------------- |
| [Order Event Webhook](#order-event-webhook) | `POST` | 플랫폼 제공 URL | 비즈니스가 주문 라이프사이클 이벤트를 플랫폼으로 전송 |

### 주문 이벤트 웹훅

비즈니스는 파트너 온보딩 중 플랫폼이 제공한 웹훅 URL로 주문 이벤트를 POST합니다. URL 형식은 플랫폼마다 다를 수 있습니다.

**Inputs**

| Name          | Type                                                                                     | Required | Description                                                                                                                                  |
| ------------- | ---------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| ucp           | [UCP Response Order Schema](/ucp-docs-ko/specification/order/#ucp-response-order-schema) | **Yes**  | Protocol metadata for discovery profiles and responses. Uses slim schema pattern with context-specific required fields.                      |
| id            | string                                                                                   | **Yes**  | Unique order identifier.                                                                                                                     |
| checkout_id   | string                                                                                   | **Yes**  | Associated checkout ID for reconciliation.                                                                                                   |
| permalink_url | string                                                                                   | **Yes**  | Permalink to access the order on merchant site.                                                                                              |
| line_items    | Array\[[Order Line Item](/ucp-docs-ko/specification/order/#order-line-item)\]            | **Yes**  | Immutable line items — source of truth for what was ordered.                                                                                 |
| fulfillment   | object                                                                                   | **Yes**  | Fulfillment data: buyer expectations and what actually happened.                                                                             |
| adjustments   | Array\[[Adjustment](/ucp-docs-ko/specification/order/#adjustment)\]                      | No       | Append-only event log of money movements (refunds, returns, credits, disputes, cancellations, etc.) that exist independently of fulfillment. |
| totals        | Array\[[Total](/ucp-docs-ko/specification/order/#total)\]                                | **Yes**  | Different totals for the order.                                                                                                              |
| event_id      | string                                                                                   | **Yes**  | Unique event identifier.                                                                                                                     |
| created_time  | string                                                                                   | **Yes**  | Event creation timestamp in RFC 3339 format.                                                                                                 |

**Output**

| Name | Type                                         | Required | Description |
| ---- | -------------------------------------------- | -------- | ----------- |
| ucp  | [Ucp](/ucp-docs-ko/specification/order/#ucp) | **Yes**  |             |

### 웹훅 URL 설정

플랫폼은 capability 협상 시 order capability의 `config` 필드에 웹훅 URL을 제공합니다. 비즈니스는 플랫폼 프로필에서 이 URL을 발견(discover)하여 주문 라이프사이클 이벤트 전송에 사용합니다.

| Name        | Type   | Required | Description                                                 |
| ----------- | ------ | -------- | ----------------------------------------------------------- |
| webhook_url | string | **Yes**  | URL where merchant sends order lifecycle events (webhooks). |

**예시:**

```json
{
  "dev.ucp.shopping.order": [
    {
      "version": "2026-01-11",
      "config": {
        "webhook_url": "https://platform.example.com/webhooks/ucp/orders"
      }
    }
  ]
}
```

### 웹훅 서명 검증

웹훅 페이로드는 진위성과 무결성을 보장하기 위해 비즈니스가 **반드시(MUST)** 서명하고, 플랫폼이 **반드시(MUST)** 검증해야 합니다.

#### 서명 (Business)

1. UCP 프로필의 `signing_keys` 배열에서 키를 선택합니다.
1. 선택한 키로 요청 본문에 대한 detached JWT(RFC 7797)를 생성합니다.
1. JWT를 `Request-Signature` 헤더에 포함합니다.
1. 수신자가 검증 키를 식별할 수 있도록 JWT 헤더의 `kid` 클레임에 키 ID를 포함합니다.

#### 검증 (Platform)

1. 수신한 웹훅 요청에서 `Request-Signature` 헤더를 추출합니다.
1. JWT 헤더를 파싱해 `kid`(키 ID)를 읽습니다.
1. `/.well-known/ucp`에서 비즈니스의 UCP 프로필을 가져옵니다(적절히 캐시 가능).
1. `signing_keys`에서 `kid`가 일치하는 키를 찾습니다.
1. 공개키로 요청 본문에 대한 JWT 서명을 검증합니다.
1. 검증 실패 시 적절한 오류 응답으로 웹훅을 거부합니다.

#### 키 로테이션

`signing_keys` 배열은 무중단(zero-downtime) 키 로테이션을 위해 다중 키를 지원합니다.

- **새 키 추가:** 새 키를 `signing_keys`에 추가한 뒤 해당 키로 서명을 시작합니다. 검증자는 `kid`로 키를 찾을 수 있습니다.
- **기존 키 제거:** 전송 중(in-flight) 웹훅이 충분히 전달된 뒤, `signing_keys`에서 이전 키를 제거합니다.

## 가이드라인

**Platform:**

- 수신 확인을 위해 빠르게 2xx HTTP 상태 코드를 **반드시(MUST)** 응답
- 응답 후 비동기로 이벤트 처리

**Business:**

- 모든 웹훅 페이로드를 자신의 `signing_keys` 배열 (`/.well-known/ucp`에 게시) 중 하나의 키로 **반드시(MUST)** 서명해야 합니다. 서명은 detached JWT(RFC 7797) 형식으로 `Request-Signature` 헤더에 **반드시(MUST)** 포함되어야 합니다.
- "Order created" 이벤트를 완전한 order 엔터티와 함께 **반드시(MUST)** 전송
- 업데이트 시 증분(delta)이 아닌 전체 order 엔터티를 **반드시(MUST)** 전송
- 실패한 웹훅 전송을 **반드시(MUST)** 재시도
- 웹훅 경로 또는 헤더에 business 식별자를 **반드시(MUST)** 포함

## 엔터티

### 항목 응답(Item Response)

| Name      | Type    | Required | Description                                                                                                                                                                 |
| --------- | ------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| id        | string  | **Yes**  | The product identifier, often the SKU, required to resolve the product details associated with this line item. Should be recognized by both the Platform, and the Business. |
| title     | string  | **Yes**  | Product title.                                                                                                                                                              |
| price     | integer | **Yes**  | Unit price in minor (cents) currency units.                                                                                                                                 |
| image_url | string  | No       | Product image URI.                                                                                                                                                          |

### 우편 주소(Postal Address)

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

### 응답(Response)

| Name    | Type    | Required | Description                                                                                                                     |
| ------- | ------- | -------- | ------------------------------------------------------------------------------------------------------------------------------- |
| version | string  | **Yes**  | Entity version in YYYY-MM-DD format.                                                                                            |
| spec    | string  | No       | URL to human-readable specification document.                                                                                   |
| schema  | string  | No       | URL to JSON Schema defining this entity's structure and payloads.                                                               |
| id      | string  | No       | Unique identifier for this entity instance. Used to disambiguate when multiple instances exist.                                 |
| config  | object  | No       | Entity-specific configuration. Structure defined by each entity's schema.                                                       |
| extends | OneOf[] | No       | Parent capability(s) this extends. Present for extensions, absent for root capabilities. Use array for multi-parent extensions. |

### 합계 응답(Total Response)

| Name         | Type    | Required | Description                                                                                                                   |
| ------------ | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------- |
| type         | string  | **Yes**  | Type of total categorization. **Enum:** `items_discount`, `subtotal`, `discount`, `fulfillment`, `tax`, `fee`, `total`        |
| display_text | string  | No       | Text to display against the amount. Should reflect appropriate method (e.g., 'Shipping', 'Delivery').                         |
| amount       | integer | **Yes**  | If type == total, sums subtotal - discount + fulfillment + tax + fee. Should be >= 0. Amount in minor (cents) currency units. |

### UCP 주문 응답

| Name             | Type   | Required | Description                                            |
| ---------------- | ------ | -------- | ------------------------------------------------------ |
| version          | string | **Yes**  | UCP version in YYYY-MM-DD format.                      |
| services         | object | No       | Service registry keyed by reverse-domain name.         |
| capabilities     | object | No       | Capability registry keyed by reverse-domain name.      |
| payment_handlers | object | No       | Payment handler registry keyed by reverse-domain name. |
| capabilities     | any    | No       |                                                        |
