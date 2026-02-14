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

# Universal Commerce Protocol (UCP) 공식 명세

## 상위 가이드라인

이 문서의 **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, **OPTIONAL** 키워드는
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html){ target="_blank" } 및
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174.html){ target="_blank" } 정의를 따릅니다.

스키마 참고:

- 날짜 형식: 별도 명시가 없으면
  [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339.html){ target="_blank" } 사용
- 금액 형식: 소수 단위(minor units, cents)

## Discovery, 거버넌스, 협상

UCP는 server-selects 아키텍처를 채택합니다. business(서버)가 양측 capability 교집합에서
프로토콜 버전과 capability를 선택합니다. business/platform 프로필은 양측에서 캐시될 수 있어
표준 요청/응답 흐름 안에서 효율적인 capability 협상이 가능합니다.

### 네임스페이스 거버넌스

UCP는 reverse-domain 네이밍으로 capability 식별자에 거버넌스 권한을 직접 인코딩합니다.
이를 통해 중앙 레지스트리 의존성을 줄입니다.

#### 네이밍 규칙

모든 capability 및 service 이름은 다음 형식을 **반드시(MUST)** 따라야 합니다.

```text
{reverse-domain}.{service}.{capability}
```

**구성요소:**

- `{reverse-domain}` - 도메인 소유권 기반 권한 식별자
- `{service}` - 서비스/버티컬 분류(예: `shopping`, `common`)
- `{capability}` - 구체 capability 이름

**예시:**

| 이름                                | 권한 주체   | 서비스   | Capability       |
| ----------------------------------- | ----------- | -------- | ---------------- |
| `dev.ucp.shopping.checkout`         | ucp.dev     | shopping | checkout         |
| `dev.ucp.shopping.fulfillment`      | ucp.dev     | shopping | fulfillment      |
| `dev.ucp.common.identity_linking`   | ucp.dev     | common   | identity_linking |
| `com.example.payments.installments` | example.com | payments | installments     |

#### Spec URL 바인딩

모든 capability에는 `spec` 및 `schema` 필드가 **필수(REQUIRED)** 입니다.
이 URL들의 origin은 네임스페이스 권한과 **일치해야 합니다(MUST)**.

| 네임스페이스    | 필수 Origin               |
| --------------- | ------------------------- |
| `dev.ucp.*`     | `https://ucp.dev/...`     |
| `com.example.*` | `https://example.com/...` |

Platform은 이 바인딩을 **검증해야 하며(MUST)**,
spec origin이 네임스페이스 권한과 맞지 않는 capability는 **거부하는 것이 권장됩니다(SHOULD)**.

#### 거버넌스 모델

| 네임스페이스 패턴 | 권한 주체    | 거버넌스 주체       |
| ----------------- | ------------ | ------------------- |
| `dev.ucp.*`       | ucp.dev      | UCP 거버넌스 기구   |
| `com.{vendor}.*`  | {vendor}.com | 벤더 조직           |
| `org.{org}.*`     | {org}.org    | 일반 조직           |

`dev.ucp.*` 네임스페이스는 UCP 거버넌스 기구가 승인한 capability 전용입니다.
벤더는 커스텀 capability에 대해 자신의 reverse-domain 네임스페이스를 **반드시(MUST)** 사용해야 합니다.

### 서비스

**service**는 버티컬(shopping, common 등)의 API 표면을 정의합니다.
service에는 표준 형식으로 정의된 연산, 이벤트, 전송 바인딩이 포함됩니다.

- **REST**: OpenAPI 3.x (JSON 형식)
- **MCP**: OpenRPC (JSON 형식)
- **A2A**: Agent Card 명세
- **EP(embedded)**: OpenRPC (JSON 형식)

#### 서비스 정의

| 필드              | 타입   | 필수 여부 | 설명                                |
| ----------------- | ------ | --------- | ----------------------------------- |
| `version`         | string | Yes       | 서비스 버전(YYYY-MM-DD)            |
| `spec`            | string | Yes       | 서비스 문서 URL                     |
| `rest`            | object | No        | REST 전송 바인딩                    |
| `rest.schema`     | string | Yes       | OpenAPI 명세 URL(JSON)              |
| `rest.endpoint`   | string | Yes       | Business REST 엔드포인트            |
| `mcp`             | object | No        | MCP 전송 바인딩                     |
| `mcp.schema`      | string | Yes       | OpenRPC 명세 URL(JSON)              |
| `mcp.endpoint`    | string | Yes       | Business MCP 엔드포인트             |
| `a2a`             | object | No        | A2A 전송 바인딩                     |
| `a2a.endpoint`    | string | Yes       | Business A2A Agent Card URL         |
| `embedded`        | string | No        | Embedded 전송 바인딩                |
| `embedded.schema` | string | Yes       | OpenRPC 명세 URL(JSON)              |

