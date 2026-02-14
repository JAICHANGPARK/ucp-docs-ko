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

# Cart Capability

* **Capability Name:** `dev.ucp.shopping.cart`
* **Version:** `DRAFT`

## 개요

Cart capability는 checkout의 복잡성을 도입하지 않고 바스켓 빌딩을 가능하게 합니다.
[Checkout](checkout.md)이 payment handler, 상태 라이프사이클, 주문 확정을 관리하는 반면,
cart는 구매 의도가 확정되기 전 단계에서 아이템을 모으기 위한
경량 CRUD 인터페이스를 제공합니다.

**Cart와 Checkout의 사용 기준:**

* **Cart**: 사용자가 탐색·비교·나중 저장 단계에 있음.
  결제 구성 불필요. 플랫폼/에이전트는 항목 추가·제거·수정을 자유롭게 수행 가능.
* **Checkout**: 사용자가 구매 의도를 명확히 표현한 상태.
  payment handler가 구성되고 상태 라이프사이클이 시작되며,
  세션이 완료 단계로 진행됨.

일반적인 흐름: `cart session` &#8594; `checkout session` &#8594; `order`

Cart는 다음을 지원합니다.

* **점진적 구성(Incremental building)**: 세션을 넘나들며 항목 추가/제거
* **로컬라이즈드 추정치(Localized estimates)**: 전체 checkout 오버헤드 없이
  컨텍스트 기반 가격 추정 제공
* **공유(Sharing)**: `continue_url`을 통한 cart 공유 및 복구

## Cart vs Checkout

| Aspect | Cart | Checkout |
| ------ | ---- | -------- |
| **Purpose** | 구매 전 탐색 | 구매 확정 |
| **Payment** | 없음 | 필수(handler, instrument) |
| **Status** | 이진 상태(존재/미존재) | 라이프사이클(`incomplete` → `completed`) |
| **Complete Operation** | 없음 | 있음 |
| **Totals** | 추정치(부분적일 수 있음) | 최종 가격 |

## Cart-to-Checkout 변환

Cart capability가 협상되면,
플랫폼은 Create Checkout 요청에 `cart_id`를 제공하여 cart를 checkout으로 변환할 수 있습니다.
이때 cart 내용(`line_items`, `context`, `buyer`)이 checkout 세션 초기값으로 사용됩니다.

```json
{
  "cart_id": "cart_abc123",
  "line_items": []
}
```

비즈니스는 cart 내용을 **MUST** 사용해야 하며,
checkout payload의 중복 필드는 **MUST** 무시해야 합니다.
`cart_id` 파라미터는 비즈니스 프로필에서 cart capability가 광고된 경우에만 사용할 수 있습니다.

**멱등 변환(Idempotent conversion):**

해당 `cart_id`에 대해 아직 완료되지 않은 checkout이 이미 존재하면,
비즈니스는 새 checkout을 생성하는 대신 기존 checkout 세션을 **MUST** 반환해야 합니다.
이를 통해 cart당 단일 활성 checkout이 보장되며,
충돌하는 세션 생성을 방지합니다.

**변환 이후 cart 라이프사이클:**

`cart_id`로 checkout을 초기화한 경우,
비즈니스는 checkout 기간 동안 cart와 checkout 세션을 연결 상태로 유지하는 것을
**SHOULD** 권장합니다.

* **활성 checkout 중** — 비즈니스는 cart를 유지하고,
    checkout에서 발생한 관련 변경(수량 변경, 항목 제거)을
    cart에 반영하는 것을 **SHOULD** 권장합니다.
    이는 구매자가 checkout과 storefront 사이를 이동할 때
    back-to-storefront 흐름을 지원합니다.

* **checkout 완료 후** — 비즈니스는 TTL, checkout 완료, 기타 비즈니스 로직에 따라
    cart를 정리(clear)할 수 있습니다.
    정리된 cart ID에 대한 후속 요청은 `NOT_FOUND`를 반환하며,
    플랫폼은 `create_cart`로 새 세션을 시작할 수 있습니다.

## 가이드라인

### 플랫폼

