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

# 스키마 작성 가이드

이 가이드는 UCP JSON 스키마 작성 규칙을 설명합니다.
메타데이터 필드, 레지스트리 패턴, 스키마 변형(variants), 버전 관리를 다룹니다.

## 스키마 메타데이터 필드

UCP 스키마는 표준 JSON Schema 필드와 UCP 전용 메타데이터를 함께 사용합니다.

| Field | Standard | Purpose | Required For |
| ----- | -------- | ------- | ------------ |
| `$schema` | JSON Schema | JSON Schema draft 버전 선언 (`draft/2020-12` **SHOULD** 사용) | 모든 스키마 |
| `$id` | JSON Schema | `$ref` 해석을 위한 스키마의 정규 URI | 모든 스키마 |
| `title` | JSON Schema | 사람이 읽을 수 있는 표시 이름 | 모든 스키마 |
| `description` | JSON Schema | 스키마 목적 및 사용 방식 | 모든 스키마 |
| `name` | UCP | 역도메인 식별자(레지스트리 키로도 사용) | capabilities, services, handlers |
| `version` | UCP | 엔터티 버전(`YYYY-MM-DD` 형식) | capabilities, services, payment handlers |
| `id` | UCP | 다중 구성 구분을 위한 인스턴스 식별자 | payment handlers 전용 |

### 왜 Self-Describing인가?

Capability 스키마는 **self-describing이어야 합니다**.
플랫폼이 스키마를 가져왔을 때, 다른 문서를 교차 참조하지 않고도
해당 스키마가 어떤 capability와 버전을 의미하는지 즉시 판단할 수 있어야 합니다.
이는 다음 이유에서 중요합니다.

1. **독립 버전 관리**: Capability는 독립적으로 버전이 올라갈 수 있습니다.
   버전은 URL에서 추론하면 안 되며 스키마 자체가 명시적으로 선언해야 합니다.

2. **검증**: 검증기는 capability 선언의 `schema` URL이 가리키는 스키마 내부의
   `name`/`version`이 선언과 일치하는지 교차 검증할 수 있습니다.
   불일치는 작성 오류이며 빌드 시점에 잡아야 합니다.

3. **개발자 경험**: 통합 개발자가 스키마 파일을 읽을 때,
   `$id` URL을 역추적하지 않아도 해당 capability를 즉시 이해할 수 있습니다.

4. **간결한 네임스페이스**: `name` 필드는
   표준화된 역도메인 식별자(예: `dev.ucp.shopping.checkout`)를 제공하며,
   전체 `$id` URL보다 간결하고 의미적으로 명확합니다.

### 왜 `$id`와 `name`을 둘 다 쓰는가?

| Field  | Role                                                    | Format                 |
| ------ | ------------------------------------------------------- | ---------------------- |
| `$id`  | `$ref` 해석과 툴링을 위한 JSON Schema 기본 식별자       | URI (스펙상 필수)      |
| `name` | 레지스트리 키이자 안정적 식별자                         | 역도메인               |

JSON Schema 스펙에 따라 `$id`는 유효한 URI여야 합니다.
`name`은 **레지스트리(`capabilities`, `services`, `payment_handlers`)에서 사용하는 키**이며,
capability 협상에서 wire protocol 식별자로 사용됩니다.
즉, 인프라 변화에 따라 `schema` URL이 바뀌더라도 식별 체계는 분리되어 유지됩니다.

역도메인 형식은 **네임스페이스 거버넌스**를 제공합니다.
도메인 소유자가 자신의 네임스페이스(`dev.ucp.*`, `com.shopify.*`)를 통제해
UCP 엔터티와 벤더 엔터티 간 충돌을 피할 수 있습니다.
이 안정적인 식별 계층 덕분에,
향후 검증 가능한 자격증명, content-addressed 스키마 등으로
신뢰·해석 메커니즘이 진화해도 capability 협상은 깨지지 않습니다.

### 왜 `version`에 날짜를 쓰는가?

`version` 필드는 날짜 기반 버전(`YYYY-MM-DD`)을 사용하여 다음을 가능하게 합니다.