전송 정의는 **얇게(thin)** 유지되어야 하며(**MUST**), 메서드명 선언과 기본 스키마 참조만 포함해야 합니다.
자세한 내용은 [요구사항](#requirements)을 참고하세요.

#### 엔드포인트 해석

`endpoint` 필드는 API 호출의 base URL을 제공합니다.
OpenAPI 경로는 이 endpoint에 덧붙여 최종 URL을 구성합니다.

**예시:**

```json
{
  "version": "2026-01-11",
  "transport": "rest",
  "schema": "https://ucp.dev/services/shopping/openapi.json",
  "endpoint": "https://business.example.com/api/v2"
}
```

OpenAPI 경로가 `/checkout-sessions`일 때 해석된 URL은 다음과 같습니다.

```text
POST https://business.example.com/api/v2/checkout-sessions
```

**규칙:**

- `endpoint`는 스킴(https)을 포함한 유효 URL이어야 합니다(**MUST**).
- `endpoint`는 trailing slash를 포함하지 않아야 합니다(**SHOULD NOT**).
- OpenAPI 경로는 상대 경로이며 endpoint 뒤에 직접 붙습니다.
- 동일한 해석 규칙이 MCP JSON-RPC endpoint에도 적용됩니다.
- A2A 전송의 `endpoint`는 해당 agent의 Agent Card URL을 가리킵니다.

### 기능(Capability)

**capability**는 서비스 내부 기능 단위이며, 지원 기능과 문서/스키마 위치를 선언합니다.

#### 기능(Capability) 정의

{{ extension_schema_fields('capability.json#/$defs/platform_schema', 'capability-schema') }}

#### 확장(Extensions)

**extension**은 다른 capability를 확장하는 선택 모듈입니다.
`extends` 필드로 상위 capability를 선언합니다.

```json
{
  "dev.ucp.shopping.fulfillment": [
    {
      "version": "2026-01-23",
      "spec": "https://ucp.dev/2026-01-23/specification/fulfillment",
      "schema": "https://ucp.dev/2026-01-23/schemas/shopping/fulfillment.json",
      "extends": "dev.ucp.shopping.checkout"
    }
  ]
}
```

##### 다중 부모 확장

확장은 배열 형식으로 여러 상위 capability를 확장할 수 있습니다(**MAY**).

```json
{
  "dev.ucp.shopping.discount": [
    {
      "version": "2026-01-23",
      "spec": "https://ucp.dev/2026-01-23/specification/discount",
      "schema": "https://ucp.dev/2026-01-23/schemas/shopping/discount.json",
      "extends": ["dev.ucp.shopping.checkout", "dev.ucp.shopping.cart"]
    }
  ]
}
```

확장이 여러 상위를 선언한 경우:

- 확장은 각 상위 capability별로 서로 다른 필드를 정의할 수 있습니다(**MAY**).
  (예: checkout용 `loyalty_earned`, cart용 `loyalty_preview`)
- 협상 규칙은 [교집합 알고리즘](#intersection-algorithm)을 참고하세요.

확장 유형 예:

- **공식 확장**: `dev.ucp.shopping.fulfillment` → `dev.ucp.shopping.checkout` 확장
- **벤더 확장**: `com.example.installments` → `dev.ucp.shopping.checkout` 확장

### 스키마 조합

확장은 새 필드를 추가하고 공유 구조를 수정할 수 있습니다.
(예: discount는 `totals`를 수정하고 fulfillment는 `totals.type`에 fulfillment를 추가)

#### 요구사항 { #requirements }

- 전송 정의(OpenAPI/OpenRPC)는 기본 스키마만 참조해야 합니다(**MUST**).
  인라인으로 필드 나열이나 payload shape 정의를 해서는 안 됩니다(**MUST NOT**).
- 확장은 자기 기술적(self-describing)이어야 합니다(**MUST**).
  각 확장 스키마는 `allOf` 조합을 통해 도입 타입과 기본 타입 수정 방식을 명시해야 합니다(**MUST**).
- Platform은 기본 스키마와 활성 확장 스키마를 조회·조합해 클라이언트 측에서 스키마를 해석해야 합니다(**MUST**).

#### 확장 스키마 패턴

확장 스키마는 `allOf`를 이용해 조합 타입을 정의합니다.
`$defs` 키는 결정적 스키마 해석을 위해 상위 capability의 전체 이름(reverse-domain)을 사용해야 합니다(**MUST**).

```json
{
  "$defs": {
    "discounts_object": { ... },
    "dev.ucp.shopping.checkout": {
      "title": "Checkout with Discount",
      "allOf": [
        {"$ref": "checkout.json"},
        {
          "type": "object",
          "properties": {
            "discounts": {
              "$ref": "#/$defs/discounts_object"
            }
          }
        }
      ]
    }
  }
}
```

**요구사항:**

- 확장 스키마는 `extends`에 선언한 각 상위마다 `$defs` 항목을 가져야 합니다(**MUST**).
- `$defs` 키는 상위의 전체 capability 이름과 정확히 일치해야 합니다(**MUST**).

이 규약의 효과:

- **자기 기술성**: 어떤 상위를 확장하는지 스키마가 직접 선언
- **결정적 해석**: `extends` 값이 `$defs` 키에 직접 매핑
- **검증 가능성**: 빌드 시 각 `extends` 항목의 `$defs` 대응 여부를 확인 가능

#### 스키마 해석 규약 { #schema-resolution-convention }

payload 검증을 위해 구현체는 다음 순서로 확장 스키마를 해석합니다.

1. 연산에서 루트 capability를 결정합니다.
   (예: checkout 연산은 `dev.ucp.shopping.checkout`)
2. 각 활성 확장에 대해 `$defs[{root_capability}]`를 해석·적용합니다.

**예시:** checkout 응답에 discount 확장이 포함된 경우

- 루트 capability: `dev.ucp.shopping.checkout`
- 확장 스키마: `discount.json`
- 해석 대상: `discount.json#/$defs/dev.ucp.shopping.checkout`

#### 해석 흐름 { #resolution-flow }

Platform은 다음 순서로 스키마를 해석해야 합니다(**MUST**).

1. **Discovery**: `/.well-known/ucp`에서 business profile 조회
2. **Negotiation**: capability 교집합 계산
   ([교집합 알고리즘](#intersection-algorithm) 참고)
3. **Schema Fetch**: 기본 스키마 및 활성 확장 스키마 조회
4. **Compose**: 활성 확장 기준으로 `allOf` 체인 병합
5. **Validate**: 조합된 스키마로 요청/응답 검증

### 프로필 구조

#### Business 프로필

Business는 `/.well-known/ucp`에 profile을 게시합니다. 예시는 다음과 같습니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "services": {
      "dev.ucp.shopping": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "rest",
          "endpoint": "https://business.example.com/ucp/v1",
          "schema": "https://ucp.dev/services/shopping/openapi.json"
        },
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "mcp",
          "endpoint": "https://business.example.com/ucp/mcp",
          "schema": "https://ucp.dev/services/shopping/mcp.openrpc.json"
        },
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "a2a",
          "endpoint": "https://business.example.com/.well-known/agent-card.json"
        },
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "embedded",
          "schema": "https://ucp.dev/services/shopping/embedded.openrpc.json"
        }
      ]
    },
    "capabilities": {
      "dev.ucp.shopping.checkout": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/checkout",
          "schema": "https://ucp.dev/schemas/shopping/checkout.json"
        }
      ],
      "dev.ucp.shopping.fulfillment": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/fulfillment",
          "schema": "https://ucp.dev/schemas/shopping/fulfillment.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ],
      "dev.ucp.shopping.discount": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/discount",
          "schema": "https://ucp.dev/schemas/shopping/discount.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ]
    },
    "payment_handlers": {
      "com.example.processor_tokenizer": [
        {
          "id": "processor_tokenizer",
          "version": "2026-01-11",
          "spec": "https://example.com/specs/payments/processor_tokenizer",
          "schema": "https://example.com/specs/payments/merchant_tokenizer.json",
          "config": {
            "type": "CARD",
            "tokenization_specification": {
              "type": "PUSH",
              "parameters": {
                "token_retrieval_url": "https://api.psp.example.com/v1/tokens"
              }
            }
          }
        }
      ]
    }
  },
  "signing_keys": [
    {
      "kid": "business_2025",
      "kty": "EC",
      "crv": "P-256",
      "x": "WbbXwVYGdJoP4Xm3qCkGvBRcRvKtEfXDbWvPzpPS8LA",
      "y": "sP4jHHxYqC89HBo8TjrtVOAGHfJDflYxw7MFMxuFMPY",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

`ucp` 객체는 버전, services, capabilities, payment handlers 등 프로토콜 메타데이터를 담습니다.
`signing_keys` 배열은 webhook 및 기타 인증 메시지의 서명 검증에 쓰이는 공개키(JWK 형식)를 포함합니다.

#### Platform 프로필

Platform profile도 유사한 구조이며, 암호학적 검증이 필요한 capability를 위해 서명 키를 포함합니다.
capability는 capability별 설정(예: callback URL, feature flag)을 위한 `config` 객체를 포함할 수 있습니다(**MAY**).
예시는 다음과 같습니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "services": {
      "dev.ucp.shopping": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "rest",
          "schema": "https://ucp.dev/services/shopping/openapi.json"
        }
      ]
    },
    "capabilities": {
      "dev.ucp.shopping.checkout": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/checkout",
          "schema": "https://ucp.dev/schemas/shopping/checkout.json"
        }
      ],
      "dev.ucp.shopping.fulfillment": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/fulfillment",
          "schema": "https://ucp.dev/schemas/shopping/fulfillment.json",
          "extends": "dev.ucp.shopping.checkout"
        }
      ],
      "dev.ucp.shopping.order": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/order",
          "schema": "https://ucp.dev/schemas/shopping/order.json",
          "config": {
            "webhook_url": "https://platform.example.com/webhooks/ucp/orders"
          }
        }
      ]
    },
    "payment_handlers": {
      "com.google.pay": [
        {
          "id": "gpay_1234",
          "version": "2024-12-03",
          "spec": "https://developers.google.com/merchant/ucp/guides/gpay-payment-handler",
          "schema": "https://pay.google.com/gp/p/ucp/2026-01-11/schemas/gpay_config.json"
        }
      ],
      "dev.shopify.shop_pay": [
        {
          "id": "shop_pay_1234",
          "version": "2026-01-11",
          "spec": "https://shopify.dev/ucp/shop-pay-handler",
          "schema": "https://shopify.dev/ucp/schemas/shop-pay-config.json"
        }
      ],
      "dev.ucp.processor_tokenizer": [
        {
          "id": "processor_tokenizer",
          "version": "2026-01-11",
          "spec": "https://example.com/specs/payments/processor_tokenizer-payment",
          "schema": "https://ucp.dev/schemas/payments/delegate-payment.json"
        }
      ]
    }
  },
  "signing_keys": [
    {
      "kid": "platform_2025",
      "kty": "EC",
      "crv": "P-256",
      "x": "MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4",
      "y": "4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM",
      "use": "sig",
      "alg": "ES256"
    }
  ]
}
```

### 요청 기반 플랫폼 광고

Platform은 capability 협상을 위해 각 요청에 profile URI를 전달해야 합니다(**MUST**).

**HTTP 전송:** Platform은 `UCP-Agent` 헤더에
Dictionary Structured Field 문법([RFC 8941](https://datatracker.ietf.org/doc/html/rfc8941){ target="_blank" })
을 사용해야 합니다(**MUST**).

```text
POST /checkout HTTP/1.1
UCP-Agent: profile="https://agent.example/profiles/shopping-agent.json"
Content-Type: application/json

