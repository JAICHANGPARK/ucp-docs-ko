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

# 체크아웃(Checkout) Capability

* **Capability 이름:** `dev.ucp.shopping.checkout`

## 개요

플랫폼이 체크아웃 세션을 중개할 수 있도록 합니다. AP2 Mandates 확장을 지원하지 않는 경우,
체크아웃은 신뢰 가능한 UI에서 사용자가 수동으로 최종 확정해야 합니다.

business는 Merchant of Record(MoR) 지위를 유지하며,
이 Capability를 통해 카드 결제를 수락하기 위해 별도로 PCI DSS 준수를 획득할 필요는 없습니다.

### 흐름 개요

![High-level checkout flow sequence diagram](site:specification/images/ucp-checkout-flow.png)

### 결제(Payments)

결제 핸들러는 business의 UCP 프로필 `/.well-known/ucp` 및
`checkout.ucp.payment_handlers`에서 탐색합니다. 핸들러는 결제 수단 수집을 위한
처리 명세(예: Google Pay, Shop Pay)를 정의합니다. 구매자가 결제를 제출하면,
platform은 수집된 수단 데이터를 `payment.instruments` 배열에 채웁니다.

`payment` 객체는 체크아웃 생성 시 선택 사항이며,
결제 처리가 필요 없는 사용 사례(예: 견적 생성, 장바구니 관리)에서는 생략할 수 있습니다.

### 이행(Fulfillment)

이행은 다양한 사용 사례를 수용하기 위해 UCP에서 확장(extension)으로 모델링됩니다.

체크아웃 객체에서 이행은 선택 사항입니다. 이를 통해 플랫폼은
실물 상품에 주로 필요한 이행 세부정보 없이도 디지털 상품 체크아웃을 처리할 수 있습니다.

### 체크아웃 상태 라이프사이클

체크아웃 `status` 필드는 세션의 현재 단계를 나타내고,
다음에 필요한 동작을 결정합니다. 상태는 business가 설정하며,
platform은 진행에 필요한 정보를 메시지 형태로 받습니다.

```text
       +------------+                         +---------------------+
       | incomplete |<----------------------->| requires_escalation |
       +-----+------+                         |   (buyer handoff    |
             |                                |  via continue_url)  |
             | all info collected             +----------+----------+
             v                                           |
    +------------------+                                 |
    |ready_for_complete|                                 |
    |                  |                                 | continue_url
    | (platform can    |                                 |
    | call Complete    |                                 |
    |   Checkout)      |                                 |
    +--------+---------+                                 |
             |                                           |
             | Complete Checkout                         |
             v                                           |
   +--------------------+                                |
   |complete_in_progress|                                |
   +---------+----------+                                |
             |                                           |
             +-----------------------+-------------------+
                                     v
                               +-------------+
                               |  completed  |
                               +-------------+

                               +-------------+
                               |  canceled   |
                               +-------------+
          (session invalid/expired - can occur from any state)
```

### 상태 값

* **`incomplete`**: 체크아웃 세션에 필수 정보가 누락되었거나 해결해야 할 문제가 있음.
  platform은 `messages` 배열을 확인해 맥락을 파악하고,
  Update Checkout으로 해결을 시도해야 합니다.

* **`requires_escalation`**: API로 제공할 수 없는 정보가 필요하거나,
  구매자 입력이 필요한 상태. platform은 `messages`로 필요한 사항을 파악해야 하며
  (아래 오류 처리 참고), `recoverable` 오류가 있다면 먼저 해결한 뒤
  `continue_url`로 구매자에게 핸드오프해야 합니다.

* **`ready_for_complete`**: 체크아웃에 필요한 정보가 모두 준비되어 platform이
  프로그래밍 방식으로 최종화할 수 있는 상태. Complete Checkout 호출 가능.

* **`complete_in_progress`**: business가 Complete Checkout 요청을 처리 중인 상태.

* **`completed`**: 주문이 성공적으로 접수된 상태.