- **Capability 협상**: 플랫폼이 지원하는 특정 버전을 요청
- **브레이킹 체인지 관리**: 새 버전은 새 날짜를 사용하고,
  기존 버전은 유효하고 해석 가능하게 유지
- **독립 릴리스 주기**: Extension이 자체 일정으로 릴리스 가능

## 스키마 카테고리

UCP 스키마는 프로토콜 내 역할에 따라 6개 카테고리로 구분됩니다.

### Capability 스키마

`ucp.capabilities{}` 레지스트리에 나타나는 협상 대상 capability를 정의합니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`, `name`, `version`
- **Variants**: `platform_schema`, `business_schema`, `response_schema`

예시: `checkout.json`, `fulfillment.json`, `discount.json`, `order.json`

### Service 스키마

`ucp.services{}` 레지스트리에 나타나는 전송 바인딩을 정의합니다.
각 전송(REST, MCP, A2A, Embedded)은 별도 엔트리입니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`, `name`, `version`
- **Variants**: `platform_schema`, `business_schema`
- **전송별 요구사항**:
    - REST/MCP: `endpoint`, `schema` (OpenAPI/OpenRPC URL)
    - A2A: `endpoint` (Agent Card URL)
    - Embedded: `schema` (OpenRPC URL)

### Payment Handler 스키마

`ucp.payment_handlers{}` 레지스트리의 payment handler 구성을 정의합니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`, `name`, `version`
- **Variants**: `platform_schema`, `business_schema`, `response_schema`
- **인스턴스 `id`**: 동일 handler의 다중 구성을 구분하기 위해 필수

예시: `com.google.pay`, `dev.shopify.shop_pay`, `dev.ucp.processor_tokenizer`

**→ Handler 구조, config/instrument/credential 스키마, 전체 명세 템플릿은**
**[Payment Handler Guide](../specification/payment-handler-guide.md)**를 참고하세요.

### Component 스키마

Capability 내부에 포함되는 데이터 구조이며 독립 협상 대상이 아닙니다.
레지스트리에 나타나지 않습니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`
- **생략**: `name`, `version` (독립 버전 대상 아님)

예시:

- `schemas/shopping/payment.json` — Payment 구성(Checkout의 일부)

### Type 스키마