{"line_items": [...]}
```

**MCP 전송:** Platform은 요청 메타데이터를 담은 `meta` 객체를 포함해야 합니다(**MUST**).

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://agent.example/profiles/shopping-agent.json"
        }
      },
      "checkout": {
        "line_items": [...]
      }
    }
  },
  "id": 1
}
```

### 협상 프로토콜 { #negotiation-protocol }

#### Platform 요구사항

1. **프로필 광고**: Platform은 전송 방식에 맞는 메커니즘으로 모든 요청에 profile URI를 포함해야 합니다(**MUST**).
2. **Discovery**: Platform은 요청 시작 전 `/.well-known/ucp`에서 business profile을 조회할 수 있습니다(**MAY**).
   조회했다면 HTTP cache-control 지시에 따라 캐시하는 것이 권장됩니다(**SHOULD**).
3. **네임스페이스 검증**: Platform은 capability `spec` URI origin이 네임스페이스 권한과 일치하는지 검증해야 합니다(**MUST**).
4. **스키마 해석**: Platform은 요청 전에 협상된 capability의 스키마를 조회·조합해야 합니다(**MUST**).

#### Business 요구사항

1. **프로필 해석**: Business는 platform profile URI가 포함된 요청을 받으면 캐시가 없는 경우 profile을 조회·검증해야 합니다(**MUST**).
2. **Capability 교집합 계산**: Business는 platform과 business capability의 교집합을 계산해야 합니다(**MUST**).
3. **확장 검증**: 교집합에 상위 capability가 없는 확장은 제외해야 합니다(**MUST**).
4. **응답 요구사항**: Business는 모든 응답에 `ucp` 필드를 포함해야 하며 다음을 담아야 합니다(**MUST**).
   - `version`: 요청 처리에 사용한 UCP 버전
   - `capabilities`: 해당 응답에서 활성화된 capability 배열

#### 교집합 알고리즘 { #intersection-algorithm }

세션에서 어떤 capability가 활성화되는지는 다음 알고리즘으로 결정됩니다.

1. **교집합 계산**: 각 business capability에 대해, 동일 `name`의 platform capability가 있으면 결과에 포함합니다.
2. **고아 확장 제거**: `extends`가 설정되어 있지만 상위 capability가 교집합에 없는 capability를 제거합니다.
   - 단일 상위(`extends: "string"`): 해당 상위가 반드시 존재해야 함
   - 다중 상위(`extends: ["a", "b"]`): 상위 중 하나 이상 존재해야 함
3. **반복 제거**: 더 이상 제거할 항목이 없을 때까지 2단계를 반복합니다(전이적 확장 체인 처리).

최종 결과는 양측이 공통 지원하며 확장 의존성이 충족된 capability 집합입니다.

#### 오류 처리 { #error-handling }

UCP 협상 실패는 두 가지로 구분됩니다.

1. **Discovery 실패**: Business가 platform profile을 조회하거나 파싱하지 못함
2. **협상 실패**: profile은 유효하지만 capability 교집합이 비었거나 버전이 호환되지 않음

이 두 실패 유형은 처리 방식이 다릅니다.

- **Discovery 실패** → 선택적 `continue_url`을 포함한 전송 오류
- **협상 실패** → 선택적 `continue_url`을 포함한 UCP 응답

##### 오류 코드

**협상 오류:**

| 코드                        | 설명                                       | REST | MCP    |
| --------------------------- | ------------------------------------------ | ---- | ------ |
| `invalid_profile_url`       | profile URL 형식 오류/누락/해석 불가       | 400  | -32001 |
| `profile_unreachable`       | URL 해석은 되었으나 조회 실패(타임아웃/비2xx) | 424  | -32001 |
| `profile_malformed`         | 조회 콘텐츠가 유효 JSON이 아니거나 스키마 위반 | 422  | -32001 |
| `capabilities_incompatible` | 교집합에 호환 capability 없음              | 200  | result |
| `version_unsupported`       | platform UCP 버전 미지원                   | 200  | result |

**프로토콜 오류:**

| HTTP | 설명                                  | MCP    |
| ---- | ------------------------------------- | ------ |
| 401  | 인증 필요 또는 인증 정보 무효         | -32000 |
| 403  | 인증됨, 그러나 권한 부족              | -32000 |
| 409  | Idempotency 키가 다른 payload로 재사용됨 | -32000 |
| 429  | 요청 과다                             | -32000 |
| 500  | 예기치 않은 서버 오류                 | -32603 |
| 503  | 서버 일시적 처리 불가                 | -32000 |