* **`canceled`**: 체크아웃 세션이 무효 또는 만료된 상태.
  필요한 경우 platform은 새 체크아웃 세션을 시작해야 합니다.

### 오류 처리

`messages` 배열은 체크아웃 상태에 대한 오류/경고/정보 메시지를 담습니다.
오류 메시지에는 **누가 해결해야 하는지**를 나타내는 `severity` 필드가 포함됩니다.

| Severity | 의미 | 플랫폼 동작 |
| :------- | :--- | :---------- |
| `recoverable` | 플랫폼이 API로 수정 가능 | Update Checkout으로 해결 |
| `requires_buyer_input` | business가 API로 받을 수 없는 입력이 필요 | `continue_url`로 핸드오프 |
| `requires_buyer_review` | 구매자 검토/승인이 필요 | `continue_url`로 핸드오프 |

`requires_*` severity 오류는 `status: requires_escalation`에 기여합니다.
둘 다 구매자 핸드오프가 필요하지만 의미하는 체크아웃 상태가 다릅니다.

* `requires_buyer_input`은 체크아웃이 **불완전(incomplete)** 함을 의미합니다.
  business API가 프로그래밍 방식으로 수집할 수 없는 정보가 필요합니다.
* `requires_buyer_review`는 체크아웃이 **완전(complete)** 하지만,
  정책/규제/권한 규칙상 주문 전 구매자 승인이 필요함을 의미합니다.
  (예: 고액 주문 승인, 첫 구매 정책)

#### 오류 처리 알고리즘

상태가 `incomplete` 또는 `requires_escalation`일 때 플랫폼은 오류를 우선순위 스택으로 처리해야 합니다.
아래 예시는 세 가지 오류 유형(복구 가능 오류: 잘못된 전화번호,
구매자 입력 필요: 배송 일정,
구매자 검토 필요: 고액 주문)을 보여줍니다.
후자 둘은 핸드오프가 필요하며 플랫폼에 대한 명시적 신호로 동작합니다.
business는 이런 메시지를 가능한 한 빨리 노출하는 것이 **권장(SHOULD)** 되며,
platform은 핸드오프 전에 복구 가능한 오류를 우선 해결하는 것이 **권장(SHOULD)** 됩니다.

```json
{
  "status": "requires_escalation",
  "messages": [
    {
      "type": "error",
      "code": "invalid_phone",
      "severity": "recoverable",
      "content": "Phone number format is invalid"
    },
    {
      "type": "error",
      "code": "schedule_delivery",
      "severity": "requires_buyer_input",
      "content": "Select delivery window for your purchase"
    },
    {
      "type": "error",
      "code": "high_value_order",
      "severity": "requires_buyer_review",
      "content": "Orders over $500 require additional verification"
    }
  ]
}
```

오류 처리 알고리즘 예시:

```text
GIVEN checkout with messages array
FILTER errors FROM messages WHERE type = "error"

PARTITION errors INTO
  recoverable           WHERE severity = "recoverable"
  requires_buyer_input  WHERE severity = "requires_buyer_input"
  requires_buyer_review WHERE severity = "requires_buyer_review"

IF recoverable is not empty
  FOR EACH error IN recoverable
    ATTEMPT to fix error (e.g., reformat phone number)
  CALL Update Checkout
  RETURN and re-evaluate response

IF requires_buyer_input is not empty
  handoff_context = "incomplete, additional input from buyer is required"
ELSE IF requires_buyer_review is not empty
  handoff_context = "ready for final review by the buyer"
```

#### 표준 오류

표준 오류는 플랫폼이 일반 오류 처리 대신 적절한 전용 UX로 다루어야 하는
표준화된 오류 코드입니다.

| 코드 | 설명 |
| :--- | :--- |
| `out_of_stock` | 특정 상품 또는 변형(variant)을 사용할 수 없음 |
| `item_unavailable` | 상품을 구매할 수 없음(예: 판매 중단) |
| `address_undeliverable` | 제공된 주소로 배송 불가 |
| `payment_failed` | 결제 처리 실패 |

