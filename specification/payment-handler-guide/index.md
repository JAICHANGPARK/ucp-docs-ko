# 결제 핸들러 명세 가이드

## 소개

이 가이드는 UCP 결제 핸들러 명세를 작성하기 위한 표준 구조와 용어를 정의합니다. 모든 결제 핸들러 명세는 구현자에게 일관성, 완전성, 명확성을 제공하기 위해 이 구조를 따르는 것이 **권장(SHOULD)** 됩니다.

### 목적

결제 핸들러는 플랫폼, business, 결제 제공자 간 "N-to-N" 상호운용성을 가능하게 합니다. 잘 정의된 핸들러는 각 참여자에 대해 아래 질문에 답해야 합니다.

- **누가 참여하는가?** 어떤 참여자가 있고 역할은 무엇인가?
- **사전 조건은 무엇인가?** 어떤 온보딩/설정이 필요한가?
- **어떻게 구성되는가?** 어떤 설정이 광고되거나 소비되는가?
- **어떻게 실행되는가?** 결제 수단을 획득/처리하기 위해 어떤 프로토콜을 따르는가?

이 가이드는 모든 핸들러 명세가 위 질문에 체계적으로 답하도록 프레임워크를 제공합니다.

### 범위

이 가이드는 다음에 적용됩니다.

- **Handlers** (예: `com.google.pay`, `dev.shopify.shop_pay`) - 특정 결제 수단 구현

______________________________________________________________________

## 핵심 개념

모든 결제 핸들러 명세는 아래 핵심 요소를 **반드시(MUST)** 정의해야 합니다.

**프로토콜 시그니처 참고:** 이 섹션의 함수 시그니처(예: `PROCESSING(...)`)는 실제 함수 호출이 아니라 **논리적 데이터 흐름**을 나타냅니다. 명세 작성자는 이 논리 흐름을 구현체의 실제 전송 프로토콜에 매핑해야 합니다.

```text
+------------------------------------------------------------------------------+
|                        Payment Handler Framework                             |
+------------------------------------------------------------------------------+
|                                                                              |
|   +--------------+                                                           |
|   | PARTICIPANTS |  Who participates in this handler?                        |
|   +------+-------+                                                           |
|          |                                                                   |
|          v                                                                   |
|   +--------------+                                                           |
|   |PREREQUISITES |  How does each participant obtain identity & configs?     |
|   +------+-------+                                                           |
|          |                                                                   |
|          +--------------------+----------------------+                       |
|          v                    v                      v                       |
|   +--------------+    +--------------+      +--------------+                 |
|   |   HANDLER    |    |  INSTRUMENT  |      |  PROCESSING  |                 |
|   | DECLARATION  |    |  ACQUISITION |      |              |                 |
|   +--------------+    +--------------+      +--------------+                 |
|   Business advertises  platform acquires     Participant                     |
|   handler config       checkout instrument   processes instrument            |
|                                                                              |
+------------------------------------------------------------------------------+
```

### 참여자(Participants)

**정의:** 결제 핸들러 생명주기에 참여하는 서로 다른 행위자. 모든 핸들러는 최소 2개의 참여자(business, platform)를 가지며, 필요 시 특정 역할을 가진 추가 참여자를 정의할 수 있습니다(**MAY**).

**용어 참고:** 이 가이드에서는 참여자를 \*\*"Business"\*\*로 표기하지만, 기술 스키마 필드는 업계 표준 명명(`merchant_*`)을 유지할 수 있습니다. (예: `merchant_id`, `merchant_name`) 명세는 해당 필드 매핑을 **반드시(MUST)** 명시해야 합니다.

**표준 참여자:**

| Participant  | Role                                                     |
| ------------ | -------------------------------------------------------- |
| **Business** | 핸들러 설정을 광고하고 결제 instrument를 처리            |
| **Platform** | 핸들러를 탐색하고 결제 instrument를 획득해 checkout 제출 |

