# 플랫폼 토크나이저 결제 핸들러

- **Handler Name:** `com.example.platform_tokenizer`
- **Type:** Payment Handler Example

## 소개

이 예시는 **플랫폼이 tokenizer 역할을 수행하는** 토큰화 결제 핸들러를 보여줍니다. 플랫폼의 **payment credential provider**가 민감 결제 데이터를 안전하게 저장하고 (예: 사용자 지갑의 저장 카드), 외부 `/tokenize` endpoint 호출 없이 내부에서 토큰을 생성합니다.

플랫폼의 credential provider는 비즈니스가 호출해 결제 처리용 민감 결제 수단 정보를 가져갈 수 있도록 `/detokenize` endpoint를 제공합니다.

이 패턴은 규정 준수 자격증명 저장소를 운영하는 wallet 제공 플랫폼에 적합합니다.

**참고:** 이 예시는 카드 자격증명을 사용하지만, 패턴 자체는 **모든 자격증명 타입**에 적용할 수 있습니다. 규제 준수 요건은 자격증명 타입별로 달라집니다 (예: 카드의 경우 PCI DSS).

### 핵심 이점

- **초기 전송 없음:** 결제 확정 시점 전까지 플랫폼은 민감 데이터를 노출하지 않습니다.
- **플랫폼 주도 보안:** 토큰 라이프사이클과 바인딩 정책을 플랫폼이 제어합니다.
- **PSP 유연성:** 비즈니스가 detokenization을 PSP에 위임할 수 있어, 비즈니스 시스템에서 민감 데이터를 배제할 수 있습니다.

### 빠른 시작(QuickStart)