business는 표준 오류를 `severity: recoverable`로 표시하는 것이 **권장(SHOULD)** 됩니다.
이렇게 하면 플랫폼이 일반적인 오류 메시지 처리나 완료 단계 지연 대신,
재고 부족 안내/주소 검증 유도/결제수단 변경 같은 적절한 UX를 제공해야 함을 명확히 전달할 수 있습니다.

예: `out_of_stock`는 사전에 구체 UX가 필요하고,
`payment_required`는 제출 시점에 일반적으로 처리할 수 있습니다.

## Continue URL

`continue_url` 필드는 플랫폼 UI에서 business UI로 체크아웃을 핸드오프하여,
구매자가 체크아웃 세션을 이어서 완료할 수 있게 합니다.

### 제공 여부

business는 `status`가 `requires_escalation`일 때 `continue_url`을 **반드시(MUST)** 제공해야 합니다.
그 외 비종료 상태(`incomplete`, `ready_for_complete`, `complete_in_progress`)에서는
`continue_url` 제공이 **권장(SHOULD)** 됩니다.
종료 상태(`completed`, `canceled`)에서는 `continue_url`을 생략하는 것이 **권장(SHOULD)** 됩니다.

### 형식

`continue_url`은 절대 HTTPS URL이어야 하며(**MUST**),
매끄러운 핸드오프를 위해 체크아웃 상태를 보존하는 것이 **권장(SHOULD)** 됩니다.
business는 아래 두 방식 중 하나로 상태 보존을 구현할 수 있습니다(**MAY**).

#### 서버 측 상태 (권장)

서버 측 체크아웃 상태에 연결된 opaque URL:

```text
https://business.example.com/checkout-sessions/{checkout_id}
```

* 서버가 `checkout_id`에 연결된 체크아웃 상태를 유지
* 단순하고 안전하며 대부분 구현에 권장
* URL 수명은 보통 `expires_at`에 연동

#### Checkout Permalink

체크아웃 상태를 URL에 직접 인코딩해 서버 측 영속성 없이 재구성할 수 있는 stateless URL.
business는 체크아웃 핸드오프 및 빠른 진입을 지원하기 위해 이 형식 구현을
**권장(SHOULD)** 합니다. 예를 들어 platform은 buy-now 흐름 시작 시 체크아웃 상태를
미리 채울 수 있습니다.

> **참고:** Checkout permalink는
> [REST transport binding](checkout-rest.md)을 확장하는 REST 전용 구성입니다.
> permalink 접근 시 checkout UI로 리다이렉트되거나 checkout 페이지를 직접 렌더링합니다.

## 가이드라인

(상위 가이드라인에 더해)

### Platform

* **MAY** 에이전트를 활용해 체크아웃 세션을 보조할 수 있습니다.
  (예: 아이템 추가, 이행 주소 선택)
  단, 에이전트는 사용자가 체크아웃 상세를 검토하고 주문을 확정할 수 있도록
  신뢰 가능하고 결정적인 UI에 세션을 넘겨야 합니다.
* **MAY** 신뢰 가능한 결정적 UI에서 사용자를 언제든 다시 에이전트로 보낼 수 있습니다.
  예: 사용자가 체크아웃 화면을 나가 장바구니에 아이템을 더 추가하려는 경우.
* 플랫폼이 요청이 에이전트에 의해 수행되었음을 표시한 경우,
  **MAY** 에이전트 컨텍스트를 제공할 수 있습니다.
* 체크아웃 상태가 `requires_escalation`일 때 **MUST** `continue_url`을 사용해야 합니다.
* 다른 상황에서도 **MAY** `continue_url`을 사용해 business UI로 핸드오프할 수 있습니다.
* 핸드오프 수행 시,
  platform이 구성한 checkout permalink보다 business 제공 `continue_url`을 우선하는 것이
  **권장(SHOULD)** 됩니다.

### Business

