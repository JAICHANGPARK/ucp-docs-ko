# 주문 이행(Fulfillment) 확장

## 개요

fulfillment 확장은 business가 실물 상품 이행(배송, 매장 수령 등) 지원 여부를 광고할 수 있게 합니다.

이 확장은 Checkout에 `fulfillment` 필드를 추가하며, 다음을 포함합니다.

- `methods[]` - 장바구니 아이템에 적용 가능한 fulfillment 방법(배송, 픽업 등)
- `line_item_ids` - 이 방법으로 처리되는 아이템
- `destinations[]` - 이행 대상 위치(주소, 매장 위치)
- `groups[]` - business가 생성한 패키지 단위, 각 그룹은 선택 가능한 `options[]` 포함
- `available_methods[]` - 아이템별 재고 기반 이행 가능성(선택)

**멘탈 모델:**

- `methods[0]` Shipping
- `line_item_ids` 👕👖
- `selected_destination_id` = `destinations[0].id` 🔘✅ 123 Fake St
- `groups[0]` 📦👕👖
  - `selected_option_id` = `options[0].id` 🔘✅ Standard $5
  - `options[1]` 🔘 Express $10
- `methods[1]` Pick Up in Store
- `line_item_ids` 👞
- `selected_destination_id` = `destinations[0].id` 🔘✅ Uptown Store
- `groups[0]` 📦👞
  - `selected_option_id` = `options[0].id` 🔘✅ In-Store Pickup
  - `options[1]` 🔘 Curbside Pickup

## 스키마

fulfillment는 실물 전달이 필요한 아이템에만 적용됩니다. 이행이 필요하지 않은 아이템(예: 디지털 상품)은 method에 할당할 필요가 없습니다.

### 속성