| If you are a...                        | Start here                                    |
| -------------------------------------- | --------------------------------------------- |
| **Business** accepting this handler    | [Business Integration](#business-integration) |
| **Platform** implementing this handler | [Platform Integration](#platform-integration) |
| **PSP** processing for businesses      | [PSP Integration](#psp-integration)           |

______________________________________________________________________

## 참여자

| Participant  | Role                                                                            | Prerequisites                 |
| ------------ | ------------------------------------------------------------------------------- | ----------------------------- |
| **Business** | handler를 광고하고 토큰을 수신하며, 필요 시 PSP 위임                            | Yes — 플랫폼에 온보딩 필요    |
| **Platform** | 토큰 생성 및 `/detokenize` endpoint를 제공하는 payment credential provider 운영 | Yes — 토큰화 서비스 구현 필요 |
| **PSP**      | 필요 시 비즈니스 대신 detokenize 수행 및 결제 처리                              | Yes — 플랫폼에 온보딩 필요    |

### 패턴 플로우: 비즈니스가 Detokenize

```text
+-----------------+                              +------------+
|    Platform     |                              |  Business  |
|  (Tokenizer)    |                              |            |
+--------+--------+                              +------+-----+
         |                                              |
         |  1. Business registers with Platform (out-of-band)
         |<---------------------------------------------|
         |                                              |
         |  2. API credentials                          |
         |--------------------------------------------->|
         |                                              |
         |  3. GET ucp.payment_handlers                 |
         |--------------------------------------------->|
         |                                              |
         |  4. Handler with business identity           |
         |<---------------------------------------------|
         |                                              |
         |5. Platforms's Credential Provider generates token
         |                                              |
         |  6. POST checkout with TokenCredential       |
         |--------------------------------------------->|
         |                                              |
         |  7. POST /detokenize (to Credential Provider)|
         |<---------------------------------------------|
         |                                              |
         |  8. Sensitive Data                           |
         |--------------------------------------------->|
         |                                              |
         |  9. Checkout complete                        |
         |<---------------------------------------------|
```

### 패턴 플로우: PSP가 Detokenize

```text
+-----------------+     +------------+      +---------+
|    Platform     |     |  Business  |      |   PSP   |
|  (Tokenizer)    |     |            |      |         |
+--------+--------+     +------+-----+      +----+----+
         |                     |                 |
         |  1. Business + PSP register with Platform (out-of-band)
         |<--------------------|                 |
         |<--------------------------------------|
         |                     |                 |
         |  2. API credentials |                 |
         |-------------------->|                 |
         |-------------------------------------->|
         |                     |                 |
         |  3. Payment Credential Provider       |
         |     generates token                   |
         |                     |                 |
         |  4. POST checkout with TokenCredential|
         |-------------------->|                 |
         |                     |                 |
         |                     |  5. Forward     |
         |                     |  token to PSP   |
         |                     |---------------->|
         |                     |                 |
         |  6. POST /detokenize (to Credential Provider, with business identity)
         |<--------------------------------------|
         |                     |                 |
         |  7. Sensitive Data  |                 |
         |-------------------------------------->|
         |                     |                 |
         |                     |  8. Payment     |
         |                     |  result         |
         |                     |                  |
         |                     |<----------------|
         |                     |                 |
         |  9. Checkout complete                 |
         |<--------------------|                 |
```

______________________________________________________________________

## 비즈니스 통합

### 사전 조건

#### 중요: 보안 및 규정 준수 필수

이 핸들러를 수락하기 전에, 비즈니스는 플랫폼에 등록하여 `/detokenize` 호출용 인증 자격증명을 발급받아야 합니다.

`/detokenize` endpoint를 통해 민감 결제 수단 정보를 수신하는 주체이므로, 비즈니스는 처리 자격증명 타입의 관련 데이터 보안 표준을 **MUST** 준수해야 합니다 (예: 카드의 경우 PCI DSS). 여기에는 다음이 포함됩니다.

- 보안 전송(강력한 cipher suite를 사용하는 HTTPS/TLS)
- 결제 처리 중 민감 데이터의 보안 처리
- 금융 수단 저장·처리에 관한 관련 규제 준수

필요 시 비즈니스는 PSP에 detokenization을 위임할 수 있습니다 (PSP 또한 동일하게 규정 준수 필요).

**Prerequisites Output:**

| Field                      | Description                                        |
| -------------------------- | -------------------------------------------------- |
| `identity.access_token`    | 온보딩 시 플랫폼이 할당한 비즈니스 식별자          |
| Authentication credentials | `/detokenize` 호출 인증용 API key 또는 OAuth token |

### 핸들러 구성

비즈니스는 플랫폼의 토큰화 handler를 광고합니다. `config`에는 토큰 바인딩을 위한 플랫폼 측 비즈니스 identity가 포함됩니다. 플랫폼 handler 명세(`spec` 참조)는 플랫폼의 **payment credential provider**가 제공하는 `/detokenize` endpoint URL을 문서화합니다.

이 handler는 토큰화 입력으로 [CardCredential](https://ucp.dev/schemas/shopping/types/card_credential.json)을 받고, checkout에는 [TokenCredential](https://ucp.dev/schemas/shopping/types/token_credential.json)을 제공합니다.

**참고:** `/detokenize` 결과에는 **민감 결제 데이터**가 포함됩니다. 송신자(플랫폼 credential provider)와 수신자(비즈니스 또는 PSP)는 처리 자격증명 타입의 관련 표준을 **MUST** 준수해야 합니다 (예: 카드의 경우 PCI DSS).

#### 비즈니스 구성(디스커버리)

| Field         | Type   | Required | Description                            |
| ------------- | ------ | -------- | -------------------------------------- |
| `environment` | string | Yes      | API 환경 (`sandbox` 또는 `production`) |
| `business_id` | string | Yes      | 플랫폼이 할당한 비즈니스 식별자        |

#### 비즈니스 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.example.platform_tokenizer": [
        {
          "id": "platform_wallet",
          "version": "2026-01-11",
          "spec": "https://platform.example.com/ucp/handler.json",
          "schema": "https://platform.example.com/ucp/handler/schema.json",
          "config": {
            "environment": "production",
            "business_id": "business_abc123"
          }
        }
      ]
    }
  }
}
```

#### 응답 구성(체크아웃)

response config에는 런타임 토큰 라이프사이클 정보가 포함됩니다.

| Field               | Type    | Required | Description     |
| ------------------- | ------- | -------- | --------------- |
| `environment`       | string  | Yes      | API 환경        |
| `business_id`       | string  | Yes      | 비즈니스 식별자 |
| `token_ttl_seconds` | integer | No       | 토큰 TTL(초)    |

#### 응답 구성 예시

```json
{
  "config": {
    "environment": "production",
    "business_id": "business_abc123",
    "token_ttl_seconds": 900,
  }
}
```

### 결제 처리

토큰 자격증명이 포함된 checkout을 수신하면 다음을 수행합니다.

1. **Validate Handler:** `instrument.handler_id`가 기대 handler ID와 일치하는지 확인
1. **Detokenize 또는 위임:**
1. **Option A (Direct):** 플랫폼의 **credential provider** `/detokenize` endpoint를 직접 호출 후 결제 처리
1. **Option B (Delegated):** 토큰을 PSP로 전달해 detokenization 및 결제 처리 위임
1. **Return Response:** 최종 checkout 상태 반환

Option B는 [PSP Integration](#psp-integration) 섹션을 참고하세요.

#### 역토큰화 요청 예시(비즈니스)

```json
POST https://provider.platform.example.com/ucp/detokenize
Content-Type: application/json
Authorization: Bearer {business_api_key}