MCP over HTTP에서는 HTTP 상태 코드가 1차 신호이고 JSON-RPC `error.code`는 2차 신호입니다.
두 전송 모두 429/503에 대해 `Retry-After`(REST) 또는 `error.data.retry_after`(MCP) 제공이 권장됩니다(**SHOULD**).

##### `continue_url` 필드

UCP 협상이 실패했을 때 `continue_url`은 웹 fallback 경로를 제공합니다.
Business는 상황에 가장 적합한 URL을 제공하는 것이 좋습니다(**SHOULD**).

- checkout 연산: cart 또는 checkout 페이지 링크
- catalog 연산: 상품 상세 또는 검색 결과 링크
- 최후 fallback: 스토어프런트 홈 링크

이를 통해 에이전트는 표준 웹 인터페이스로 유연하게 전환해 작업을 이어갈 수 있습니다.

##### 전송 바인딩

=== "REST"

    **Discovery 실패 (424):**

    ```http
    HTTP/1.1 424 Failed Dependency
    Content-Type: application/json

    {
      "code": "profile_unreachable",
      "content": "Unable to fetch agent profile: connection timeout",
      "continue_url": "https://merchant.com/cart"
    }
    ```

    **협상 실패 (200):**

    ```http
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {}
      },
      "messages": [
        {
          "type": "error",
          "code": "version_unsupported",
          "content": "UCP version 2024-01-01 is not supported",
          "severity": "requires_buyer_input"
        }
      ],
      "continue_url": "https://merchant.com"
    }
    ```

    **프로토콜 오류 - Rate Limit (429):**

    ```http
    HTTP/1.1 429 Too Many Requests
    Retry-After: 60
    ```

    **프로토콜 오류 - Unauthorized (401):**

    ```http
    HTTP/1.1 401 Unauthorized
    WWW-Authenticate: Bearer realm="ucp"
    ```

    프로토콜 오류는 표준 HTTP 상태 코드와 헤더를 사용합니다.
    응답 바디는 선택 사항입니다.

=== "MCP"

    **Discovery 실패 (JSON-RPC error):**

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "error": {
        "code": -32001,
        "message": "UCP discovery failed",
        "data": {
          "code": "profile_unreachable",
          "content": "Unable to fetch agent profile: connection timeout",
          "continue_url": "https://merchant.com/cart"
        }
      }
    }
    ```

    **협상 실패 (JSON-RPC result):**

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "structuredContent": {
          "ucp": {
            "version": "2026-01-11",
            "capabilities": {}
          },
          "messages": [
            {
              "type": "error",
              "code": "version_unsupported",
              "content": "UCP version 2024-01-01 is not supported",
              "severity": "requires_buyer_input"
            }
          ],
          "continue_url": "https://merchant.com"
        },
        "content": [
          {"type": "text", "text": "{\"ucp\":{...},\"messages\":[...],\"continue_url\":\"...\"}"}
        ]
      }
    }
    ```

    **프로토콜 오류 - Rate Limit (JSON-RPC error):**

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "error": {
        "code": -32000,
        "message": "Rate limit exceeded",
        "data": {
          "retry_after": 60
        }
      }
    }
    ```

    **프로토콜 오류 - Unauthorized (JSON-RPC error):**

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "error": {
        "code": -32000,
        "message": "Unauthorized"
      }
    }
    ```

    Streamable HTTP 전송을 사용할 때 서버는 JSON-RPC 오류와 함께
    대응 HTTP 상태 코드(예: rate limit의 `429`)를 반환해야 합니다(**MUST**).
    오류 유형의 1차 신호는 HTTP 상태 코드입니다.

#### 응답의 Capability 선언 { #capability-declaration-in-responses }

