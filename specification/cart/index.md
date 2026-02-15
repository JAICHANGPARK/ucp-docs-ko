# 장바구니 기능

- **기능 이름:** `dev.ucp.shopping.cart`
- **Version:** `DRAFT`

## 개요

Cart capability는 checkout의 복잡성을 도입하지 않고 바스켓 빌딩을 가능하게 합니다. [Checkout](https://jaichangpark.github.io/ucp-docs-ko/specification/checkout/index.md)이 payment handler, 상태 라이프사이클, 주문 확정을 관리하는 반면, cart는 구매 의도가 확정되기 전 단계에서 아이템을 모으기 위한 경량 CRUD 인터페이스를 제공합니다.

**Cart와 Checkout의 사용 기준:**

- **Cart**: 사용자가 탐색·비교·나중 저장 단계에 있음. 결제 구성 불필요. 플랫폼/에이전트는 항목 추가·제거·수정을 자유롭게 수행 가능.
- **Checkout**: 사용자가 구매 의도를 명확히 표현한 상태. payment handler가 구성되고 상태 라이프사이클이 시작되며, 세션이 완료 단계로 진행됨.

일반적인 흐름: `cart session` → `checkout session` → `order`

Cart는 다음을 지원합니다.

- **점진적 구성(Incremental building)**: 세션을 넘나들며 항목 추가/제거
- **로컬라이즈드 추정치(Localized estimates)**: 전체 checkout 오버헤드 없이 컨텍스트 기반 가격 추정 제공
- **공유(Sharing)**: `continue_url`을 통한 cart 공유 및 복구

## 장바구니 vs 체크아웃

| 항목          | 장바구니                 | 체크아웃                                 |
| ------------- | ------------------------ | ---------------------------------------- |
| **목적**      | 구매 전 탐색             | 구매 확정                                |
| **결제**      | 없음                     | 필수(handler, instrument)                |
| **상태**      | 이진 상태(존재/미존재)   | 라이프사이클(`incomplete` → `completed`) |
| **완료 연산** | 없음                     | 있음                                     |
| **합계**      | 추정치(부분적일 수 있음) | 최종 가격                                |

## 장바구니-체크아웃 변환

Cart capability가 협상되면, 플랫폼은 Create Checkout 요청에 `cart_id`를 제공하여 cart를 checkout으로 변환할 수 있습니다. 이때 cart 내용(`line_items`, `context`, `buyer`)이 checkout 세션 초기값으로 사용됩니다.

```json
{
  "cart_id": "cart_abc123",
  "line_items": []
}
```

비즈니스는 cart 내용을 **MUST** 사용해야 하며, checkout payload의 중복 필드는 **MUST** 무시해야 합니다. `cart_id` 파라미터는 비즈니스 프로필에서 cart capability가 광고된 경우에만 사용할 수 있습니다.

**멱등 변환(Idempotent conversion):**

해당 `cart_id`에 대해 아직 완료되지 않은 checkout이 이미 존재하면, 비즈니스는 새 checkout을 생성하는 대신 기존 checkout 세션을 **MUST** 반환해야 합니다. 이를 통해 cart당 단일 활성 checkout이 보장되며, 충돌하는 세션 생성을 방지합니다.

**변환 이후 cart 라이프사이클:**

`cart_id`로 checkout을 초기화한 경우, 비즈니스는 checkout 기간 동안 cart와 checkout 세션을 연결 상태로 유지하는 것을 **SHOULD** 권장합니다.

- **활성 checkout 중** — 비즈니스는 cart를 유지하고, checkout에서 발생한 관련 변경(수량 변경, 항목 제거)을 cart에 반영하는 것을 **SHOULD** 권장합니다. 이는 구매자가 checkout과 storefront 사이를 이동할 때 back-to-storefront 흐름을 지원합니다.
- **checkout 완료 후** — 비즈니스는 TTL, checkout 완료, 기타 비즈니스 로직에 따라 cart를 정리(clear)할 수 있습니다. 정리된 cart ID에 대한 후속 요청은 `NOT_FOUND`를 반환하며, 플랫폼은 `create_cart`로 새 세션을 시작할 수 있습니다.

## 가이드라인

### 플랫폼

- 구매 전 탐색과 세션 지속성을 위해 cart를 **MAY** 사용할 수 있습니다.
- 사용자가 구매 의도를 표현하면 cart를 checkout으로 변환하는 것을 **SHOULD** 권장합니다.
- 비즈니스 UI로 핸드오프하기 위해 `continue_url`을 **MAY** 표시할 수 있습니다.
- cart 만료/취소 시 `NOT_FOUND`를 정상적으로 처리하는 것을 **SHOULD** 권장합니다.

### 비즈니스

- cart 핸드오프 및 세션 복구를 위해 `continue_url` 제공을 **SHOULD** 권장합니다.
- TODO: `continue_url` 목적지(cart vs checkout) 논의 필요.
- 계산 가능한 경우 추정 totals 제공을 **SHOULD** 권장합니다.
- 주소 미확정 상태에서는 checkout 단계까지 fulfillment totals 생략을 **MAY** 할 수 있습니다.
- 검증 경고에 대해 informational message 반환을 **SHOULD** 권장합니다.
- `expires_at`으로 cart 만료 시간 설정을 **MAY** 할 수 있습니다.
- `cart_id` 기반 checkout 초기화 시 [cart lifecycle requirements](#cart-to-checkout-conversion)을 준수하는 것을 **SHOULD** 권장합니다.

## 장바구니 스키마 정의

| Name         | Type                                                                                  | Required | Description                                                                                                                                        |
| ------------ | ------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| ucp          | [UCP Response Cart Schema](/ucp-docs-ko/specification/cart/#ucp-response-cart-schema) | **Yes**  | Protocol metadata for discovery profiles and responses. Uses slim schema pattern with context-specific required fields.                            |
| id           | string                                                                                | **Yes**  | Unique cart identifier.                                                                                                                            |
| line_items   | Array\[[Line Item Response](/ucp-docs-ko/specification/cart/#line-item-response)\]    | **Yes**  | Cart line items. Same structure as checkout. Full replacement on update.                                                                           |
| context      | [Context](/ucp-docs-ko/specification/cart/#context)                                   | No       | Buyer signals for localization (country, region, postal_code). Merchant uses for pricing, availability, currency. Falls back to geo-IP if omitted. |
| buyer        | [Buyer](/ucp-docs-ko/specification/cart/#buyer)                                       | No       | Optional buyer information for personalized estimates.                                                                                             |
| currency     | string                                                                                | **Yes**  | ISO 4217 currency code. Determined by merchant based on context or geo-IP.                                                                         |
| totals       | Array\[[Total Response](/ucp-docs-ko/specification/cart/#total-response)\]            | **Yes**  | Estimated cost breakdown. May be partial if shipping/tax not yet calculable.                                                                       |
| messages     | Array\[[Message](/ucp-docs-ko/specification/cart/#message)\]                          | No       | Validation messages, warnings, or informational notices.                                                                                           |
| links        | Array\[[Link](/ucp-docs-ko/specification/cart/#link)\]                                | No       | Optional merchant links (policies, FAQs).                                                                                                          |
| continue_url | string                                                                                | No       | URL for cart handoff and session recovery. Enables sharing and human-in-the-loop flows.                                                            |
| expires_at   | string                                                                                | No       | Cart expiry timestamp (RFC 3339). Optional.                                                                                                        |

## 작업(Operations)

Cart capability는 다음 논리 작업을 정의합니다.

| 작업                  | 설명                                |
| --------------------- | ----------------------------------- |
| **장바구니 생성**     | 새 cart 세션을 생성합니다.          |
| **장바구니 조회**     | cart 세션의 현재 상태를 조회합니다. |
| **장바구니 업데이트** | cart 세션을 업데이트합니다.         |
| **장바구니 취소**     | cart 세션을 취소합니다.             |

### 장바구니 생성

라인 아이템과 선택적 buyer/context 정보를 포함해 새 cart 세션을 생성합니다. (로컬라이즈드 가격 추정 용도)

- [REST Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-rest/#create-cart)
- [MCP Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-mcp/#create_cart)

### 장바구니 조회

cart 세션의 최신 상태를 조회합니다. cart가 존재하지 않거나 만료/취소된 경우 `NOT_FOUND`를 반환합니다.

- [REST Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-rest/#get-cart)
- [MCP Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-mcp/#get_cart)

### 장바구니 업데이트

cart 세션 전체를 교체합니다. 플랫폼은 전체 cart 리소스를 **MUST** 전송해야 하며, 전송된 리소스가 비즈니스 측 기존 상태를 대체합니다.

- [REST Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-rest/#update-cart)
- [MCP Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-mcp/#update_cart)

### 장바구니 취소

cart 세션을 취소합니다. 비즈니스는 삭제 전 cart 상태를 **MUST** 반환해야 합니다. 해당 cart ID에 대한 후속 작업은 `NOT_FOUND`를 반환하는 것을 **SHOULD** 권장합니다.

- [REST Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-rest/#cancel-cart)
- [MCP Binding](https://jaichangpark.github.io/ucp-docs-ko/specification/cart-mcp/#cancel_cart)

## 엔터티(Entities)

Cart는 [Checkout](https://jaichangpark.github.io/ucp-docs-ko/specification/checkout/index.md)과 동일한 엔터티 스키마를 재사용합니다. 이를 통해 cart를 checkout 세션으로 변환할 때 데이터 구조 일관성이 유지됩니다.

### 라인 아이템(Line Item)

#### 라인 아이템 생성 요청

| Name     | Type                                              | Required | Description                           |
| -------- | ------------------------------------------------- | -------- | ------------------------------------- |
| item     | [Item](/ucp-docs-ko/specification/checkout/#item) | **Yes**  |                                       |
| quantity | integer                                           | **Yes**  | Quantity of the item being purchased. |

#### 라인 아이템 업데이트 요청

| Name      | Type                                              | Required | Description                                            |
| --------- | ------------------------------------------------- | -------- | ------------------------------------------------------ |
| id        | string                                            | No       |                                                        |
| item      | [Item](/ucp-docs-ko/specification/checkout/#item) | **Yes**  |                                                        |
| quantity  | integer                                           | **Yes**  | Quantity of the item being purchased.                  |
| parent_id | string                                            | No       | Parent line item identifier for any nested structures. |

#### 라인 아이템 응답

| Name      | Type                                                         | Required | Description                                            |
| --------- | ------------------------------------------------------------ | -------- | ------------------------------------------------------ |
| id        | string                                                       | **Yes**  |                                                        |
| item      | [Item](/ucp-docs-ko/specification/checkout/#item)            | **Yes**  |                                                        |
| quantity  | integer                                                      | **Yes**  | Quantity of the item being purchased.                  |
| totals    | Array\[[Total](/ucp-docs-ko/specification/checkout/#total)\] | **Yes**  | Line item totals breakdown.                            |
| parent_id | string                                                       | No       | Parent line item identifier for any nested structures. |

### 구매자(Buyer)

| Name         | Type   | Required | Description              |
| ------------ | ------ | -------- | ------------------------ |
| first_name   | string | No       | First name of the buyer. |
| last_name    | string | No       | Last name of the buyer.  |
| email        | string | No       | Email of the buyer.      |
| phone_number | string | No       | E.164 standard.          |

### 컨텍스트(Context)

| Name            | Type   | Required | Description                                                                                                                                                                                                                                                                                                                                                                         |
| --------------- | ------ | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| address_country | string | No       | The country. Recommended to be in 2-letter ISO 3166-1 alpha-2 format, for example "US". For backward compatibility, a 3-letter ISO 3166-1 alpha-3 country code such as "SGP" or a full country name such as "Singapore" can also be used. Optional hint for market context (currency, availability, pricing)—higher-resolution data (e.g., shipping address) supersedes this value. |
| address_region  | string | No       | The region in which the locality is, and which is in the country. For example, California or another appropriate first-level Administrative division. Optional hint for progressive localization—higher-resolution data (e.g., shipping address) supersedes this value.                                                                                                             |
| postal_code     | string | No       | The postal code. For example, 94043. Optional hint for regional refinement—higher-resolution data (e.g., shipping address) supersedes this value.                                                                                                                                                                                                                                   |
| intent          | string | No       | Background context describing buyer's intent (e.g., 'looking for a gift under $50', 'need something durable for outdoor use'). Informs relevance, recommendations, and personalization.                                                                                                                                                                                             |

### 합계(Total)

| Name         | Type    | Required | Description                                                                                                                   |
| ------------ | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------- |
| type         | string  | **Yes**  | Type of total categorization. **Enum:** `items_discount`, `subtotal`, `discount`, `fulfillment`, `tax`, `fee`, `total`        |
| display_text | string  | No       | Text to display against the amount. Should reflect appropriate method (e.g., 'Shipping', 'Delivery').                         |
| amount       | integer | **Yes**  | If type == total, sums subtotal - discount + fulfillment + tax + fee. Should be >= 0. Amount in minor (cents) currency units. |

세금은 계산 가능한 경우 포함될 수 있습니다. 플랫폼은 cart totals를 추정치로 간주해야 하며, 정확한 세금은 checkout 단계에서 계산됩니다.

### 메시지(Message)

This object MUST be one of the following types: [Message Error](/ucp-docs-ko/specification/checkout/#message-error), [Message Warning](/ucp-docs-ko/specification/checkout/#message-warning), [Message Info](/ucp-docs-ko/specification/checkout/#message-info).

#### 메시지 오류

| Name         | Type                                                          | Required | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------ | ------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| type         | string                                                        | **Yes**  | **Constant = error**. Message type discriminator.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| code         | [Error Code](/ucp-docs-ko/specification/checkout/#error-code) | **Yes**  | Error code identifying the type of error. Standard errors are defined in specification (see examples), and have standardized semantics; freeform codes are permitted.                                                                                                                                                                                                                                                                                                                                          |
| path         | string                                                        | No       | RFC 9535 JSONPath to the component the message refers to (e.g., $.items[1]).                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| content_type | string                                                        | No       | Content format, default = plain. **Enum:** `plain`, `markdown`                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| content      | string                                                        | **Yes**  | Human-readable message.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| severity     | string                                                        | **Yes**  | Declares who resolves this error. 'recoverable': agent can fix via API. 'requires_buyer_input': merchant requires information their API doesn't support collecting programmatically (checkout incomplete). 'requires_buyer_review': buyer must authorize before order placement due to policy, regulatory, or entitlement rules (checkout complete). Errors with 'requires\_*' severity contribute to 'status: requires_escalation'.* *Enum:*\* `recoverable`, `requires_buyer_input`, `requires_buyer_review` |

#### 메시지 정보

| Name         | Type   | Required | Description                                                    |
| ------------ | ------ | -------- | -------------------------------------------------------------- |
| type         | string | **Yes**  | **Constant = info**. Message type discriminator.               |
| path         | string | No       | RFC 9535 JSONPath to the component the message refers to.      |
| code         | string | No       | Info code for programmatic handling.                           |
| content_type | string | No       | Content format, default = plain. **Enum:** `plain`, `markdown` |
| content      | string | **Yes**  | Human-readable message.                                        |

#### 메시지 경고

| Name         | Type   | Required | Description                                                                                                                           |
| ------------ | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| type         | string | **Yes**  | **Constant = warning**. Message type discriminator.                                                                                   |
| path         | string | No       | JSONPath (RFC 9535) to related field (e.g., $.line_items[0]).                                                                         |
| code         | string | **Yes**  | Warning code. Machine-readable identifier for the warning type (e.g., final_sale, prop65, fulfillment_changed, age_restricted, etc.). |
| content      | string | **Yes**  | Human-readable warning message that MUST be displayed.                                                                                |
| content_type | string | No       | Content format, default = plain. **Enum:** `plain`, `markdown`                                                                        |

### 링크(Link)

| Name  | Type   | Required | Description                                                                                                                                                                                                                          |
| ----- | ------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| type  | string | **Yes**  | Type of link. Well-known values: `privacy_policy`, `terms_of_service`, `refund_policy`, `shipping_policy`, `faq`. Consumers SHOULD handle unknown values gracefully by displaying them using the `title` field or omitting the link. |
| url   | string | **Yes**  | The actual URL pointing to the content to be displayed.                                                                                                                                                                              |
| title | string | No       | Optional display text for the link. When provided, use this instead of generating from type.                                                                                                                                         |