{
  "token": "ptok_x9y8z7w6v5u4",
  "binding": {
    "checkout_id": "checkout_789"
  }
}
```

참고: 비즈니스가 직접 인증해 호출하는 경우, `binding.identity`는 필요하지 않습니다. 플랫폼이 API key 기반으로 호출 주체를 식별할 수 있기 때문입니다.

______________________________________________________________________

## 플랫폼 통합

### 사전 조건

이 핸들러는 **규정 준수 payment credential provider** 또는 wallet 서비스를 운영하는 플랫폼이 구현합니다. 민감 데이터 처리와 `/detokenize` 노출은 메인 플랫폼 앱이 아니라 credential provider가 담당합니다. 구현을 위해 플랫폼은 다음을 충족해야 합니다.

1. 자격증명 저장·처리 규정 준수 유지(예: 카드의 경우 PCI DSS)
1. 온보딩 시 비즈니스 공개키/식별정보 관리
1. 핸들러 identity 기반으로 올바른 바인딩 정책 적용

**Implementation Requirements:**

| Requirement            | Description                                                                       |
| ---------------------- | --------------------------------------------------------------------------------- |
| `/detokenize` endpoint | 플랫폼 애플리케이션이 아니라 규정 준수 payment credential provider가 노출         |
| Token storage          | credential provider에서 토큰↔자격증명 매핑 및 바인딩 메타데이터 저장              |
| Participant allowlist  | 온보딩된 business/PSP만 credential provider의 `/detokenize` 호출 허용             |
| Binding verification   | payment credential provider가 detokenize 시 `checkout_id` 및 호출자 identity 검증 |

### 핸들러 구성(플랫폼)

플랫폼은 UCP 프로필의 `payment_handlers` 레지스트리에서 `platform_config`를 사용해 이 핸들러를 광고합니다.

#### 플랫폼 구성(디스커버리)

| Field                       | Type    | Required | Description                            |
| --------------------------- | ------- | -------- | -------------------------------------- |
| `environment`               | string  | Yes      | API 환경 (`sandbox` 또는 `production`) |
| `platform_id`               | string  | Yes      | 플랫폼 식별자                          |
| `default_token_ttl_seconds` | integer | No       | 비즈니스에 제공하는 기본 토큰 TTL      |

#### 플랫폼 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.example.platform_tokenizer": [
        {
          "id": "platform_wallet",
          "version": "2026-01-11",
          "spec": "https://platform.example.com/ucp/handler.json",
          "schema": "https://platform.example.com/ucp/handler/schema.json",
          "config": {
            "environment": "production",
            "platform_id": "platform_abc123",
            "default_token_ttl_seconds": 900
          }
        }
      ]
    }
  }
}
```

### 토큰 생성

플랫폼 애플리케이션은 결제 플로우를 오케스트레이션하지만, **민감 결제 데이터에는 접근하지 않습니다**. 대신 다음 방식으로 처리됩니다.

1. 플랫폼의 **payment credential provider**가 결제 자격증명을 안전하게 저장
1. 결제가 필요할 때 플랫폼 애플리케이션이 credential provider에 토큰 생성 요청
1. credential provider가 `checkout_id`와 비즈니스 `identity` 모두에 바인딩된 토큰 생성
1. credential provider가 토큰을 플랫폼 애플리케이션에 반환
1. 플랫폼 애플리케이션이 checkout 제출 시 해당 토큰 포함

이 분리 구조를 통해 플랫폼 앱은 민감 결제 수단 정보에 직접 접근하지 않습니다.

### 체크아웃 제출

플랫폼 애플리케이션은 payment credential provider에서 받은 토큰으로 checkout을 제출합니다.

```json
POST /checkout-sessions/{checkout_id}/complete
Content-Type: application/json

{
  "payment": {
    "instruments": [
      {
        "id": "instr_1",
        "handler_id": "platform_wallet",
        "type": "card",
        "selected": true,
        "display": {
          "brand": "visa",
          "last_digits": "4242"
        },
        "credential": {
          "type": "token",
          "token": "ptok_x9y8z7w6v5u4"
        }
      }
    ]
  },
  "risk_signals": {
    // ... the key value pair for potential risk signal data
  }
}
```

______________________________________________________________________

## 피에스피(PSP) 통합

### 사전 조건

#### 중요: 보안 및 규정 준수 필수

PSP가 비즈니스를 대신해 detokenize를 수행하기 전에, 처리 대상 비즈니스 목록을 포함해 플랫폼에 등록해야 합니다.