응답의 `capabilities` 레지스트리는 현재 활성 capability를 나타냅니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": {
      "dev.ucp.shopping.checkout": [
        {"version": "2026-01-11"}
      ],
      "dev.ucp.shopping.fulfillment": [
        {"version": "2026-01-11"}
      ]
    },
    "payment_handlers": {
      "com.example.processor_tokenizer": [
        {"id": "processor_tokenizer", "version": "2026-01-11"}
      ]
    }
  },
  "id": "checkout_123",
  "line_items": [...]
  ... other fields
}
```

#### 응답 Capability 선택 { #response-capability-selection }

Business는 `ucp.capabilities`에 아래 조건을 모두 만족하는 capability만 포함해야 합니다(**MUST**).

1. 해당 세션의 협상 교집합에 포함됨
2. 해당 응답의 연산 유형에 관련됨

**루트 Capability 관련성:**

루트 capability는 연산 유형과 일치할 때 관련성이 있습니다.

- `create_checkout` / `update_checkout` / `complete_checkout` →
    `dev.ucp.shopping.checkout`
- `create_cart` / `update_cart` → `dev.ucp.shopping.cart`
- Order webhooks → `dev.ucp.shopping.order`

**확장 관련성:**

확장은 `extends` 값 중 **하나 이상**이 관련 루트 capability와 일치할 때 관련성이 있습니다.

**선택 예시:**

| 응답 유형 | 포함                             | 미포함                       |
| --------- | -------------------------------- | ---------------------------- |
| Checkout  | checkout, discount, fulfillment  | cart, order                  |
| Cart      | cart, discount                   | checkout, fulfillment, order |
| Order     | order                            | checkout, cart, discount     |

## 결제 아키텍처

UCP는 **platform**, **business**, **결제 자격증명 제공자(payment credential provider)** 간의
"N 대 N" 통합 복잡성을 줄이기 위해 결제를 분리형 아키텍처로 설계했습니다.
이 설계는 **Payment Instruments**(무엇을 받는가)와
**Payment Handlers**(어떻게 처리하는가의 명세)를 분리해
보안성과 확장성을 확보합니다.

### 보안 및 신뢰 모델

결제 아키텍처는 "Trust-by-Design" 철학을 따릅니다.
business와 결제 자격증명 제공자 사이에는 신뢰 가능한 법적·기술적 관계가 있다고 가정하며,
platform(Client)은 원시 금융 자격증명에 직접 접근하지 않는 중개 계층(**SHOULD NOT**)으로 동작합니다.

#### 신뢰 삼각형

1. **Business ↔ 결제 자격증명 제공자:** 기존의 법적·기술적 관계가 존재하며, business는 API 키와 계약을 보유합니다.
2. **Platform ↔ 결제 자격증명 제공자:** Platform은 iframe/API 등으로 토큰화를 수행하지만 자금의 소유 주체는 아닙니다.
3. **Platform ↔ Business:** Platform은 결과물(토큰/mandate)을 business에 전달해 주문 확정을 돕습니다.

#### 자율 커머스를 위한 강화 보안

사용자 승인에 대한 암호학적 증명이 필요한 시나리오(예: 자율 AI 에이전트)를 위해,
UCP는 **AP2 Mandates Extension**(`dev.ucp.shopping.ap2_mandate`)을 지원합니다.
이 선택 확장은 검증 가능한 디지털 자격증명을 통해 부인 방지(non-repudiation) 수준의 승인을 제공합니다.

이 확장의 적용 시점과 방법은
[거래 무결성 및 부인 방지](#transaction-integrity-and-non-repudiation)와
[AP2 Mandates Extension](ap2-mandates.md)를 참고하세요.

#### 자격증명 흐름과 PCI 범위

규정 준수 비용(PCI-DSS)을 줄이기 위한 원칙:

1. **단방향 흐름:** 자격증명은 **Platform → Business** 방향으로만 이동합니다.
   Business는 응답에서 자격증명을 되돌려 보내면 안 됩니다(**MUST NOT**).
2. **불투명 자격증명:** Platform은 원시 PAN 대신 토큰(예: network token), 암호화 payload, mandate를 다룹니다.
3. **Handler ID 라우팅:** payload의 `handler_id`는 business가 어떤 제공자 키로 복호화/승인할지 정확히 식별하도록 하여 키 혼동 공격을 줄입니다.

### 역할과 책임: 누가 무엇을 구현하는가?

UCP 결제 모델에서 자주 헷갈리는 지점은 책임 분리입니다.
역할별 책임은 다음과 같습니다.

| 역할                             | 책임                          | 수행 내용                                                                                                                                                                                                                                                         |
| :------------------------------- | :---------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **결제 자격증명 제공자**         | **명세 정의**                 | **Handler Definition**을 작성합니다. 카드 토큰화 방식과 필요한 config 입력을 규정하는 "청사진"(JSON Schema)을 게시합니다.<br>*예: `'com.psp-x.tokenization' 핸들러 스키마를 제공`*                                                                              |
| **Business**                     | **핸들러 구성**               | 사용할 핸들러를 선택하고 UCP Checkout 응답에 **구체 구성값**(공개키, Merchant ID 등)을 제공합니다.<br>*예: `이 공개키로 'com.psp-x.tokenization' 기반 Visa 결제를 허용`*                                                                                         |
| **Platform**                     | **프로토콜 실행**             | Business config를 읽고, 결제 자격증명 제공자 명세의 로직을 실행해 토큰을 획득합니다.<br>*예: `Business가 지정한 SDK를 호출해 토큰 획득`*                                                                                                                        |

### Checkout 라이프사이클의 결제

결제가 필요한 경우 UCP 내 결제 흐름은
**Negotiation**, **Acquisition**, **Completion**의 3단계 라이프사이클을 따릅니다.

![상위 수준 결제 흐름 시퀀스 다이어그램](site:specification/images/ucp-payment-flow.png)

1. **Negotiation (Business → Platform):** Business는 UCP profile에 사용 가능한 payment handler를 광고합니다. Platform은 이를 통해 *어떻게 결제할지*를 파악합니다.
2. **Acquisition (Platform ↔ 결제 자격증명 제공자):** Platform이 핸들러 로직을 실행합니다. 보통 클라이언트/에이전트 측에서 직접 제공자와 통신해 자격증명을 토큰으로 교환합니다.
3. **Completion (Platform → Business):** Platform은 불투명 자격증명(토큰)을 business에 전달하고, business는 백엔드 결제 연동으로 자금 처리를 완료합니다.

### 결제 핸들러

Payment Handler는 **엔터티가 아니라 명세(specification)** 이며,
결제 수단을 어떻게 처리할지 정의하는 계약입니다.

**핵심 구분:**

- **Payment Credential Provider** = 참여 주체(예: Google Pay, Shop Pay)
- **Payment Handler** = 해당 주체가 작성한 명세(예: `com.google.pay`, `dev.shopify.shop_pay`)

Payment handler를 통해 network token을 포함한 다양한 결제 수단과 토큰 타입을 지원할 수 있습니다.
일반적으로 결제 자격증명 제공자 또는 UCP 거버넌스가 이 표준 정의를 작성합니다.

**동적 필터링:** Business는 cart 문맥에 따라 `handlers` 목록을 필터링해야 합니다(**MUST**).
(예: 구독 상품에서 BNPL 제거, 배송지 기반 지역 결제수단 필터링)

### 위험 신호(Risk Signals)

사기 평가를 돕기 위해 Platform은 `complete` 호출에 추가 risk signal을 포함할 수 있습니다(**MAY**).
이를 통해 business는 거래 정당성에 대한 더 많은 문맥을 확보합니다.
risk signal 구조/내용은 본 명세에서 엄격히 고정하지 않아,
Platform-Business 간 합의나 핸들러 요구사항에 따라 유연하게 구성할 수 있습니다.

**예시(유연한 구조):**

```json
{
  "risk_signals": {
    "session_id": "abc_123_xyz",
    "score": 0.95,
  }
}
```

### 구현 시나리오

다음 시나리오는 서로 다른 payment handler와 결제 수단이
실제 데이터 예시에서 어떻게 협상되고 실행되는지 보여줍니다.

#### 시나리오 A: 디지털 월렛

이 시나리오에서 platform은 결제 자격증명 제공자(예: `com.google.pay`, `dev.shopify.shop_pay`)를 식별하고,
해당 API를 호출해 암호화 결제 토큰을 획득합니다.

##### 1. Business 광고(Create Checkout 응답)

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.google.pay": [
        {
          "id": "8c9202bd-63cc-4241-8d24-d57ce69ea31c",
          "version": "2026-01-11",
          "config": {
            "api_version": 2,
            "api_version_minor": 0,
            "environment": "TEST",
            "merchant_info": {
              "merchant_name": "Example Merchant",
              "merchant_id": "01234567890123456789",
              "merchant_origin": "checkout.merchant.com"
            },
            "allowed_payment_methods": [
              {
                "type": "CARD",
                "parameters": {
                  "allowed_auth_methods": ["PAN_ONLY"],
                  "allowed_card_networks": ["VISA", "MASTERCARD"]
                },
                "tokenization_specification": {
                  "type": "PAYMENT_GATEWAY",
                  "parameters": {
                    "gateway": "example",
                    "gatewayMerchantId": "exampleGatewayMerchantId"
                  }
                }
              }
            ]
          }
        }
      ],
      "dev.shopify.shop_pay": [
        {
          "id": "shop_pay_1234",
          "version": "2026-01-11",
          "config": {
            "shop_id": "shopify-559128571",
            "environment": "production"
          }
        }
      ]
    }
  }
}
```

##### 2. 토큰 실행(Platform 측)

Platform은 `com.google.pay` 또는 `dev.shopify.shop_pay`를 인식하고,
해당 handler API에 `config`를 전달합니다. Handler는 암호화 토큰 데이터를 반환합니다.

##### 3. Complete Checkout(Business 요청)

Platform은 payment handler 응답을 payment instrument로 감싸 전달합니다.

```json
POST /checkout-sessions/{id}/complete

{
  "payment": {
    "instruments": [
      {
        "id": "pm_1234567890abc",
        "handler_id": "8c9202bd-63cc-4241-8d24-d57ce69ea31c",
        "type": "card",
        "selected": true,
        "display": {
          "brand": "visa",
          "last_digits": "4242"
        },
        "billing_address": {
          "street_address": "123 Main Street",
          "extended_address": "Suite 400",
          "address_locality": "Charleston",
          "address_region": "SC",
          "postal_code": "29401",
          "address_country": "US",
          "first_name": "Jane",
          "last_name": "Smith"
        },
        "credential": {
          "type": "PAYMENT_GATEWAY",
          "token": "{\"signature\":\"...\",\"protocolVersion\":\"ECv2\"...}"
        }
      }
    ]
  },
  "risk_signals": {
      // ...
  }
}
```

