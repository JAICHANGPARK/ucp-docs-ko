<!--
   Copyright 2026 UCP Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->

# 주문 기능

* **기능 이름:** `dev.ucp.shopping.order`

## 개요

주문은 체크아웃 제출이 성공적으로 완료된 뒤 확정된 거래를 나타냅니다.
무엇을 구매했는지, 어떻게 전달될 예정인지, 주문 생성 이후 어떤 일이 있었는지를
하나의 완전한 기록으로 제공합니다.

### 핵심 개념

주문은 크게 3가지 구성요소를 가집니다.

**라인 아이템(Line Items)** - 체크아웃에서 무엇을 구매했는지:

* 현재 수량 카운트(총 수량, 이행 수량)를 포함

**이행(Fulfillment)** - 아이템이 어떻게 전달되는지:

* **기대치(Expectations)** - 구매자에게 보여지는 "언제/어떻게 도착하는지"에 대한 *약속*
* **이벤트(append-only log)** - 실제로 어떤 일이 발생했는지 (예: 👕 배송됨)

**조정(Adjustments, append-only log)** - 이행과 독립적인 주문 이후 이벤트:

* 보통 금액 이동(환불, 반품, 크레딧, 분쟁, 취소)
* 주문 이후 발생하는 어떤 변경도 가능
* 이행 이전/중간/이후 어느 시점에도 발생 가능

## 데이터 모델

### 라인 아이템

라인 아이템은 체크아웃에서 구매한 항목과 현재 상태를 나타냅니다.

* 아이템 상세(상품, 가격, 주문 수량)
* 수량 카운트와 상태는 파생(derived)됨

### 이행(Fulfillment)

이행은 아이템이 구매자에게 전달되는 방식을 추적합니다.

#### 기대치(Expectations)

**기대치**는 구매자 관점의 아이템 묶음(예: "패키지 📦")으로, 다음을 나타냅니다.

* 어떤 아이템이 함께 묶였는지
* 어디로 가는지(`destination`)
* 어떤 방식으로 전달되는지(`method_type`)
* 언제 도착하는지(`description`, `fulfillable_on`)

기대치는 주문 이후 분할/병합/조정될 수 있습니다. 예를 들면:

* 배송일 기준으로 묶기: "무엇이 언제 오는지"
* 유연성을 위해 넓은 날짜 범위의 단일 기대치 사용
* 목표는 **구매자 기대치 설정**이며, 이는 좋은 구매 경험을 위한 핵심입니다.

#### 이행 이벤트(Fulfillment Events)

**이행 이벤트**는 실제 배송 상태를 추적하는 append-only 로그입니다.

* 라인 아이템 ID와 수량을 참조
* 트래킹 정보를 포함
* `type`은 개방형 문자열 필드로, 비즈니스가 필요에 맞게 정의 가능
  (일반 예시: `processing`, `shipped`, `in_transit`, `delivered`,
  `failed_attempt`, `canceled`, `undeliverable`, `returned_to_sender`)

### 조정(Adjustments)

**조정**은 이행과 독립적으로 존재하는 append-only 이벤트 로그입니다.

* `type`은 개방형 문자열 필드로, 비즈니스가 필요에 맞게 정의 가능
  (보통 `refund`, `return`, `credit`,
  `price_adjustment`, `dispute`, `cancellation` 같은 금액 이동)
* 주문 이후 변경이면 어떤 것이든 포함 가능
* 필요 시 라인 아이템에 연결 가능(또는 배송비 환불 같은 주문 단위 이벤트)
* 관련 시 금액(`amount`) 포함
* 이행 상태와 무관하게 어느 시점에나 발생 가능

## 스키마

### 주문(Order)

{{ schema_fields('order', 'order') }}

### 주문 라인 아이템(Order Line Item)

라인 아이템은 체크아웃에서 구매한 내용과 현재 상태를 반영합니다.
상태 및 수량 카운트는 이벤트 로그를 기준으로 계산되어야 합니다.

{{ schema_fields('order_line_item', 'order') }}

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

기대치는 아이템이 언제/어떻게 전달되는지에 대한 구매자 관점의 묶음입니다.
이는 구매자에게 제공하는 현재 약속을 나타내며, 주문 이후 분할/병합/조정될 수 있습니다.

{{ schema_fields('expectation', 'order') }}

### 이행 이벤트(Fulfillment Event)

이벤트는 실제 배송 과정을 기록하는 append-only 레코드입니다. `type` 필드는
개방형 문자열로, 비즈니스가 이행 프로세스에 맞춰 값을 정의할 수 있습니다.

{{ schema_fields('fulfillment_event', 'order') }}

예시: `processing`, `shipped`, `in_transit`, `delivered`, `failed_attempt`,
`canceled`, `undeliverable`, `returned_to_sender` 등.