**확장 참여자** (핸들러별 예시):

| Participant   | Example Role                                      |
| ------------- | ------------------------------------------------- |
| **Tokenizer** | 원본 자격증명을 보관하고 토큰 자격증명 발급       |
| **PSP**       | business를 대신해 checkout instrument로 결제 처리 |

### 사전 요구사항(Prerequisites)

**정의:** 참여자가 핸들러 흐름에 들어가기 전에 완료해야 하는 온보딩/설정/구성.

**시그니처:**

```text
PREREQUISITES(participant, onboarding_input) → prerequisites_output
```

| Field                  | Description                                |
| ---------------------- | ------------------------------------------ |
| `participant`          | 온보딩 대상 참여자 (business, platform 등) |
| `onboarding_input`     | 설정 중 참여자가 제공하는 정보             |
| `prerequisites_output` | 온보딩 후 받은 identity 및 추가 구성       |

**Prerequisites Output:**

`prerequisites_output`은 온보딩 결과를 담습니다. 최소한 **identity**를 포함해야 하며([Payment Identity](https://ucp.dev/schemas/shopping/types/payment_identity.json) 참고), 핸들러별로 추가 구성/자격증명/설정이 포함될 수 있습니다(**MAY**).

결제 핸들러 명세는 `prerequisites_output`에 대한 별도 정식 스키마를 반드시 정의할 필요는 없습니다. 대신 아래를 명확히 문서화하는 것이 **권장(SHOULD)** 됩니다.

- 어떤 identity가 할당되는지 (그리고 `PaymentIdentity`에 어떻게 매핑되는지)
- 어떤 추가 구성이 제공되는지
- 해당 출력이 Handler Declaration, Instrument Acquisition, Processing에서 어떻게 사용되는지

**참고:**

- prerequisites는 보통 out-of-band(포털, 계약, API 호출)로 진행됨
- 여러 참여자가 독립적인 prerequisites를 가질 수 있음(**MAY**)
- prerequisites의 identity는 보통 핸들러 `config` 안에 나타남 (예: `merchant_id` 등 핸들러 전용 필드)
- 원본 자격증명을 받는 참여자(business, PSP 등)는 보통 온보딩에서 보안 책임 수락 절차를 거치며, 자격증명 처리 및 준수 책임을 명시적으로 수락해야 함

### 핸들러 선언(Handler Declaration)

**정의:** business가 이 핸들러 지원을 알리고 platform이 호출할 수 있도록 광고하는 설정.

**시그니처:**

```text
HANDLER_DECLARATION(prerequisites_output) → handler_declaration
```

| Field                  | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `prerequisites_output` | business prerequisites에서 얻은 identity 및 설정 |
| `handler_declaration`  | `ucp.payment_handlers`에 광고되는 핸들러 객체    |

**출력 구조:**

핸들러 선언은 [`PaymentHandler`](https://ucp.dev/schemas/payment_handler.json) 스키마를 따릅니다. 명세는 구성/도구 스키마의 종류와, business prerequisites 출력 및 원하는 설정에 따라 각각을 만드는 방법을 정의하는 것이 **권장(SHOULD)** 됩니다.

```json
{
  "ucp": {
    "payment_handlers": {
      "com.example.handler": [
        {
          "id": "processor_tokenizer_1234",
          "version": "2026-01-11",
          "spec": "https://example.com/ucp/handler",
          "schema": "https://example.com/ucp/handler/schema.json",
          "config": {
            // Handler-specific configuration (see 2.3.1)
          }
        }
      ]
    }
  }
}
```

______________________________________________________________________

#### 핸들러 선언 변형

`PaymentHandler` 스키마는 컨텍스트별로 3가지 변형을 정의합니다. 기술적으로는 `id`와 `version`만 필수지만, 각 변형은 고유 목적을 가지며 보통 서로 다른 설정을 포함합니다.

| Variant             | Context                                 | Purpose                                                                                                                    |
| ------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **business_schema** | Business discovery (`/.well-known/ucp`) | business identity와 이 핸들러 구성 방식을 선언. merchant 전용 설정 포함                                                    |
| **platform_schema** | Platform profile (advertised URI)       | platform identity와 지원 방식 선언. 구현자를 위한 `spec`/`schema` URL 포함                                                 |
| **response_schema** | Checkout/Order API responses            | **런타임 구성**(병합 컨텍스트): merchant identity, 결제수단, 토큰화 명세 등 거래 처리에 필요한 상태. 보통 가장 정보가 많음 |

**Business Schema 예시** (business가 핸들러 구성 선언):

```json
{
  "id": "processor_tokenizer_1234",
  "version": "2026-01-11",
  "spec": "https://example.com/ucp/handler",
  "schema": "https://example.com/ucp/handler/schema.json",
  "config": {
    "environment": "production",
    "business_id": "business_xyz_789"
  }
}
```

**Platform Schema 예시** (platform이 핸들러 지원 선언):

```json
{
  "id": "platform_tokenizer_2345", // note: ids are for disambiguation, they may differ between business and platform
  "version": "2026-01-11",
  "spec": "https://example.com/ucp/handler",
  "schema": "https://example.com/ucp/handler/schema.json",
  "config": {
    "environment": "production",
    "platform_id": "platform_abc_123"
  }
}
```

**Response Schema 예시** (checkout용 런타임 컨텍스트):

```json
{
  "id": "processor_tokenizer_1234",
  "version": "2026-01-11",
  "config": {
    "api_version": 2,
    "environment": "production",
    "business_id": "business_xyz_789",
    "available_instruments": [
      {
        "type": "token_alt",
        "tokenization_specification": {
          "type": "merchant_gateway"
        }
      }
    ]
  }
}
```

______________________________________________________________________

#### 스키마 정의

`schema` 필드는 핸들러 전용 형태를 정의하는 JSON schema를 가리킵니다. 작성자는 보통 형태별로 파일을 분리하고 참조합니다.

- **Config** - platform/business 선언 및 런타임 응답용 설정
- **Instrument** - platform에 반환되는 결제 instrument 구조
- **Credential** - instrument 내부 자격증명 구조

**예시 Handler Schema:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/schema.json",
  "title": "Tokenizer Handler Schema",
  "description": "Schema for the com.example.tokenizer payment handler.",
  "name": "com.example.tokenizer",
  "version": "2026-01-11",

  "$defs": {
    "tokenizer_token": { "$ref": "types/tokenizer_token.json" },
    "tokenizer_alt_token": { "$ref": "types/tokenizer_alt_token.json" },

    "tokenizer_instrument": { "$ref": "types/tokenizer_instrument.json" },
    "tokenizer_alt_instrument": { "$ref": "types/tokenizer_alt_instrument.json" },

    "com.example.tokenizer": {
      "payment_instrument": {
        "title": "Tokenizer Payment Instrument",
        "description": "Any instrument type supported by this handler.",
        "oneOf": [
          { "$ref": "#/$defs/tokenizer_instrument" },
          { "$ref": "#/$defs/tokenizer_alt_instrument" }
        ]
      },
      "platform_schema": {
        "title": "Tokenizer (Platform)",
        "description": "Platform-level handler configuration for discovery.",
        "allOf": [
          { "$ref": "https://ucp.dev/schemas/payment_handler.json#/$defs/platform_schema" },
          {
            "properties": {
              "config": {
                "$ref": "types/platform_config.json",
                "description": "Platform configuration for this handler."
              }
            }
          }
        ]
      },
      "business_schema": {
        "title": "Tokenizer (Business)",
        "description": "Business-level handler configuration for discovery.",
        "allOf": [
          { "$ref": "https://ucp.dev/schemas/payment_handler.json#/$defs/business_schema" },
          {
            "properties": {
              "config": {
                "$ref": "types/business_config.json",
                "description": "Business configuration for this handler."
              }
            }
          }
        ]
      },
      "response_schema": {
        "title": "Tokenizer (Response)",
        "description": "Runtime handler configuration in checkout responses.",
        "allOf": [
          { "$ref": "https://ucp.dev/schemas/payment_handler.json#/$defs/response_schema" },
          {
            "properties": {
              "config": {
                "$ref": "types/response_config.json",
                "description": "Runtime configuration for this handler."
              }
            }
          }
        ]
      }
    }
  }
}
```

______________________________________________________________________

#### 구성 스키마 형태

각 변형은 컨텍스트에 맞는 전용 config 스키마를 가집니다.

| Variant             | Config File                  | Purpose                                                   |
| ------------------- | ---------------------------- | --------------------------------------------------------- |
| **business_schema** | `types/business_config.json` | Business identity 및 merchant 전용 설정                   |
| **platform_schema** | `types/platform_config.json` | Platform identity 및 platform 수준 설정                   |
| **response_schema** | `types/response_config.json` | 전체 런타임 상태: identity, 사용 가능한 방식, 토큰화 명세 |

**예시 `types/business_config.json`:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/business_config.json",
  "title": "Tokenizer Business Config",
  "type": "object",
  "properties": {
    "environment": {
      "type": "string",
      "enum": ["sandbox", "production"],
      "default": "production"
    },
    "business_id": {
      "type": "string",
      "description": "Business identifier for this handler."
    }
  }
}
```

**예시 `types/platform_config.json`:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/platform_config.json",
  "title": "Tokenizer Platform Config",
  "type": "object",
  "properties": {
    "environment": {
      "type": "string",
      "enum": ["sandbox", "production"],
      "default": "production"
    },
    "platform_id": {
      "type": "string",
      "description": "Platform identifier for this handler."
    }
  }
}
```

**예시 `types/response_config.json`:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/response_config.json",
  "title": "Tokenizer Response Config",
  "type": "object",
  "properties": {
    "api_version": { "type": "integer" },
    "environment": {
      "type": "string",
      "enum": ["sandbox", "production"]
    },
    "business_id": {
      "type": "string",
      "description": "Business identifier for this handler."
    },
    "available_instruments": {
      "type": "array",
      "description": "Available instrument types for this checkout.",
      "items": {
        "type": "object",
        "properties": {
          "type": { "type": "string" },
          "tokenization_specification": { "type": "object" }
        }
      }
    }
  }
}
```

______________________________________________________________________

#### 결제 수단 스키마 형태

**기본 Instrument 스키마:**

| Schema                                                                                                | Description                                                      |
| ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [`payment_instrument.json`](https://ucp.dev/schemas/shopping/types/payment_instrument.json)           | 기본: id, handler_id, type, billing_address, credential, display |
| [`card_payment_instrument.json`](https://ucp.dev/schemas/shopping/types/card_payment_instrument.json) | 기본을 확장해 brand, last_digits, expiry, card art 포함          |

UCP는 `card` 같은 공통 결제 instrument의 기본 스키마를 제공합니다. 명세 작성자는 핸들러 전용 표시 데이터 추가나 credential 참조 커스터마이징을 위해 기본 instrument를 확장할 수 있습니다(**MAY**). 핸들러는 결제 흐름별로 여러 instrument 타입을 정의할 수 있습니다(**MAY**).

**예시 `types/tokenizer_instrument.json`** (카드 기반):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/tokenizer_instrument.json",
  "title": "Tokenizer Card Instrument",
  "description": "Card-based payment instrument for com.example.tokenizer.",
  "allOf": [
    { "$ref": "https://ucp.dev/schemas/shopping/types/card_payment_instrument.json" }
  ],
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": { "const": "tokenizer_card" },
    "credential": {
      "oneOf": [
        { "$ref": "tokenizer_token.json" },
        { "$ref": "tokenizer_alt_token.json" }
      ]
    },
    "special_tokenizer_context": {
      "type": "object",
      "description": "Handler-specific context for tokenizer instruments."
    }
  }
}
```

**예시 `types/tokenizer_alt_instrument.json`:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/tokenizer_alt_instrument.json",
  "title": "Tokenizer Alt Instrument",
  "description": "Alternative payment instrument for com.example.tokenizer.",
  "allOf": [
    { "$ref": "https://ucp.dev/schemas/shopping/types/payment_instrument.json" }
  ],
  "type": "object",
  "required": ["type"],
  "properties": {
    "type": { "const": "tokenizer_alt" },
    "credential": {
      "oneOf": [
        { "$ref": "tokenizer_token.json" },
        { "$ref": "tokenizer_alt_token.json" }
      ]
    },
    "special_tokenizer_context": {
      "type": "object",
      "description": "Handler-specific context for tokenizer instruments."
    }
  }
}
```

______________________________________________________________________

#### 자격증명 스키마 형태

**기본 Credential 스키마:**

| Schema                                                                                      | Description                     |
| ------------------------------------------------------------------------------------------- | ------------------------------- |
| [`payment_credential.json`](https://ucp.dev/schemas/shopping/types/payment_credential.json) | 기본: type discriminator만 포함 |
| [`token_credential.json`](https://ucp.dev/schemas/shopping/types/token_credential.json)     | 토큰: type + token string       |

UCP는 공통 결제 credential의 기본 스키마를 제공합니다. 작성자는 핸들러 전용 credential 컨텍스트를 포함하도록 이를 확장할 수 있습니다(**MAY**). 핸들러는 instrument 흐름별로 여러 credential 타입을 정의할 수 있습니다(**MAY**).

명세는 핸들러가 수용하는 credential 타입을 **반드시(MUST)** 정의해야 합니다.

**중요:** token credential을 사용하는 경우, 스키마는 플랫폼이 갱신 시점을 알 수 있도록 만료 필드(`expiry`, `ttl` 등)를 **반드시(MUST)** 포함해야 합니다.

**예시 `types/tokenizer_token.json`** (만료 토큰):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/tokenizer_token.json",
  "title": "Tokenizer Card Token",
  "description": "Card token credential for com.example.tokenizer.",
  "allOf": [
    { "$ref": "https://ucp.dev/schemas/shopping/types/token_credential.json" }
  ],
  "type": "object",
  "required": ["type", "token", "expiry"],
  "properties": {
    "type": {
      "const": "tokenizer_card_token",
      "description": "Credential type discriminator."
    },
    "expiry": {
      "type": "string",
      "format": "date-time",
      "description": "Token expiration. Platforms must refresh before this time."
    }
  }
}
```

**예시 `types/tokenizer_alt_token.json`** (대체 토큰):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/ucp/handlers/tokenizer/types/tokenizer_alt_token.json",
  "title": "Tokenizer Alt Token",
  "description": "Alt token credential for com.example.tokenizer, adding routing hints",
  "allOf": [
    { "$ref": "https://ucp.dev/schemas/shopping/types/token_credential.json" }
  ],
  "type": "object",
  "required": ["type", "token", "expiry"],
  "properties": {
    "type": {
      "const": "tokenizer_alt_token",
      "description": "Credential type discriminator."
    },
    "expiry": {
      "type": "string",
      "format": "date-time",
      "description": "Token expiration. Platforms must refresh before this time."
    },
    "routing_hint": {
      "type": "string",
      "description": "Optional routing number hint."
    }
  }
}
```

### 결제 수단 획득

**정의:** platform이 business checkout에 제출 가능한 payment instrument를 획득하기 위해 따르는 프로토콜.

**시그니처:**

```text
INSTRUMENT_ACQUISITION(
  platform_prerequisites_output,
  handler_declaration,
  binding,
  buyer_input
) → checkout_instrument
```

| Field                           | Description                                                         |
| ------------------------------- | ------------------------------------------------------------------- |
| `platform_prerequisites_output` | prerequisites가 필요했던 경우 platform의 prerequisites 출력(config) |
| `handler_declaration.config`    | business에서 제공된 핸들러 전용 설정                                |
| `binding`                       | **(2.6 참고)** credential을 특정 checkout에 결합하기 위한 컨텍스트  |
| `buyer_input`                   | 구매자의 결제 선택 또는 자격증명                                    |
| `checkout_instrument`           | checkout 제출용 결제 instrument                                     |

결제 핸들러 명세가 instrument acquisition의 정식 프로세스를 반드시 정의할 필요는 없습니다. 대신 아래를 명확히 문서화하는 것이 **권장(SHOULD)** 됩니다.

- 핸들러 `config`를 적용해 유효한 `checkout_instrument`를 구성하는 방법
- 사용 가능한 `config`와 `checkout`을 바탕으로, 보안상 핵심인 checkout/business별 credential binding을 만드는 방법

### 처리(Processing)

**정의:** 참여자(보통 business 또는 PSP)가 전달받은 payment instrument를 처리하고 거래를 완료하기 위해 수행하는 단계.

**시그니처:**

```text
PROCESSING(
  identity,
  checkout_instrument,
  binding,
  transaction_context
) → processing_result
```

| Field                 | Description                       |
| --------------------- | --------------------------------- |
| `identity`            | 처리 참여자의 `PaymentIdentity`   |
| `checkout_instrument` | platform에서 전달된 instrument    |
| `binding`             | 검증을 위한 binding 컨텍스트      |
| `transaction_context` | checkout 총액, line item 등       |
| `processing_result`   | 결제 상세를 포함한 성공/실패 결과 |

#### 오류 처리

명세는 공통 실패(예: Declined, Insufficient Funds, Network Error)를 표준 UCP Error 정의로 매핑하는 규칙을 **반드시(MUST)** 정의해야 합니다. 이렇게 해야 기반 처리기가 달라도 플랫폼이 구매자에게 일관되고 현지화 가능한 오류 UX를 제공할 수 있습니다.

### 핵심 정의

| Term        | Definition                                                                                                                                                                                                |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Binding** | 결제 instrument를 특정 checkout 거래와 business identity에 암호학적/논리적으로 결합하는 메커니즘. 이를 통해 Business A용 유효 credential이 가로채여 Business B에서 재사용되는 리플레이 공격을 방지합니다. |

______________________________________________________________________

## 명세 템플릿

핸들러 명세는 표준 템플릿 구조를 따르는 것이 **권장(SHOULD)** 됩니다. **[REQUIRED]** 표시는 **반드시(MUST)** 포함해야 하며, **[CONDITIONAL]** 표시는 해당 시에만 필요합니다.

**→ [Payment Handler Template](https://jaichangpark.github.io/ucp-docs-ko/specification/payment-handler-template/index.md)**

## 명세 작성자용 적합성 체크리스트

결제 핸들러 명세를 공개하기 전 아래를 확인하세요.

### 구조

- 표준 템플릿 구조를 사용한다
- 모든 [REQUIRED] 섹션이 존재한다
- 해당되는 [CONDITIONAL] 섹션이 존재한다

### 참여자

- 모든 참여자가 나열되어 있다
- 각 참여자의 역할이 명확히 설명되어 있다
- 필요 시 "Business"와 "Merchant" 용어 차이를 명시했다

### 사전 요구사항

- prerequisites가 필요한 각 참여자의 절차를 문서화했다
- 온보딩 입력을 명시했다
- prerequisites output(identity + 추가 config)을 설명했다
- identity가 `PaymentIdentity` 구조(`access_token`)에 매핑된다

### 핸들러 선언

- identity 스키마를 문서화했다(기본 또는 확장)
- config 스키마를 문서화했다(해당 시), environment 포함
- instrument 스키마를 문서화했다(기본 또는 확장)

### 결제 수단 획득

- 프로토콜 단계를 명확히 나열했다
- 논리 흐름을 실제 프로토콜에 매핑했다
- API 호출 또는 SDK 사용 예시를 제시했다
- binding 요구사항을 명시했다
- Checkout Payment Instrument 생성 방식/형태를 정의했다

### 처리

- 처리 단계를 명확히 나열했다
- 검증 요구사항을 명시했다
- 오류 처리 및 매핑을 다뤘다

### 보안

- 보안 요구사항을 나열했다
- binding 검증을 필수로 요구했다
- 자격증명 처리 지침을 제공했다
- (해당 시) 토큰 만료 정책을 정의했다

### 일반

- 핸들러 이름이 reverse-DNS 규칙을 따른다
- 버전이 YYYY-MM-DD 형식을 따른다
- 모든 schema URL이 namespace 권한과 일치한다
- references 섹션에 모든 스키마를 포함했다

______________________________________________________________________

## 모범 사례(Best Practices)

유지보수 가능한 고품질 핸들러 명세를 작성하려면 아래 지침을 따르세요.

### 스키마 설계

| Practice                         | Description                                                                  |
| -------------------------------- | ---------------------------------------------------------------------------- |
| **Extend, don't reinvent**       | 기본 스키마는 `allOf`로 조합하고, `brand`/`last_digits` 등을 재정의하지 않음 |
| **Use const for discriminators** | `credential.type`을 `const`로 정의해 타입 판별을 명확히 함                   |
| **Validate early**               | 명세 확정 전 스키마를 안정 URL에 게시해 구현자가 미리 검증 가능하게 함       |
| **Include Expiry**               | token credential 설계 시 `expiry` 또는 `ttl`을 항상 포함                     |

### 문서화

| Practice                  | Description                                         |
| ------------------------- | --------------------------------------------------- |
| **Show, don't just tell** | 모든 스키마/프로토콜 단계에 완전한 JSON 예시를 포함 |
| **Document error cases**  | 발생 가능한 오류와 참여자별 처리 방법을 명시        |
| **Version independently** | 핸들러 버전은 UCP 코어 버전과 독립적으로 진화       |

### 보안

| Practice                         | Description                                                       |
| -------------------------------- | ----------------------------------------------------------------- |
| **Require binding**              | credential을 항상 `binding`으로 특정 checkout에 결합              |
| **Minimize credential exposure** | 원본 credential(PAN 등)이 닿는 시스템 수를 최소화하도록 흐름 설계 |
| **Specify token lifetimes**      | 토큰이 single-use/time-limited/session-scoped인지 명확히 문서화   |

### 유지보수성

| Practice                        | Description                                                                                                                           |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Host schemas at stable URLs** | schema URL은 바꾸지 않고 필요 시 버전 경로 사용                                                                                       |
| **Fail gracefully**             | 공통 실패 시나리오에 대한 명확한 오류 응답 정의                                                                                       |
| **Link to examples**            | 기존 핸들러 명세 및 [Tokenization Guide](https://jaichangpark.github.io/ucp-docs-ko/specification/tokenization-guide/index.md)를 참조 |

______________________________________________________________________

## 함께 보기

- **[Tokenization Guide](https://jaichangpark.github.io/ucp-docs-ko/specification/tokenization-guide/index.md)** - 토큰화 결제 핸들러 구축 가이드
- **[Google Pay Handler](https://developers.google.com/merchant/ucp/guides/google-pay-payment-handler)**
- Google Pay 연동용 핸들러
- **[Shop Pay Handler](https://shopify.dev/docs/agents/checkout/shop-pay-handler)**
- Shop Pay 연동용 핸들러