#### 시나리오 B: 챌린지(SCA) 기반 직접 토큰화

이 시나리오에서 platform은 범용 tokenizer로 세션 토큰 또는 network token을 요청합니다.
은행이 Strong Customer Authentication(SCA/3DS)을 요구하면,
business는 completion을 일시 중단하고 챌린지를 요구합니다.

##### 1. Business 광고

```json
{
  "ucp": {
    "payment_handlers": {
      "com.example.tokenizer": [
        {
          "id": "merchant_tokenizer",
          "version": "2026-01-11",
          "spec": "https://example.com/specs/tokenizer",
          "schema": "https://example.com/schemas/tokenizer.json",
          "config": {
            "token_url": "https://api.psp.com/tokens",
            "public_key": "pk_123"
          }
        }
      ]
    }
  }
}
```

##### 2. 토큰 실행(Platform 측)

Platform은 `https://api.psp.com/tokens`를 호출하고 `tok_visa_123`을 수신합니다.
해당 제공자와의 신원·법적 연계는 사전에 정립되어 있어야 합니다(**SHOULD**).
`tok_visa_123`은 vault 카드 또는 network token을 표현할 수 있습니다.

##### 3. Complete Checkout(Business 요청)

```json
POST /checkout-sessions/{id}/complete

{
  "payment": {
    "instruments": [
      {
        "handler_id": "merchant_tokenizer",
        // ... more instrument required field
        "credential": { "token": "tok_visa_123" }
      }
    ]
  },
  "risk_signals": {
    // ... host could send risk_signals here
  }
}
```

##### 4. 챌린지 필요(Business 응답)

Business가 승인 시도를 수행하지만 PSP가 3DS가 필요한 "Soft Decline"을 반환합니다.

```json
HTTP/1.1 200 OK
{
  "status": "requires_escalation",
  "messages": [{
    "type": "error",
    "code": "requires_3ds",
    "content": "bank requires verification.",
    "severity": "requires_buyer_input"
  }],
  "continue_url": "https://psp.com/challenge/123"
}
```

*Platform은 이제 `continue_url`을 WebView/Window로 열어
사용자가 은행 인증을 완료하도록 한 뒤 completion을 재시도해야 합니다(**MUST**).*

#### 시나리오 C: 자율 에이전트(AP2)

이 시나리오는 **에이전트 권장 흐름**을 보여줍니다.
세션 토큰 대신 에이전트가 암호학적 mandate를 생성합니다.

##### 1. Business 광고

```json
{
  "ucp": {
    "payment_handlers": {
      "dev.ucp.ap2_mandate_compatible_handlers": [
        {
          "id": "ap2_234352",
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specs/ap2-handler",
          "schema": "https://ucp.dev/schemas/ap2-handler.json"
        }
      ]
    }
  }
}
```

##### 2. 에이전트 실행

에이전트는 비에이전트 표면(non-agentic surface)에서 사용자 개인키로 객체를 서명합니다.

##### 3. Complete Checkout

```json
POST /checkout-sessions/{id}/complete

{
  "payment": {
    "instruments": [
      {
        "handler_id": "ap2_234352",
        // other required instruments fields
        "credential": {
          "type": "card",
          "token": "eyJhbGciOiJ...", // Token would contain payment_mandate, the signed proof of funds auth
        }
      }
    ]
  },
  "risk_signals": {
    "session_id": "abc_123_xyz",
    "score": 0.95
  },
  "ap2": {
    "checkout_mandate": "eyJhbGciOiJ...", // Signed proof of checkout terms
  }
}
```

*이를 통해 business는 해당 거래에 대한 사용자 승인 사실을 부인 방지 형태로 확보할 수 있으며,
안전한 자율 처리 기반을 갖게 됩니다.*

### PCI-DSS 범위 관리

#### Platform 범위

대부분의 platform 구현은 다음 방식으로 **PCI-DSS 범위를 회피**할 수 있습니다.

- 불투명 자격증명(암호화 데이터, 토큰 참조 등)을 제공하는 handler 사용
- 원시 결제 데이터(카드번호, CVV 등)를 조회/저장하지 않음
- 자격증명을 직접 사용 가능한 형태로 보유하지 않고 전달만 수행
- 원시 자격증명이 platform을 통과하지 않는 PSP 토큰화 handler 사용

#### Business 범위

Business는 다음 방식으로 PCI 범위를 최소화할 수 있습니다.

- 제공자 호스팅 토큰화 사용(자격증명은 제공자가 저장, business는 토큰 참조만 수신)
- 암호화 자격증명을 제공하는 wallet provider 활용(Google Pay, Shop Pay)
- 원시 자격증명 로그 금지
- PCI 인증 제공자에게 자격증명 처리를 위임

#### 결제 자격증명 제공자 범위

결제 자격증명 제공자(PSP, wallet)는 보통 PCI-DSS Level 1 인증을 보유하며 다음을 처리합니다.

- 원시 자격증명 수집
- 자격증명 보호(토큰화, 암호화, 안전 저장)
- 자격증명 검증 및 처리
- PCI 준수 인프라 운영

### 보안 모범 사례

**Business 권장사항:**

1. 처리 전 `handler_id` 검증(광고된 집합 내 핸들러인지 확인)
2. TEST/PRODUCTION 환경별 PSP 자격증명 분리
3. 결제 처리 멱등성 구현(중복 과금 방지)
4. 자격증명 제외 결제 이벤트 로깅
5. 적절한 자격증명 타임아웃 설정
6. 암호학적 증명이 필요한 자율 커머스 시나리오에서는
   `dev.ucp.shopping.ap2_mandate` 확장 지원 고려
   ([AP2 Mandates Extension](ap2-mandates.md) 참고)

**Platform 권장사항:**

1. checkout API 호출에 항상 HTTPS 사용
2. 프로토콜 실행 전 handler config 검증
3. 자격증명 획득 타임아웃 처리 구현
4. 제출 후 메모리에서 자격증명 제거
5. 자격증명 만료를 우아하게 처리(필요 시 재획득)
6. 자율 에이전트 시나리오에서는 승인 증명을 위해
   `dev.ucp.shopping.ap2_mandate` 확장 사용 고려
   ([AP2 Mandates Extension](ap2-mandates.md) 참고)

**결제 자격증명 제공자 권장사항:**

1. 특정 business용 자격증명 보안 확보(암호화, 토큰화, 기타 handler별 방식)
2. 자격증명 획득 API 레이트리밋 적용
3. 자격증명 제공 전 platform 권한 검증
4. 합리적인 자격증명 만료 시간 설정(예: 토큰 15분, 시간 제한 암호화 payload)
5. 자격증명이 platform에서 직접 사용되지 않도록 보장(의도된 business만 사용)