* 체크아웃 완료 후 확인 이메일을 **반드시(MUST)** 발송해야 합니다.
* 정확한 오류 메시지를 제공하는 것이 **권장(SHOULD)** 됩니다.
* 체크아웃 세션 처리 로직은 **반드시(MUST)** 결정적이어야 합니다.
* `status` = `requires_escalation` 반환 시 `continue_url`을 **반드시(MUST)** 제공해야 합니다.
* `status` = `requires_escalation` 반환 시 `severity: escalation` 메시지를
  최소 1개 이상 **반드시(MUST)** 포함해야 합니다.
* 모든 비종료 체크아웃 응답에서 `continue_url` 제공이 **권장(SHOULD)** 됩니다.
* 체크아웃 세션이 "completed" 상태에 도달하면 불변(immutable)으로 간주됩니다.

## Capability 스키마 정의

{{ schema_fields('checkout_resp', 'checkout') }}

## 연산(Operations)

Checkout capability는 다음 논리 연산을 정의합니다.

| 연산 | 설명 |
| :--- | :--- |
| **Create Checkout** | 새 체크아웃 세션 시작. 사용자가 장바구니에 아이템을 담는 즉시 호출됨 |
| **Get Checkout** | 체크아웃 세션의 현재 상태 조회 |
| **Update Checkout** | 체크아웃 세션 갱신 |
| **Complete Checkout** | 체크아웃을 최종 확정하고 주문 접수 |
| **Cancel Checkout** | 체크아웃 세션 취소 |

### Create Checkout

사용자가 구매 의사를 표현했을 때(예: Buy 클릭),
아이템 상세를 포함해 체크아웃 세션을 시작하기 위해 platform이 호출합니다.

**권장 사항:** 불일치를 줄이고 더 매끄러운 사용자 경험을 위해,
business가 피드로 제공한 상품 데이터(가격/제목 등)는 응답에서 반환되는 실제 속성과
일치하는 것이 **권장(SHOULD)** 됩니다.

{{ method_fields('create_checkout', 'rest.openapi.json', 'checkout') }}

### Get Checkout

체크아웃 리소스의 최신 상태를 제공합니다. 취소/완료 이후 무엇을 반환할지는
business 정책에 달려 있습니다(예: 장기간 상태 유지 또는 특정 TTL 후 만료되어
`not found` 오류 반환). platform 측에서는 checkout TTL에 대한 별도 강제 규칙이 없습니다.

platform은 체크아웃 세션 생성 시 business가 `expires_at`로 제공한 TTL을 따릅니다.

{{ method_fields('get_checkout', 'rest.openapi.json', 'checkout') }}

### Update Checkout

체크아웃 리소스를 전체 교체(full replacement)합니다.
platform은 write-only 필드 업데이트를 포함한 전체 checkout 리소스를
**반드시(REQUIRED)** 전송해야 합니다. 요청에 담긴 리소스는
business 측 기존 체크아웃 세션 상태를 대체합니다.

{{ method_fields('update_checkout', 'rest.openapi.json', 'checkout') }}

### Complete Checkout

최종 주문 확정 호출입니다.
사용자가 선택한 아이템에 대해 결제 및 주문 확정을 의사결정했을 때 호출합니다.
응답은 `order` 필드가 채워진 checkout 객체이며,
반환된 `order`에는 배치된 주문의 전체 상태를 참조할 수 있는 `id`, `permalink_url` 등
필수 식별자가 포함됩니다.
주문 영속화 시점에는 `Checkout`의 필드를 사용해(`line_items`, `fulfillment` 등)
초기 주문 표현을 구성할 수 있습니다(**MAY**).

이 호출 이후 상세 상태는 주문과 연관 아이템이 공급망을 따라 이동함에 따라,
후속 이벤트를 통해 갱신됩니다.

{{ method_fields('complete_checkout', 'rest.openapi.json', 'checkout') }}

### Cancel Checkout

취소 가능한 경우 체크아웃 세션 취소에 사용합니다.
체크아웃 세션을 취소할 수 없는 경우(예: 이미 canceled 또는 completed),
business는 작업이 허용되지 않음을 나타내는 오류를 반환하는 것이 **권장(SHOULD)** 됩니다.
`completed`/`canceled`가 아닌 상태의 체크아웃 세션은 취소 가능해야 하며(**SHOULD**),
가능하도록 설계하는 것이 바람직합니다.