| Name        | Type                                                               | Required | Description          |
| ----------- | ------------------------------------------------------------------ | -------- | -------------------- |
| fulfillment | [Fulfillment](/ucp-docs-ko/specification/fulfillment/#fulfillment) | No       | Fulfillment details. |

### 엔터티

#### 주문 이행(Fulfillment)

| Name              | Type                                                                                                          | Required | Description                         |
| ----------------- | ------------------------------------------------------------------------------------------------------------- | -------- | ----------------------------------- |
| methods           | Array\[[Fulfillment Method](/ucp-docs-ko/specification/fulfillment/#fulfillment-method)\]                     | No       | Fulfillment methods for cart items. |
| available_methods | Array\[[Fulfillment Available Method](/ucp-docs-ko/specification/fulfillment/#fulfillment-available-method)\] | No       | Inventory availability hints.       |

#### 주문 이행 방식 응답

| Name                    | Type                                                                                                | Required | Description                                                                                                  |
| ----------------------- | --------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| id                      | string                                                                                              | **Yes**  | Unique fulfillment method identifier.                                                                        |
| type                    | string                                                                                              | **Yes**  | Fulfillment method type. **Enum:** `shipping`, `pickup`                                                      |
| line_item_ids           | Array[string]                                                                                       | **Yes**  | Line item IDs fulfilled via this method.                                                                     |
| destinations            | Array\[[Fulfillment Destination](/ucp-docs-ko/specification/fulfillment/#fulfillment-destination)\] | No       | Available destinations. For shipping: addresses. For pickup: retail locations.                               |
| selected_destination_id | ['string', 'null']                                                                                  | No       | ID of the selected destination.                                                                              |
| groups                  | Array\[[Fulfillment Group](/ucp-docs-ko/specification/fulfillment/#fulfillment-group)\]             | No       | Fulfillment groups for selecting options. Agent sets selected_option_id on groups to choose shipping method. |

#### 주문 이행 목적지 응답

This object MUST be one of the following types: [Shipping Destination](/ucp-docs-ko/specification/fulfillment/#shipping-destination), [Retail Location](/ucp-docs-ko/specification/fulfillment/#retail-location).

#### 배송 목적지 응답

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
| id               | string | **Yes**  | ID specific to this shipping destination.                                                                                                                                                                                                 |

#### 오프라인 매장 위치 응답

| Name    | Type                                                                     | Required | Description                       |
| ------- | ------------------------------------------------------------------------ | -------- | --------------------------------- |
| id      | string                                                                   | **Yes**  | Unique location identifier.       |
| name    | string                                                                   | **Yes**  | Location name (e.g., store name). |
| address | [Postal Address](/ucp-docs-ko/specification/fulfillment/#postal-address) | No       | Physical address of the location. |

#### 주문 이행 그룹 응답

| Name               | Type                                                                                      | Required | Description                                                            |
| ------------------ | ----------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------------------- |
| id                 | string                                                                                    | **Yes**  | Group identifier for referencing merchant-generated groups in updates. |
| line_item_ids      | Array[string]                                                                             | **Yes**  | Line item IDs included in this group/package.                          |
| options            | Array\[[Fulfillment Option](/ucp-docs-ko/specification/fulfillment/#fulfillment-option)\] | No       | Available fulfillment options for this group.                          |
| selected_option_id | ['string', 'null']                                                                        | No       | ID of the selected fulfillment option for this group.                  |

#### 주문 이행 옵션 응답

| Name                      | Type                                                            | Required | Description                                                                |
| ------------------------- | --------------------------------------------------------------- | -------- | -------------------------------------------------------------------------- |
| id                        | string                                                          | **Yes**  | Unique fulfillment option identifier.                                      |
| title                     | string                                                          | **Yes**  | Short label (e.g., 'Express Shipping', 'Curbside Pickup').                 |
| description               | string                                                          | No       | Complete context for buyer decision (e.g., 'Arrives Dec 12-15 via FedEx'). |
| carrier                   | string                                                          | No       | Carrier name (for shipping).                                               |
| earliest_fulfillment_time | string                                                          | No       | Earliest fulfillment date.                                                 |
| latest_fulfillment_time   | string                                                          | No       | Latest fulfillment date.                                                   |
| totals                    | Array\[[Total](/ucp-docs-ko/specification/fulfillment/#total)\] | **Yes**  | Fulfillment option totals breakdown.                                       |

#### 주문 이행 가능 방식 응답

| Name           | Type               | Required | Description                                                                              |
| -------------- | ------------------ | -------- | ---------------------------------------------------------------------------------------- |
| type           | string             | **Yes**  | Fulfillment method type this availability applies to. **Enum:** `shipping`, `pickup`     |
| line_item_ids  | Array[string]      | **Yes**  | Line items available for this fulfillment method.                                        |
| fulfillable_on | ['string', 'null'] | No       | 'now' for immediate availability, or ISO 8601 date for future (preorders, transfers).    |
| description    | string             | No       | Human-readable availability info (e.g., 'Available for pickup at Downtown Store today'). |

#### 합계 응답

| Name         | Type    | Required | Description                                                                                                                   |
| ------------ | ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------- |
| type         | string  | **Yes**  | Type of total categorization. **Enum:** `items_discount`, `subtotal`, `discount`, `fulfillment`, `tax`, `fee`, `total`        |
| display_text | string  | No       | Text to display against the amount. Should reflect appropriate method (e.g., 'Shipping', 'Delivery').                         |
| amount       | integer | **Yes**  | If type == total, sums subtotal - discount + fulfillment + tax + fee. Should be >= 0. Amount in minor (cents) currency units. |

#### 우편 주소(Postal Address)

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

### 예시

```json
{
  "fulfillment": {
    "methods": [
      {
        "id": "method_1",
        "type": "shipping",
        "line_item_ids": ["shirt", "pants"],
        "selected_destination_id": "dest_1",
        "destinations": [
          {
            "id": "dest_1",
            "street_address": "123 Main St",
            "address_locality": "Springfield",
            "address_region": "IL",
            "postal_code": "62701",
            "address_country": "US"
          }
        ],
        "groups": [
          {
            "id": "package_1",
            "line_item_ids": ["shirt", "pants"],
            "selected_option_id": "standard",
            "options": [
              {
                "id": "standard",
                "title": "Standard Shipping",
                "description": "Arrives Dec 12-15 via USPS",
                "totals": [
                  {
                    "type": "total",
                    "amount": 500
                  }
                ]
              },
              {
                "id": "express",
                "title": "Express Shipping",
                "description": "Arrives Dec 10-11 via FedEx",
                "totals": [
                  {
                    "type": "total",
                    "amount": 1000
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 렌더링

fulfillment 옵션은 **method-agnostic 렌더링**을 목표로 설계되었습니다. platform은 method 타입(배송/픽업 등)을 구체적으로 이해하지 않아도 옵션을 의미 있게 표시할 수 있습니다. business가 사전 계산된 사람이 읽기 쉬운 필드를 제공하고, platform은 이를 그대로 렌더링하면 됩니다.

### 사람이 읽기 쉬운 필드

| 위치                  | 필드          | 필수 | 목적                                       |
| --------------------- | ------------- | ---- | ------------------------------------------ |
| `groups[].options[]`  | `title`       | Yes  | 같은 그룹 내 옵션을 구분하는 기본 라벨     |
| `groups[].options[]`  | `description` | No   | title을 보조하는 추가 설명                 |
| `groups[].options[]`  | `total`       | Yes  | 소수 단위 가격(아직 확정 전이면 null 가능) |
| `available_methods[]` | `description` | No   | 대체 가능 방법에 대한 독립 설명            |

### 비즈니스 책임

**`options[].title`에 대해:**

- 같은 그룹 내 형제 옵션과 구분되도록 **MUST** 작성
- 방법/속도를 포함하는 것이 **SHOULD** (예: "Express Shipping", "Curbside Pickup")
- `description`이 없어도 구매자 의사결정에 충분해야 **MUST** 함

**`options[].description`에 대해:**

- `title` 또는 `total`을 반복하면 안 되며(**MUST NOT**), 보조 맥락만 제공
- 도착 시점/택배사/의사결정 관련 정보를 포함하는 것이 **SHOULD**
- 완전한 문장 또는 구로 작성하는 것이 **SHOULD** (예: "Arrives Dec 12-15 via FedEx")
- title만으로 충분하면 생략 가능(**MAY**)

**`available_methods[].description`에 대해:**

- 무엇을/언제/어디서 처리 가능한지 설명하는 독립 문장이어야 **MUST** 함
- platform 대화 UI에 그대로 사용할 수 있어야 **SHOULD** 함 (예: "Pants available for pickup at Downtown Store today at 2pm")

**정렬 순서에 대해:**

- business는 `options[]`를 의미 있는 순서(예: 최저가 우선, 최단시간 우선)로 반환하는 것이 **SHOULD**
- platform은 제공된 순서 그대로 렌더링하는 것이 **SHOULD**

### 플랫폼 책임

platform은 fulfillment를 범용 렌더링 가능한 구조로 취급하는 것이 **SHOULD** 합니다.

- 각 옵션을 `title`, `description`, `total` 기반 카드 형태로 렌더링
- business가 제공한 순서대로 옵션 제시
- 반환된 모든 method를 제시 (method 선택은 구매자 결정)
- `available_methods[].description`을 사용해 대체 옵션 노출

platform은 인식 가능한 method 타입에 대해 향상 UX를 제공할 수 있습니다(**MAY**). (예: pickup 매장 선택기, shipping 운송사 로고) 단, 이는 선택 사항입니다. 기본 계약은 **`title` + `description` + `total`만으로 모든 옵션을 렌더링 가능해야 한다**는 점입니다.

구매자가 플랫폼이 완전 처리할 수 없는 옵션을 선택한 경우, platform은 business checkout으로 핸드오프하기 위해 `continue_url`을 사용하는 것이 **SHOULD** 됩니다.

## 사용 가능한 방식(Available Methods)

available methods는 특정 아이템이 특정 method로 이행 가능한지, 그리고 언제 가능한지를 나타냅니다. 사용 사례 예시:

- **대체 방법 안내**: "이 바지는 Downtown Store 매장 수령도 가능합니다"
- **나중 이행**: 예약 주문, 원거리 창고 출고, 매장 재고 입고 후 픽업

```json
{
  "fulfillment": {
    "methods": [
      {
        "id": "shipping",
        "type": "shipping",
        "line_item_ids": ["shirt", "pants"]
      },
      {
        "id": "pickup",
        "type": "pickup",
        "line_item_ids": []
      }
    ],
    "available_methods": [
      {
        "type": "shipping",
        "line_item_ids": ["shirt", "pants"],
        "fulfillable_on": "now"
      },
      {
        "type": "pickup",
        "line_item_ids": ["pants"],
        "fulfillable_on": "2026-12-01T10:00:00Z",
        "description": "Available for pickup at Downtown Store today at 2pm"
      }
    ]
  }
}
```

`description` 필드는 platform이 구매자에게 대체 옵션을 안내할 수 있게 합니다.

> 🤖 The shirt and pants ship for $5, arriving in 5-8 days. Or the pants can be picked up at Downtown Store in 4 hours.

구매자가 pickup을 선택했지만 platform이 분할 fulfillment를 지원하지 않으면, platform은 business checkout으로 핸드오프하기 위해 `continue_url`을 사용하는 것이 **SHOULD** 됩니다.

## 구성(Configuration)

business와 platform은 각자의 프로필에서 fulfillment 제약을 선언합니다. business는 platform 프로필을 조회해 이에 맞는 응답을 생성합니다.

### 플랫폼 프로필

platform은 `platform_schema`를 사용해 렌더링 capability를 선언합니다.

| Name                 | Type    | Required | Description                         |
| -------------------- | ------- | -------- | ----------------------------------- |
| supports_multi_group | boolean | No       | Enables multiple groups per method. |

config를 생략하거나 `supports_multi_group: false`로 설정한 platform은 단일 그룹 응답을 받습니다. 응답 구조는 항상 `methods[].groups[]`이며, 차이는 각 method 내 `groups.length`가 1을 초과할 수 있는지 여부입니다.

```json
// Default: single group per method
{ "dev.ucp.shopping.fulfillment": [{"version": "2026-01-11"}] }

// Opt-in: business MAY return multiple groups per method
{ "dev.ucp.shopping.fulfillment": [{"version": "2026-01-11", "config": { "supports_multi_group": true }}] }
```

### 비즈니스 프로필

business는 `merchant_config`를 사용해 자신이 지원하는 fulfillment 구성을 선언합니다.

| Name                       | Type         | Required | Description                                    |
| -------------------------- | ------------ | -------- | ---------------------------------------------- |
| allows_multi_destination   | object       | No       | Permits multiple destinations per method type. |
| allows_method_combinations | Array[array] | No       | Allowed method type combinations.              |

```json
{
  "capabilities": {
    "dev.ucp.shopping.fulfillment": [
      {
        "version": "2026-01-11",
        "config": {
          "allows_multi_destination": {
            "shipping": true
          },
          "allows_method_combinations": [["shipping", "pickup"]]
        }
      }
    ]
  }
}
```

위 예시는 shipping이 다중 주소를 지원하고, 장바구니에서 shipping+pickup 혼합이 가능함을 의미합니다.

### 비즈니스 응답 동작

**`supports_multi_group: false`(기본값)일 때:**

- business는 모든 아이템을 **method당 단일 그룹**으로 통합해야 합니다(**MUST**).
- 응답은 배열 구조를 유지합니다: `methods[].groups[]`에서 `groups.length === 1`
- 장바구니 요구에 따라 business는 여러 method(예: shipping + pickup)를 여전히 반환할 수 있습니다(**MAY**).

**`supports_multi_group: true`일 때:**

- business는 재고/패키징/창고 로직에 따라 method당 다중 그룹을 반환할 수 있습니다(**MAY**).
- platform은 그룹 선택 UI(예: 패키지별 배송 속도 선택)를 렌더링해야 합니다.

### 신규 Method 추가

fulfillment를 신규 method 타입(예: `local_delivery`)으로 확장하는 확장은, 아래를 포함하는 extension schema를 **반드시(MUST)** 추가해야 합니다.

1. `fulfillment_method`의 `type` enum에 신규 method 추가
1. 대응 business config 옵션 추가:
1. `allows_multi_destination.local_delivery: boolean`
1. `allows_method_combinations` 항목 enum (예: `"local_delivery"` 포함)

참고: platform의 `supports_multi_group`는 method-agnostic(단일 boolean)이므로 추가 확장이 필요하지 않습니다.

## 예시

### 기본

**Config:** 별도 요구 없음(기본 동작)

```json
{
  "fulfillment": {
    "methods": [
      {
        "id": "method_1",
        "type": "shipping",
        "line_item_ids": ["shirt", "pants"],
        "selected_destination_id": "dest_1",
        "destinations": [
          {
            "id": "dest_1",
            "street_address": "123 Main St",
            "address_locality": "Springfield",
            "address_region": "IL",
            "postal_code": "62701",
            "address_country": "US"
          }
        ],
        "groups": [
          {
            "id": "package_1",
            "line_item_ids": ["shirt", "pants"],
            "selected_option_id": "standard",
            "options": [
              {
                "id": "standard",
                "title": "Standard Shipping",
                "description": "Arrives Dec 12-15 via USPS",
                "totals": [
                  {
                    "type": "total",
                    "amount": 500
                  }
                ]
              },
              {
                "id": "express",
                "title": "Express Shipping",
                "description": "Arrives Dec 10-11 via FedEx",
                "totals": [
                  {
                    "type": "total",
                    "amount": 1000
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 그룹 분할(Split Groups)

**Config:** platform 프로필에 `config.supports_multi_group: true` 필요

business가 아이템을 여러 패키지로 나누고, 구매자가 패키지별 배송 옵션을 선택합니다.

```json
{
  "fulfillment": {
    "methods": [
      {
        "id": "method_1",
        "type": "shipping",
        "line_item_ids": ["shirt", "pants"],
        "selected_destination_id": "dest_1",
        "destinations": [
          {
            "id": "dest_1",
            "street_address": "123 Main St",
            "address_locality": "Springfield",
            "address_region": "IL",
            "postal_code": "62701",
            "address_country": "US"
          }
        ],
        "groups": [
          {
            "id": "package_1",
            "line_item_ids": ["shirt"],
            "selected_option_id": "standard",
            "options": [
              {
                "id": "standard",
                "title": "Standard",
                "totals": [ {"type": "total", "amount": 500} ]
              },
              {
                "id": "express",
                "title": "Express",
                "totals": [ {"type": "total", "amount": 1000} ]
              }
            ]
          },
          {
            "id": "package_2",
            "line_item_ids": ["pants"],
            "selected_option_id": "express",
            "options": [
              {
                "id": "standard",
                "title": "Standard",
                "totals": [ {"type": "total", "amount": 500} ]
              },
              {
                "id": "express",
                "title": "Express",
                "totals": [ {"type": "total", "amount": 1000} ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### 목적지 분할(Split Destinations)

**Config:** business 프로필에 `config.allows_multi_destination.shipping: true` 필요

셔츠는 엄마(미국), 바지는 할머니(홍콩)에게 배송되는 예시입니다. 동일 타입(shipping)의 method를 2개 두고 각각 독립 목적지를 가집니다.

```json
{
  "fulfillment": {
    "methods": [
      {
        "id": "method_1",
        "type": "shipping",
        "line_item_ids": ["shirt"],
        "selected_destination_id": "dest_mom",
        "destinations": [
          {
            "id": "dest_mom",
            "street_address": "123 Mom St",
            "address_locality": "Springfield",
            "address_region": "IL",
            "postal_code": "62701",
            "address_country": "US"
          }
        ],
        "groups": [
          {
            "id": "package_1",
            "line_item_ids": ["shirt"],
            "selected_option_id": "standard",
            "options": [
              {
                "id": "standard",
                "title": "Standard",
                "totals": [
                  {
                    "type": "total",
                    "amount": 500
                  }
                ]
              },
              {
                "id": "express",
                "title": "Express",
                "totals": [
                  {
                    "type": "total",
                    "amount": 1000
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        "id": "method_2",
        "type": "shipping",
        "line_item_ids": ["pants"],
        "selected_destination_id": "dest_grandma",
        "destinations": [
          {
            "id": "dest_grandma",
            "street_address": "88 Queensway",
            "address_locality": "Hong Kong",
            "address_country": "HK"
          }
        ],
        "groups": [
          {
            "id": "package_2",
            "line_item_ids": ["pants"],
            "selected_option_id": "standard",
            "options": [
              {
                "id": "standard",
                "title": "Standard",
                "totals": [
                  {
                    "type": "total",
                    "amount": 500
                  }
                ]
              },
              {
                "id": "express",
                "title": "Express",
                "totals": [
                  {
                    "type": "total",
                    "amount": 1000
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
}
```