### 조정(Adjustment)

조정은 이행과 독립적으로 존재하는 다형성(polymorphic) 이벤트입니다.
`type` 필드는 개방형 문자열로, 비즈니스 요구에 맞게 정의할 수 있습니다.

{{ schema_fields('adjustment', 'order') }}

예시: `refund`, `return`, `credit`, `price_adjustment`, `dispute`,
`cancellation` 등.

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

| 이벤트 메커니즘 | 메서드 | 엔드포인트 | 설명 |
| :-------------- | :----- | :--------- | :--- |
| [Order Event Webhook](#order-event-webhook) | `POST` | 플랫폼 제공 URL | 비즈니스가 주문 라이프사이클 이벤트를 플랫폼으로 전송 |

### 주문 이벤트 웹훅 { #order-event-webhook }

비즈니스는 파트너 온보딩 중 플랫폼이 제공한 웹훅 URL로 주문 이벤트를 POST합니다.
URL 형식은 플랫폼마다 다를 수 있습니다.

{{ method_fields('order_event_webhook', 'rest.openapi.json', 'order') }}

### 웹훅 URL 설정

플랫폼은 capability 협상 시 order capability의 `config` 필드에 웹훅 URL을 제공합니다.
비즈니스는 플랫폼 프로필에서 이 URL을 발견(discover)하여 주문 라이프사이클 이벤트 전송에 사용합니다.

{{ extension_schema_fields('order.json#/$defs/platform_schema', 'order') }}

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

웹훅 페이로드는 진위성과 무결성을 보장하기 위해 비즈니스가 **반드시(MUST)** 서명하고,
플랫폼이 **반드시(MUST)** 검증해야 합니다.

#### 서명 (Business)

1. UCP 프로필의 `signing_keys` 배열에서 키를 선택합니다.
2. 선택한 키로 요청 본문에 대한 detached JWT(RFC 7797)를 생성합니다.
3. JWT를 `Request-Signature` 헤더에 포함합니다.
4. 수신자가 검증 키를 식별할 수 있도록 JWT 헤더의 `kid` 클레임에 키 ID를 포함합니다.

#### 검증 (Platform)

1. 수신한 웹훅 요청에서 `Request-Signature` 헤더를 추출합니다.
2. JWT 헤더를 파싱해 `kid`(키 ID)를 읽습니다.
3. `/.well-known/ucp`에서 비즈니스의 UCP 프로필을 가져옵니다(적절히 캐시 가능).
4. `signing_keys`에서 `kid`가 일치하는 키를 찾습니다.
5. 공개키로 요청 본문에 대한 JWT 서명을 검증합니다.
6. 검증 실패 시 적절한 오류 응답으로 웹훅을 거부합니다.

#### 키 로테이션

`signing_keys` 배열은 무중단(zero-downtime) 키 로테이션을 위해 다중 키를 지원합니다.

* **새 키 추가:** 새 키를 `signing_keys`에 추가한 뒤 해당 키로 서명을 시작합니다.
  검증자는 `kid`로 키를 찾을 수 있습니다.
* **기존 키 제거:** 전송 중(in-flight) 웹훅이 충분히 전달된 뒤,
  `signing_keys`에서 이전 키를 제거합니다.

## 가이드라인

**Platform:**

* 수신 확인을 위해 빠르게 2xx HTTP 상태 코드를 **반드시(MUST)** 응답
* 응답 후 비동기로 이벤트 처리

**Business:**

* 모든 웹훅 페이로드를 자신의 `signing_keys` 배열
  (`/.well-known/ucp`에 게시) 중 하나의 키로 **반드시(MUST)** 서명해야 합니다.
  서명은 detached JWT(RFC 7797) 형식으로 `Request-Signature` 헤더에 **반드시(MUST)** 포함되어야 합니다.
* "Order created" 이벤트를 완전한 order 엔터티와 함께 **반드시(MUST)** 전송
* 업데이트 시 증분(delta)이 아닌 전체 order 엔터티를 **반드시(MUST)** 전송
* 실패한 웹훅 전송을 **반드시(MUST)** 재시도
* 웹훅 경로 또는 헤더에 business 식별자를 **반드시(MUST)** 포함

## 엔터티

### 항목 응답(Item Response)

{{ schema_fields('types/item_resp', 'order') }}

### 우편 주소(Postal Address)

{{ schema_fields('postal_address', 'order') }}

### 응답(Response)

{{ extension_schema_fields('capability.json#/$defs/response_schema', 'order') }}

### 합계 응답(Total Response)

{{ schema_fields('types/total_resp', 'order') }}

### UCP 주문 응답

{{ extension_schema_fields('ucp.json#/$defs/response_order_schema', 'order') }}