{{ method_fields('cancel_checkout', 'rest.openapi.json', 'checkout') }}

## 전송 바인딩(Transport Bindings)

위 추상 연산은 아래와 같이 특정 전송 프로토콜에 바인딩됩니다.

* [REST Binding](checkout-rest.md): 표준 HTTP 메서드와 JSON payload를 사용하는 REST API 매핑
* [MCP Binding](checkout-mcp.md): 에이전트 상호작용을 위한 Model Context Protocol 매핑
* [A2A Binding](checkout-a2a.md): 에이전트 상호작용을 위한 Agent-to-Agent Protocol 매핑
* [Embedded Checkout Binding](embedded-checkout.md): 임베디드 체크아웃 구현을 위한 JSON-RPC

## 엔터티

### Buyer

{{ schema_fields('buyer', 'checkout') }}

### Context

Context 신호는 잠정적 힌트입니다.
business는 권위 있는 데이터(예: 주소)가 없을 때 이 값을 활용하는 것이 **권장(SHOULD)** 되며,
지원하지 않는 값은 오류 없이 무시할 수 있습니다(**MAY**).
이는 명시적 검증과 오류 피드백이 필요한 authoritative selection과 다릅니다.

{{ schema_fields('context', 'checkout') }}

### Fulfillment Option

{{ extension_schema_fields('fulfillment.json#/$defs/fulfillment_option', 'checkout') }}

### Item

#### Item Create Request

{{ schema_fields('types/item_create_req', 'checkout') }}

#### Item Update Request

{{ schema_fields('types/item_update_req', 'checkout') }}

#### Item Response

{{ schema_fields('types/item_resp', 'checkout') }}

### Line Item

#### Line Item Create Request

{{ schema_fields('types/line_item_create_req', 'checkout') }}

#### Line Item Update Request

{{ schema_fields('types/line_item_update_req', 'checkout') }}

#### Line Item Response

{{ schema_fields('types/line_item_resp', 'checkout') }}

### Link

{{ schema_fields('types/link', 'checkout') }}

#### Well-Known Link Types

business는 거래와 관련된 링크를 가능한 한 모두 제공하는 것이 **권장(SHOULD)** 됩니다.
아래는 권장 well-known 타입입니다.

| 타입 | 설명 |
| :--- | :--- |
| `privacy_policy` | business 개인정보 처리방침 링크 |
| `terms_of_service` | business 이용약관 링크 |
| `refund_policy` | business 환불 정책 링크 |
| `shipping_policy` | business 배송 정책 링크 |
| `faq` | business 자주 묻는 질문 링크 |

business는 도메인별 요구를 위해 사용자 정의 타입을 정의할 수 있습니다(**MAY**).
platform은 알 수 없는 타입을 `title` 필드로 표시하거나 생략하는 방식으로
유연하게 처리하는 것이 **권장(SHOULD)** 됩니다.

### Message

{{ schema_fields('message', 'checkout') }}

### Message Error

{{ schema_fields('types/message_error', 'checkout') }}

### Message Info

{{ schema_fields('types/message_info', 'checkout') }}

### Message Warning

{{ schema_fields('types/message_warning', 'checkout') }}

### Payment

{{ schema_fields('payment', 'checkout') }}

### Payment Instrument

{{ schema_fields('payment_instrument', 'checkout') }}

### Payment Credential

{{ schema_fields('payment_credential', 'checkout') }}

### Postal Address

{{ schema_fields('postal_address', 'checkout') }}

### Response

{{ extension_schema_fields('capability.json#/$defs/response_schema', 'checkout') }}

### Total

#### Total Response

{{ schema_fields('types/total_resp', 'checkout') }}

### UCP Response Checkout

{{ extension_schema_fields('ucp.json#/$defs/response_checkout_schema', 'checkout') }}

### Order Confirmation

{{ schema_fields('order_confirmation', 'checkout') }}