다른 스키마가 재사용하는 정의입니다. 레지스트리에 나타나지 않습니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`
- **생략**: `name`, `version`

예시: `types/buyer.json`, `types/line_item.json`, `types/postal_address.json`

### Meta 스키마

엔터티 payload가 아니라 프로토콜 구조 자체를 정의합니다.

- **Top-level fields**: `$schema`, `$id`, `title`, `description`
- **생략**: `name`, `version`

예시: `ucp.json` (entity base), `capability.json`, `service.json`, `payment_handler.json`

## 레지스트리 패턴

UCP는 capability, service, handler를
**`name`을 키로 가지는 객체 레지스트리**로 구성합니다.
(`name` 필드가 포함된 객체 배열을 기본 구조로 쓰지 않음)

```json
{
  "capabilities": {
    "dev.ucp.shopping.checkout": [{"version": "2026-01-11"}],
    "dev.ucp.shopping.fulfillment": [{"version": "2026-01-11"}]
  },
  "services": {
    "dev.ucp.shopping": [
      {"version": "2026-01-11", "transport": "rest"},
      {"version": "2026-01-11", "transport": "mcp"}
    ]
  },
  "payment_handlers": {
    "com.google.pay": [{"id": "gpay_1234", "version": "2026-01-11"}]
  }
}
```

### 레지스트리 컨텍스트

동일한 레지스트리 구조가 3개 컨텍스트에서 재사용되며,
각 컨텍스트별 필수 필드가 다릅니다.

| Context | Location | Required Fields |
| ------- | -------- | --------------- |
| Platform Profile | 공지된 URI | `version`, `spec`, `schema` |
| Business Profile | `/.well-known/ucp` | `version`; 필요 시 `config` 추가 |
| API Responses | Checkout/order payload | `version` (+ handlers의 경우 `id`) |

## 엔터티 패턴

모든 capability, service, handler는 공통 `entity` 베이스 스키마를 확장합니다.

| Field | Type | Description |
| ----- | ---- | ----------- |
| `version` | string | 엔터티 버전(`YYYY-MM-DD`) — 항상 필수 |
| `spec` | URI | 사람이 읽을 수 있는 명세 문서 |
| `schema` | URI | JSON Schema URL |
| `id` | string | 인스턴스 식별자(handlers 전용) |
| `config` | object | 엔터티별 설정 |

### 스키마 변형(Variants)

각 엔터티 타입은 컨텍스트별로 **3가지 변형**을 정의합니다.

**`platform_schema`** — discovery용 전체 선언

```json
{
  "dev.ucp.shopping.fulfillment": [{
    "version": "2026-01-11",
    "spec": "https://ucp.dev/specification/fulfillment",
    "schema": "https://ucp.dev/schemas/shopping/fulfillment.json",
    "config": {
      "supports_multi_group": true
    }
  }]
}
```

**`business_schema`** — 비즈니스별 오버라이드

```json
{
  "dev.ucp.shopping.fulfillment": [{
    "version": "2026-01-11",
    "config": {
      "allows_multi_destination": {"shipping": true}
    }
  }]
}
```

**`response_schema`** — API 응답용 최소 참조

```json
{
  "ucp": {
    "capabilities": {
      "dev.ucp.shopping.fulfillment": [{"version": "2026-01-11"}]
    }
  }
}
```

스키마의 `$defs`에 세 변형을 모두 정의하세요.

```json
"$defs": {
  "platform_schema": {
    "allOf": [{"$ref": "../capability.json#/$defs/platform_schema"}]
  },
  "business_schema": {
    "allOf": [{"$ref": "../capability.json#/$defs/business_schema"}]
  },
  "response_schema": {
    "allOf": [{"$ref": "../capability.json#/$defs/response_schema"}]
  }
}
```

## 버전 전략

### UCP Capability (`dev.ucp.*`)

UCP가 작성한 capability는 기본적으로 프로토콜 릴리스와 함께 버전이 올라갑니다.
필요 시 개별 capability가 독립 버전으로 분리될 **may** 가능성도 있습니다.

### Vendor Capability (`com.{vendor}.*`)

`dev.ucp.*` 외 capability는 완전히 독립적으로 버전 관리합니다.

```json
{
  "name": "com.shopify.loyalty",
  "version": "2025-09-01",
  "spec": "https://shopify.dev/ucp/loyalty",
  "schema": "https://shopify.dev/ucp/schemas/loyalty.json"
}
```

Vendor 스키마도 동일한 self-describing 요구사항을 따라야 합니다.

## 완전한 예시: Capability 스키마

Capability 스키마는 payload 구조와 선언 변형을 함께 정의합니다.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ucp.dev/schemas/shopping/checkout.json",
  "name": "dev.ucp.shopping.checkout",
  "version": "2026-01-11",
  "title": "Checkout",
  "description": "Base checkout schema. Extensions compose via allOf.",

  "$defs": {
    "platform_schema": {
      "allOf": [{"$ref": "../capability.json#/$defs/platform_schema"}]
    },
    "business_schema": {
      "allOf": [{"$ref": "../capability.json#/$defs/business_schema"}]
    },
    "response_schema": {
      "allOf": [{"$ref": "../capability.json#/$defs/response_schema"}]
    }
  },

  "type": "object",
  "required": ["ucp", "id", "line_items", "status", "currency", "totals", "links"],
  "properties": {
    "ucp": {"$ref": "../ucp.json#/$defs/response_checkout_schema"},
    "id": {"type": "string", "description": "Checkout identifier"},
    "line_items": {"type": "array", "items": {"$ref": "types/line_item.json"}},
    "status": {"type": "string", "enum": ["open", "completed", "expired"]},
    "currency": {"type": "string", "pattern": "^[A-Z]{3}$"},
    "totals": {"$ref": "types/totals.json"},
    "links": {"$ref": "types/links.json"}
  }
}
```

핵심 요점:

- **Top-level `name`, `version`**으로 스키마를 self-describing하게 유지
- **`$defs` variants**로 컨텍스트별 검증 지원
- **Payload properties**로 실제 checkout 응답 구조 정의
