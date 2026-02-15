# 할인 확장

## 개요

Discount extension은 비즈니스가 checkout 세션에서 할인 코드를 지원함을 나타내고, 플랫폼과 비즈니스 간 할인 코드 공유 방식을 정의합니다.

**핵심 기능:**

- 하나 이상의 할인 코드 제출
- 사람이 읽을 수 있는 제목과 금액을 포함한 적용 할인 수신
- 거절된 코드는 상세 오류 코드와 함께 `messages[]`로 전달
- 자동 할인도 코드 기반 할인과 함께 노출

**의존성:**

- Checkout Capability

## 디스커버리

비즈니스는 프로필에서 discount 지원을 광고합니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": {
      "dev.ucp.shopping.discount": [
        {
          "version": "2026-01-11",
          "extends": "dev.ucp.shopping.checkout",
          "spec": "https://ucp.dev/specification/discount",
          "schema": "https://ucp.dev/schemas/shopping/discount.json"
        }
      ]
    }
  }
}
```

## 스키마

이 capability가 활성화되면 checkout은 `discounts` 객체로 확장됩니다.

### 할인 객체(Discounts Object)

| Name    | Type                                                                               | Required | Description                                                                                                |
| ------- | ---------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------------------- |
| codes   | Array[string]                                                                      | No       | Discount codes to apply. Case-insensitive. Replaces previously submitted codes. Send empty array to clear. |
| applied | Array\[[Applied Discount](/ucp-docs-ko/specification/discount/#applied-discount)\] | No       | Discounts successfully applied (code-based and automatic).                                                 |

### 적용 할인(Applied Discount)

| Name        | Type                                                                   | Required | Description                                                                                                                      |
| ----------- | ---------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------- |
| code        | string                                                                 | No       | The discount code. Omitted for automatic discounts.                                                                              |
| title       | string                                                                 | **Yes**  | Human-readable discount name (e.g., 'Summer Sale 20% Off').                                                                      |
| amount      | integer                                                                | **Yes**  | Total discount amount in minor (cents) currency units.                                                                           |
| automatic   | boolean                                                                | No       | True if applied automatically by merchant rules (no code required).                                                              |
| method      | string                                                                 | No       | Allocation method. 'each' = applied independently per item. 'across' = split proportionally by value. **Enum:** `each`, `across` |
| priority    | integer                                                                | No       | Stacking order for discount calculation. Lower numbers applied first (1 = first).                                                |
| allocations | Array\[[Allocation](/ucp-docs-ko/specification/discount/#allocation)\] | No       | Breakdown of where this discount was allocated. Sum of allocation amounts equals total amount.                                   |

### 할당(Allocation)

| Name   | Type    | Required | Description                                                                       |
| ------ | ------- | -------- | --------------------------------------------------------------------------------- |
| path   | string  | **Yes**  | JSONPath to the allocation target (e.g., '$.line_items[0]', '$.totals.shipping'). |
| amount | integer | **Yes**  | Amount allocated to this target in minor (cents) currency units.                  |

## 할당(Allocation) 상세

`applied` 배열은 할인이 어떻게 계산되고 분배되었는지를 설명합니다.

### 할당 방식(Allocation Method)

`method` 필드는 할인 계산 방식을 나타냅니다.

| Method   | Meaning                                  | Example                                        |
| -------- | ---------------------------------------- | ---------------------------------------------- |
| `each`   | 자격 조건을 만족하는 각 항목에 독립 적용 | "각 품목 10% 할인" → 10% × 품목 가격           |
| `across` | 금액 비율에 따라 분할                    | "주문 $10 할인" → $60 품목에 $6, $40 품목에 $4 |

### 중첩 적용 순서(Stacking Order)

여러 할인 적용 시 `priority`는 계산 순서를 의미합니다. 숫자가 낮을수록 먼저 적용됩니다.

```text
Cart: $100
Discount A (priority: 1): 20% off → $100 × 0.8 = $80
Discount B (priority: 2): $10 off → $80 - $10 = $70
```

퍼센트 할인은 적용 순서에 따라 복합 계산 결과가 달라지므로 순서가 중요합니다.

### 할당 배열(Allocations Array)

`allocations` 배열은 각 할인 금액이 어디에 반영되었는지 분해해 보여주며, 대상 식별에는 JSONPath를 사용합니다.

| Path Pattern        | Target            |
| ------------------- | ----------------- |
| `$.line_items[0]`   | 첫 번째 line item |
| `$.line_items[1]`   | 두 번째 line item |
| `$.totals.shipping` | 배송비            |

이를 통해 여러 할인이 중첩되는 경우에도, 플랫폼은 각 할인 금액이 각 line item에 얼마나 기여했는지 설명할 수 있습니다.

**Invariant:** `allocations[].amount`의 합은 `applied_discount.amount`와 같습니다.

## 작업(Operations)

할인 코드는 표준 checkout create/update 작업으로 제출됩니다.

**Request 동작:**

- **교체 의미(Replacement semantics):** `discounts.codes`를 제출하면 이전 제출 코드를 대체
- **코드 제거:** 모든 코드 제거는 빈 배열(`"codes": []`) 제출
- **대소문자 비구분:** 코드 매칭은 비즈니스 기준으로 대소문자 비구분

**Response 동작:**

- `discounts.applied`에는 활성 할인 전체(코드 기반 + 자동 할인)가 포함
- 거절 코드는 `messages[]`로 전달(아래 참고)
- 할인 금액은 `totals[]`, `line_items[].discount`에 반영

## 거절된 코드

제출된 할인 코드가 적용되지 않으면, 비즈니스는 다음처럼 `messages[]` 배열로 이를 전달합니다.

```json
{
  "messages": [
    {
      "type": "warning",
      "code": "discount_code_expired",
      "path": "$.discounts.codes[0]",
      "content": "Code 'SUMMER20' expired on December 1st"
    }
  ]
}
```

> **Implementation guidance:** 주문 총액 또는 사용자의 총액 기대에 영향을 주는 작업은, 플랫폼이 조용히 처리하지 않고 사용자에게 노출할 수 있도록 `type: "warning"`을 **SHOULD** 사용해야 합니다. 거절된 할인은 대표적인 사례입니다. 사용자는 할인을 기대했지만 적용되지 않으므로, 이를 안내해야 합니다.

**거절 할인 오류 코드:**

| Code                                   | Description                     |
| -------------------------------------- | ------------------------------- |
| `discount_code_expired`                | 코드 만료                       |
| `discount_code_invalid`                | 코드 없음 또는 형식 오류        |
| `discount_code_already_applied`        | 이미 적용된 코드                |
| `discount_code_combination_disallowed` | 다른 활성 할인과 조합 불가      |
| `discount_code_user_not_logged_in`     | 인증 사용자에게만 허용되는 코드 |
| `discount_code_user_ineligible`        | 사용자 자격 조건 미충족         |

## 자동 할인(Automatic Discounts)

비즈니스는 카트 내용, 고객 세그먼트, 프로모션 규칙에 따라 할인을 자동 적용할 수 있습니다.

- `discounts.applied`에 `automatic: true`로 표시되고 `code` 필드는 없음
- 플랫폼 동작 없이 자동 적용
- 플랫폼이 제거할 수 없음
- 투명성 확보를 위해 노출됨(플랫폼이 적용 이유 설명 가능)

## 라인 아이템 및 합계(Totals)에 미치는 영향

적용 할인은 core checkout 필드에 반영되며, 두 가지 서로 다른 total type을 사용합니다.

| Total Type       | When to Use                                |
| ---------------- | ------------------------------------------ |
| `items_discount` | line item에 할당된 할인(`$.line_items[*]`) |
| `discount`       | 주문 레벨 할인(배송, 수수료, 정액 할인 등) |

**type 판별 방식:** 할인의 `allocations`가 line item을 가리키면 `items_discount`에 기여합니다. allocations가 없거나 shipping/fees를 가리키면 `discount`에 기여합니다.

| Discount Type        | Where Reflected                            |
| -------------------- | ------------------------------------------ |
| Line-item discount   | `line_items[].discount` + `items_discount` |
| Order-level discount | `totals[]` with `type: "discount"`         |

**Invariant:** `totals[type=items_discount].amount`는 `sum(line_items[].discount)`와 같습니다.

`discounts.applied` 배열은 **무엇이** 적용되었는지 보여주고, `totals[]`와 `line_items[].discount`는 **어디에**, **얼마나** 적용되었는지 보여줍니다.

**금액 표기 규칙:** 모든 할인 금액은 minor currency unit의 양의 정수입니다. 사용자 표시 시 discount type은 차감 형태(예: "-$13.99")로 표시해야 합니다.

## 예시

### 주문 레벨 할인

주문 총액에 적용되는 정액 할인 예시입니다. allocations는 없으며, totals에서는 `type: "discount"`를 사용합니다.

**Request:**

```json
{
  "discounts": {
    "codes": ["SAVE10"]
  }
}
```

**Response:**

```json
{
  "discounts": {
    "codes": ["SAVE10"],
    "applied": [
      {
        "code": "SAVE10",
        "title": "$10 Off Your Order",
        "amount": 1000
      }
    ]
  },
  "totals": [
    {"type": "subtotal", "display_text": "Subtotal", "amount": 5000},
    {"type": "discount", "display_text": "Order Discount", "amount": 1000},
    {"type": "total", "display_text": "Total", "amount": 4000}
  ]
}
```

### 혼합 할인(품목 + 주문 레벨)

이 예시는 두 가지 할인 타입을 모두 보여줍니다. line item에 할당되는 품목 할인(20% off)과, 주문 레벨의 자동 배송 할인입니다.

**Request:**

```json
{
  "discounts": {
    "codes": ["SUMMER20"]
  }
}
```

**Response:**

```json
{
  "line_items": [
    {
      "id": "li_1",
      "item": {
        "id": "prod_1",
        "quantity": 2,
        "title": "T-Shirt",
        "price": 2000
      },
      "totals": [
        {"type": "subtotal", "amount": 4000},
        {"type": "items_discount", "amount": 800},
        {"type": "total", "amount": 3200}
      ]
    }
  ],
  "discounts": {
    "codes": ["SUMMER20"],
    "applied": [
      {
        "code": "SUMMER20",
        "title": "Summer Sale 20% Off",
        "amount": 800,
        "allocations": [
          {"path": "$.line_items[0]", "amount": 800}
        ]
      },
      {
        "title": "Free shipping on orders over $30",
        "amount": 599,
        "automatic": true
      }
    ]
  },
  "totals": [
    {"type": "subtotal", "display_text": "Subtotal", "amount": 4000},
    {"type": "items_discount", "display_text": "Item Discounts", "amount": 800},
    {"type": "discount", "display_text": "Order Discounts", "amount": 599},
    {"type": "fulfillment", "display_text": "Shipping", "amount": 0},
    {"type": "total", "display_text": "Total", "amount": 2601}
  ]
}
```

### 거절된 할인 코드

할인 코드가 적용되지 않으면, 거절 사유는 `messages[]` 배열로 전달됩니다. 코드는 `discounts.codes`에는 그대로 반환(에코)되지만, `discounts.applied`에는 포함되지 않습니다.

**Request:**

```json
{
  "discounts": {
    "codes": ["SAVE10", "EXPIRED50"]
  }
}
```

**Response:**

```json
{
  "discounts": {
    "codes": ["SAVE10", "EXPIRED50"],
    "applied": [
      {
        "code": "SAVE10",
        "title": "$10 Off Your Order",
        "amount": 1000
      }
    ]
  },
  "totals": [
    {"type": "subtotal", "display_text": "Subtotal", "amount": 5000},
    {"type": "discount", "display_text": "Order Discount", "amount": 1000},
    {"type": "total", "display_text": "Total", "amount": 4000}
  ],
  "messages": [
    {
      "type": "warning",
      "code": "discount_code_expired",
      "path": "$.discounts.codes[1]",
      "content": "Code 'EXPIRED50' expired on December 1st"
    }
  ]
}
```

### 할당(allocations)을 포함한 중첩 할인

여러 할인이 전체 allocation 내역과 함께 적용되는 예시입니다.

**Response:**

```json
{
  "line_items": [
    {
      "id": "li_1",
      "item": {
        "title": "T-Shirt",
        "price": 6000
      },
      "totals": [
        {"type": "subtotal", "amount": 6000},
        {"type": "items_discount", "amount": 1500},
        {"type": "total", "amount": 4500}
      ]
    },
    {
      "id": "li_2",
      "item": {
        "title": "Socks",
        "price": 4000
      },
      "totals": [
        {"type": "subtotal", "amount": 4000},
        {"type": "items_discount", "amount": 1000},
        {"type": "total", "amount": 3000}
      ]
    }
  ],
  "discounts": {
    "codes": ["SUMMER20", "LOYALTY5"],
    "applied": [
      {
        "code": "SUMMER20",
        "title": "Summer Sale 20% Off",
        "amount": 2000,
        "method": "each",
        "priority": 1,
        "allocations": [
          {"path": "$.line_items[0]", "amount": 1200},
          {"path": "$.line_items[1]", "amount": 800}
        ]
      },
      {
        "code": "LOYALTY5",
        "title": "$5 Loyalty Reward",
        "amount": 500,
        "method": "across",
        "priority": 2,
        "allocations": [
          {"path": "$.line_items[0]", "amount": 300},
          {"path": "$.line_items[1]", "amount": 200}
        ]
      }
    ]
  },
  "totals": [
    {"type": "subtotal", "display_text": "Subtotal", "amount": 10000},
    {"type": "items_discount", "display_text": "Item Discounts", "amount": 2500},
    {"type": "total", "display_text": "Total", "amount": 7500}
  ]
}
```

이 데이터가 있으면 에이전트는 다음처럼 설명할 수 있습니다.

> "Your T-Shirt ($60) got $12 off from the 20% summer sale, plus $3 from your