`/detokenize` endpoint를 통해 민감 결제 수단 정보를 수신하므로, PSP는 처리 자격증명 타입의 관련 보안 표준을 **MUST** 준수해야 합니다 (예: 카드의 경우 PCI DSS). 여기에는 다음이 포함됩니다.

- 보안 전송(강력한 cipher suite를 사용하는 HTTPS/TLS)
- 결제 처리 중 민감 데이터의 보안 처리
- 금융 수단 저장·처리에 관한 관련 규제 준수

**Prerequisites Output:**

| Field                      | Description                                        |
| -------------------------- | -------------------------------------------------- |
| Authentication credentials | `/detokenize` 호출 인증용 API key 또는 OAuth token |
| Business associations      | 이 PSP가 detokenize 가능한 비즈니스 identity 목록  |

### 역토큰화 플로우

비즈니스가 토큰을 PSP에 전달하면 PSP는 다음을 수행합니다.

1. payment instrument에서 토큰 추출
1. 비즈니스 identity를 `binding`에 포함해 플랫폼의 **payment credential provider** `/detokenize` endpoint 호출
1. 반환된 credential로 결제 처리

#### 역토큰화 요청 예시(PSP)

```json
POST https://provider.platform.example.com/ucp/detokenize
Content-Type: application/json
Authorization: Bearer {psp_api_key}

{
  "token": "ptok_x9y8z7w6v5u4",
  "binding": {
    "checkout_id": "checkout_789",
    "identity": {
      "access_token": "business_abc123"
    }
  }
}
```

참고: 여기서는 `binding.identity`가 필수입니다. PSP는 비즈니스를 대신해 호출하므로, 어느 비즈니스 토큰을 조회하는지 명시해야 합니다.

플랫폼의 payment credential provider는 다음을 검증합니다.

- 해당 PSP가 이 비즈니스에 대해 detokenize 권한이 있는지
- `checkout_id`가 원래 토큰화 요청과 일치하는지
- 토큰이 만료되었거나 이미 사용된 토큰이 아닌지

______________________________________________________________________

## 보안 고려사항

| Requirement                          | Description                                                                                                                                 |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Compliance (credential provider)** | 플랫폼 credential provider는 민감 결제 수단 정보를 처리·저장할 때 자격증명 타입별 관련 표준(예: 카드의 PCI DSS)을 **MUST** 준수해야 합니다. |
| **Compliance (Receivers)**           | `/detokenize`를 호출해 민감 payload를 수신하는 business/PSP는 자격증명 타입별 관련 표준을 **MUST** 준수해야 합니다.                         |
| **Secure transmission**              | `/detokenize` 데이터 전송은 강력한 cipher suite의 HTTPS/TLS를 **MUST** 사용해야 합니다.                                                     |
| **No Platform App access**           | 플랫폼 애플리케이션은 민감 데이터를 **MUST NOT** 처리해야 하며, 규정 준수 payment credential provider만 처리해야 합니다.                    |
| **Endpoint isolation**               | `/detokenize` endpoint는 플랫폼 앱이 아니라 payment credential provider가 **MUST** 노출해야 합니다.                                         |
| **Participant authentication**       | 플랫폼 credential provider는 `/detokenize` 수락 전에 business/PSP를 **MUST** 인증해야 합니다.                                               |
| **Identity binding**                 | 토큰은 handler 선언의 비즈니스 `identity`에 **MUST** 바인딩되어야 합니다.                                                                   |
| **Checkout-bound**                   | 토큰은 특정 `checkout_id`에 **MUST** 바인딩되어야 합니다.                                                                                   |
| **Caller verification**              | 플랫폼은 인증된 호출자가 토큰의 바인딩 identity와 일치하는지(또는 권한 있는 PSP인지) **MUST** 검증해야 합니다.                              |
| **Single-use**                       | 토큰은 detokenization 후 무효화하는 것을 **SHOULD** 권장합니다.                                                                             |
| **Short TTL**                        | 토큰은 짧은 TTL을 갖는 것을 **SHOULD** 권장합니다.                                                                                          |
| **HTTPS required**                   | 모든 `/detokenize` 호출은 TLS를 사용해야 합니다.                                                                                            |

______________________________________________________________________

## 참고자료

- **Pattern:** [Tokenization Payment Handler](https://ucp.dev/specification/payment-handler-guide)
- **API Pattern:** `https://ucp.dev/handlers/tokenization/openapi.json`
- **Identity Schema:** `https://ucp.dev/schemas/shopping/types/payment_identity.json`