### 사기 방지 통합

UCP 자체가 사기 방지 API를 정의하지는 않지만,
결제 아키텍처는 fraud signal 통합을 지원합니다.

- Business는 handler config에 추가 필드(예: 3DS 요구사항)를 요구할 수 있습니다.
- Platform은 자격증명과 함께 디바이스 지문/세션 데이터를 제출할 수 있습니다.
- 결제 자격증명 제공자는 자격증명 획득 단계에서 위험 평가를 수행할 수 있습니다.
- Business는 고위험 거래를 거절하고 추가 검증을 요청할 수 있습니다.

향후 확장에서 fraud signal 스키마를 표준화할 수 있지만(**MAY**),
현재 아키텍처만으로도 기존 사기 방지 시스템과 유연하게 통합할 수 있습니다.

### 결제 아키텍처 확장

위 핵심 결제 아키텍처는 특수 사용 사례를 위해 확장할 수 있습니다.

- **AP2 Mandates Extension** (`dev.ucp.shopping.ap2_mandate`):
  자율 커머스처럼 부인 방지 증거가 필요한 시나리오에 사용자 승인 암호학적 증명을 추가합니다.
  [AP2 Mandates Extension](ap2-mandates.md) 참고.

- **커스텀 Handler 타입**: 결제 자격증명 제공자는 새로운 결제 수단 지원을 위해
  커스텀 handler를 정의할 수 있습니다.
  자세한 내용은 [Payment Handler Guide](payment-handler-guide.md) 참고.

확장 모델은 핵심 아키텍처를 단순하게 유지하면서도,
필요 시 고급 보안/컴플라이언스 요구사항을 수용할 수 있게 합니다.

## 전송 계층

UCP는 복수 전송 프로토콜을 지원합니다.
Platform과 business는 profile의 `services` 정보를 기반으로 전송 방식을 협상합니다.

### REST 전송 (코어)

UCP는 REST 패턴 기반으로 **HTTP/1.1** 이상을 지원합니다.

- **Content-Type:** 요청/응답은 `application/json`을 사용해야 합니다(**MUST**).
- **Methods:** 구현체는 표준 HTTP 메서드(예: 생성 `POST`, 조회 `GET`)를 사용해야 합니다(**MUST**).
- **Status Codes:** 구현체는 표준 HTTP 상태 코드(예: 200, 201, 400, 401, 500)를 사용해야 합니다(**MUST**).

### Model Context Protocol(MCP)

UCP는 JSON-RPC 기반의 **[MCP 프로토콜](https://modelcontextprotocol.io/specification/)** 을 지원합니다.

#### 요청 포맷

MCP 요청은 `tools/call` 메서드를 사용하며,
연산명은 `params.name`, UCP payload는 `params.arguments`에 담습니다.

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_checkout",
    "arguments": {
      "meta": {"ucp-agent": {"profile": "https://..."}},
      "checkout": {"line_items": [...]}
    }
  },
  "id": 1
}
```

#### 응답 포맷

MCP 도구 응답은 하위 호환을 위해 dual-output 패턴을 사용합니다.
UCP MCP 서버는 다음을 따릅니다.

- `structuredContent`에 UCP 응답 payload를 반환해야 합니다(**MUST**).
- tool 정의에서 capability별 적절한 UCP JSON Schema를 가리키는
  `outputSchema`를 선언하는 것이 권장됩니다(**SHOULD**).
- `structuredContent`를 지원하지 않는 클라이언트 호환을 위해
  직렬화 JSON을 `content[]`에도 함께 반환하는 것이 권장됩니다(**SHOULD**).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "structuredContent": {
      "checkout": {
        "ucp": {"version": "2026-01-11", "capabilities": {...}},
        "id": "checkout_abc123",
        "status": "incomplete",
        ...
      }
    },
    "content": [
      {"type": "text", "text": "{\"checkout\":{\"ucp\":{...},\"id\":\"checkout_abc123\",...}}"}
    ]
  }
}
```

### Agent-to-Agent Protocol (A2A)

Business는 UCP를 A2A 확장으로 지원하는 A2A 에이전트를 노출할 수 있습니다(**MAY**).
이를 통해 구조화된 UCP 데이터 타입으로 platform과 통합할 수 있습니다.

### Embedded Protocol (EP)

Business는 적격 host에 임베디드 인터페이스를 제공할 수 있습니다(**MAY**).
사용자 상호작용 이벤트를 수신하고 주요 사용자 동작을 위임할 수 있습니다.

시작점은 business가 반환하는 `continue_url`입니다.

## 표준 Capability

UCP는 다음과 같은 표준 capability 집합을 정의합니다.

| Capability 이름      | ID (URI)                                       | 설명                                                                                                         |
| :------------------- | :--------------------------------------------- | :----------------------------------------------------------------------------------------------------------- |
| **Checkout**         | `{{ ucp_url }}/schemas/shopping/checkout.json` | cart 관리와 세금 계산을 포함한 checkout 세션 생성/관리 기능 제공                                              |
| **Identity Linking** | -                                              | OAuth 2.0 기반 권한 위임으로 platform이 사용자 대신 작업을 수행할 수 있게 함                                 |
| **Order**            | `{{ ucp_url }}/schemas/shopping/order.json`    | 주문 라이프사이클(배송, 전달, 반품)에 대한 비동기 업데이트를 business가 전달할 수 있게 함                    |

### 정의 및 확장

각 capability의 endpoint, schema, 유효 확장에 대한 상세 정의는
해당 명세 파일에서 제공합니다.
확장은 보통 상위 capability와 함께 버저닝되고 정의됩니다.

## 보안 및 인증

### 전송 보안

모든 UCP 통신은 **HTTPS**로 이루어져야 합니다(**MUST**).

### 요청 인증

- **Platform → Business:** 요청은 표준 헤더(예: `Authorization: Bearer <token>`)로 인증하는 것이 권장됩니다(**SHOULD**).
- **Business → Platform(Webhook):** webhook은 무결성과 출처 검증을 위해
  shared secret 또는 비대칭 키로 서명되어야 합니다(**MUST**).

### 데이터 프라이버시

민감 데이터(결제 자격증명, PII 등)는 PCI-DSS 및 GDPR 가이드라인에 따라 처리되어야 합니다(**MUST**).
UCP는 business/platform 책임 범위를 줄이기 위해 토큰화 결제 데이터 사용을 권장합니다.

### 거래 무결성 및 부인 방지 { #transaction-integrity-and-non-repudiation }

승인에 대한 암호학적 증명이 필요한 시나리오(예: 자율 에이전트, 고액 거래)에서
UCP는 **AP2 Mandates Extension**(`dev.ucp.shopping.ap2_mandate`)을 지원합니다.
이 선택 확장이 협상되면 다음이 적용됩니다.

- Business는 checkout 조건에 대한 암호학적 서명을 제공합니다.
- Platform은 사용자 승인을 증명하는 암호학적 mandate를 제공합니다.