* 구매 전 탐색과 세션 지속성을 위해 cart를 **MAY** 사용할 수 있습니다.
* 사용자가 구매 의도를 표현하면 cart를 checkout으로 변환하는 것을 **SHOULD** 권장합니다.
* 비즈니스 UI로 핸드오프하기 위해 `continue_url`을 **MAY** 표시할 수 있습니다.
* cart 만료/취소 시 `NOT_FOUND`를 정상적으로 처리하는 것을 **SHOULD** 권장합니다.

### 비즈니스

* cart 핸드오프 및 세션 복구를 위해 `continue_url` 제공을 **SHOULD** 권장합니다.
* TODO: `continue_url` 목적지(cart vs checkout) 논의 필요.
* 계산 가능한 경우 추정 totals 제공을 **SHOULD** 권장합니다.
* 주소 미확정 상태에서는 checkout 단계까지 fulfillment totals 생략을 **MAY** 할 수 있습니다.
* 검증 경고에 대해 informational message 반환을 **SHOULD** 권장합니다.
* `expires_at`으로 cart 만료 시간 설정을 **MAY** 할 수 있습니다.
* `cart_id` 기반 checkout 초기화 시
    [cart lifecycle requirements](#cart-to-checkout-conversion)을 준수하는 것을
    **SHOULD** 권장합니다.

## Cart 스키마 정의

{{ schema_fields('cart_resp', 'cart') }}

## 작업(Operation)

Cart capability는 다음 논리 작업을 정의합니다.

| Operation | Description |
| :--- | :--- |
| **Create Cart** | 새 cart 세션을 생성합니다. |
| **Get Cart** | cart 세션의 현재 상태를 조회합니다. |
| **Update Cart** | cart 세션을 업데이트합니다. |
| **Cancel Cart** | cart 세션을 취소합니다. |

### Create Cart

라인 아이템과 선택적 buyer/context 정보를 포함해 새 cart 세션을 생성합니다.
(로컬라이즈드 가격 추정 용도)

* [REST Binding](cart-rest.md#create-cart)
* [MCP Binding](cart-mcp.md#create_cart)

### Get Cart

cart 세션의 최신 상태를 조회합니다.
cart가 존재하지 않거나 만료/취소된 경우 `NOT_FOUND`를 반환합니다.

* [REST Binding](cart-rest.md#get-cart)
* [MCP Binding](cart-mcp.md#get_cart)

### Update Cart

cart 세션 전체를 교체합니다.
플랫폼은 전체 cart 리소스를 **MUST** 전송해야 하며,
전송된 리소스가 비즈니스 측 기존 상태를 대체합니다.

* [REST Binding](cart-rest.md#update-cart)
* [MCP Binding](cart-mcp.md#update_cart)

### Cancel Cart

cart 세션을 취소합니다.
비즈니스는 삭제 전 cart 상태를 **MUST** 반환해야 합니다.
해당 cart ID에 대한 후속 작업은 `NOT_FOUND`를 반환하는 것을 **SHOULD** 권장합니다.

* [REST Binding](cart-rest.md#cancel-cart)
* [MCP Binding](cart-mcp.md#cancel_cart)

## 엔터티

Cart는 [Checkout](checkout.md)과 동일한 엔터티 스키마를 재사용합니다.
이를 통해 cart를 checkout 세션으로 변환할 때 데이터 구조 일관성이 유지됩니다.

### Line Item

#### Line Item Create Request

{{ schema_fields('types/line_item_create_req', 'checkout') }}

#### Line Item Update Request

{{ schema_fields('types/line_item_update_req', 'checkout') }}

#### Line Item Response

{{ schema_fields('types/line_item_resp', 'checkout') }}

### Buyer

{{ schema_fields('buyer', 'checkout') }}

### Context

{{ schema_fields('context', 'checkout') }}

### Total

{{ schema_fields('types/total_resp', 'checkout') }}

세금은 계산 가능한 경우 포함될 수 있습니다.
플랫폼은 cart totals를 추정치로 간주해야 하며,
정확한 세금은 checkout 단계에서 계산됩니다.

### Message

{{ schema_fields('message', 'checkout') }}

#### Message Error

{{ schema_fields('types/message_error', 'checkout') }}

#### Message Info

{{ schema_fields('types/message_info', 'checkout') }}

#### Message Warning

{{ schema_fields('types/message_warning', 'checkout') }}

### Link

{{ schema_fields('types/link', 'checkout') }}