이 메커니즘은 거래 상세와 참여자 동의에 대해 종단 간 강한 암호학적 보장을 제공하여
변조와 분쟁 위험을 크게 줄입니다.

[AP2 Mandates Extension](ap2-mandates.md)에서 전체 명세, 구현 가이드, 예시를 확인할 수 있습니다.

## 버저닝

### 버전 형식

UCP는 `YYYY-MM-DD` 형식의 날짜 기반 버저닝을 사용합니다.
이를 통해 시간순 정렬과 버전 비교를 명확하게 수행할 수 있습니다.

### 버전 Discovery 및 협상

UCP는 강한 하위 호환성을 우선합니다.
특정 버전을 구현한 business는 해당 버전 또는 그 이전 버전을 사용하는 platform 요청을 처리하는 것이 권장됩니다(**SHOULD**).

Business와 platform은 각각 profile에 단일 버전을 선언합니다.

#### 예시

=== "Business Profile"

    ```json
    {
      "ucp": {
        "version": "2026-01-11",
        "services": { ... },
        "capabilities": { ... },
        "payment_handlers": { ... }
      }
    }
    ```

=== "Platform Profile"

    ```json
    {
      "ucp": {
        "version": "2026-01-11",
        "services": { ... },
        "capabilities": { ... },
        "payment_handlers": { ... }
      }
    }
    ```

### 버전 협상

![상위 수준 해석 흐름 시퀀스 다이어그램](site:specification/images/ucp-discovery-negotiation.png)

Business는 platform 버전을 검증하고 호환 여부를 판단해야 합니다(**MUST**).

1. Platform은 요청에서 참조한 profile로 버전을 선언합니다.
2. Business validates:
    - platform 버전 ≤ business 버전: 요청을 처리해야 합니다(**MUST**).
    - platform 버전 > business 버전: `version_unsupported` 오류를 반환해야 합니다(**MUST**).
3. Business는 처리에 사용한 버전을 모든 응답에 포함해야 합니다(**MUST**).

버전 확인 응답 예:

```json
{
  "ucp": {
    "version": "2026-01-11",
    "capabilities": { ... },
    "payment_handlers": { ... }
  },
  "id": "checkout_123",
  "status": "incomplete"
  ...other checkout fields
}
```

버전 미지원 오류 예:

```json
{
  "status": "requires_escalation",
  "messages": [{
    "type": "error",
    "code": "version_unsupported",
    "content": "Version 2026-01-12 is not supported. This business implements version 2026-01-11.",
    "severity": "requires_buyer_input"
  }]
}
```

### 하위 호환성

#### 하위 호환 변경

다음 변경은 새 버전 없이 도입할 수 있습니다(**MAY**).

- 응답에 비필수 필드 추가
- 요청에 비필수 파라미터 추가
- 전송에 새 endpoint/method/operation 추가
- 기존 오류 구조를 유지한 새 오류 코드 추가
- enum에 새 값 추가(단, 완전 목록으로 명시된 경우 제외)
- 응답 필드 순서 변경
- 불투명 문자열(ID, token) 길이/형식 변경

#### 비호환 변경

다음 변경은 새 버전 없이 도입하면 안 됩니다(**MUST NOT**).

- 기존 필드 삭제/개명
- 필드 타입/의미 변경
- 비필수 필드를 필수화
- operation/method/endpoint 제거
- 인증/인가 요구사항 변경
- 기존 프로토콜 흐름 또는 상태 머신 수정
- 기존 오류 코드 의미 변경

### 컴포넌트 독립 버저닝

- UCP 프로토콜 버전은 capability 버전과 독립적으로 관리됩니다.
- 각 capability도 다른 capability와 독립적으로 버저닝됩니다.
- capability는 프로토콜과 동일한 하위 호환 규칙을 따라야 합니다(**MUST**).
- Business는 위와 동일한 로직으로 capability 버전 호환성을 검증해야 합니다(**MUST**).
- 전송 계층은 자체 버전 처리 메커니즘을 정의할 수 있습니다(**MAY**).

#### UCP Capability (`dev.ucp.*`)

UCP 작성 capability는 기본적으로 프로토콜 릴리스와 함께 버저닝됩니다.
단, 프로토콜 릴리스 주기 외에서 비호환 변경이 필요하면
개별 capability를 독립 버저닝할 수 있습니다(**MAY**).

#### Vendor Capability (`com.{vendor}.*`)

`dev.ucp.*` 외 네임스페이스의 capability는 완전히 독립적으로 버저닝됩니다.
벤더는 자체 릴리스 주기와 버전 전략을 통제합니다.

## 용어집

| 용어                              | 약어    | 정의                                                                                                                                                    |
| :-------------------------------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Agent Payments Protocol**       | AP2     | AI 에이전트가 안전하게 상호운용하며 자율 결제를 수행하도록 설계된 오픈 프로토콜. UCP는 안전한 결제 mandate를 위해 AP2를 활용합니다.                    |
| **Agent2Agent Protocol**          | A2A     | 다양한 AI 에이전트 간 안전하고 협력적인 통신을 위한 오픈 표준. UCP는 A2A를 전송 계층으로 사용할 수 있습니다.                                          |
| **Capability**                    | -       | business가 지원하는 독립 핵심 기능(예: Checkout, Identity Linking). capability는 UCP의 기본 동작 단위입니다.                                           |
| **Credential Provider**           | CP      | 사용자 결제/신원 자격증명을 안전하게 관리·실행하는 신뢰 주체(예: 디지털 월렛).                                                                          |
| **Extension**                     | -       | `extends` 필드를 통해 다른 capability를 보강하는 선택 capability. 확장은 `ucp.capabilities[]`에 core capability와 함께 나타납니다.                      |
| **Profile**                       | -       | business/platform이 well-known URI에 게시하는 JSON 문서로, 정체성·지원 capability·endpoint를 선언합니다.                                               |
| **Business**                      | -       | 상품/서비스를 판매하는 주체. UCP에서 **Merchant of Record(MoR)** 로서 재무 책임과 주문 소유권을 가집니다.                                               |
| **Model Context Protocol**        | MCP     | AI 모델이 외부 데이터/도구와 연결되는 방식을 표준화한 프로토콜. UCP capability는 MCP tool과 1:1 매핑될 수 있습니다.                                   |
| **Universal Commerce Protocol**   | UCP     | 본 문서에서 정의한 표준으로, 표준화된 capability와 discovery를 통해 커머스 주체 간 상호운용성을 제공합니다.                                             |
| **Payment Service Provider**      | PSP     | business를 대신해 결제 승인/처리/정산을 수행하는 금융 인프라 제공자입니다.                                                                              |
| **Platform**                      | -       | 사용자 대면 표면(AI 에이전트, 앱, 웹사이트 등)으로서 사용자를 대신해 business를 탐색하고 커머스를 수행하는 주체입니다.                                 |
| **Verifiable Digital Credential** | VDC     | Issuer가 서명한 자격증명(클레임 집합)으로, 암호학적으로 진위 검증이 가능합니다. UCP에서 안전한 결제 승인에 활용됩니다.                                  |
