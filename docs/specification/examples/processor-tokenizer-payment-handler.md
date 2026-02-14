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

# 프로세서 토크나이저 결제 핸들러

* **Handler Name:** `com.example.processor_tokenizer`
* **Type:** Payment Handler Example

## 소개

이 핸들러는 토큰을 생성하는 주체(Tokenizer)와
최종 결제를 처리하는 주체(Processor)가 동일한
**"Tokenize to Process"** 플로우를 구현합니다.

**참고:** 이 예시는 카드 자격증명을 사용하지만,
패턴 자체는 **모든 자격증명 타입**에 적용할 수 있습니다.
규제 준수 요건은 자격증명 타입별로 달라집니다
(예: 카드의 경우 PCI DSS).

이 명세는 다음 두 가지 일반 구현 시나리오를 통합합니다.

1. **Business-Hosted:** 엔터프라이즈 비즈니스가 자체 보안 vault를 호스팅.
    비즈니스가 토큰화 및 결제 처리를 수행.
2. **PSP-Hosted:** 비즈니스가 서드파티 PSP를 사용.
    PSP가 토큰화 및 결제 처리를 수행.

두 경우 모두 **API detokenization 단계가 필요하지 않습니다**.
토큰 해석은 Processor의 보안 환경 내부에서 수행됩니다.

### 시나리오 비교

| Feature              | Scenario A: PSP-Hosted                       | Scenario B: Business-Hosted          |
| :------------------- | :------------------------------------------- | :----------------------------------- |
| **Tokenizer Host**   | Third-Party PSP                              | The Business                         |
| **Compliance Scope** | **Low** (Business never sees PAN)            | **High** (Business stores PAN)       |
| **Identity Binding** | **Required** (PSP needs Merchant Identifier) | **Implicit** (Business knows itself) |

---

## 참여자

| Participant               | Role                                                                                  | Prerequisites                                             |
| :------------------------ | :------------------------------------------------------------------------------------ | :-------------------------------------------------------- |
| **Tokenizer / Processor** | `/tokenize` endpoint 호스팅, 토큰 저장, 결제 처리 (Business 또는 PSP 가능)            | 자격증명 타입별 규제 준수(예: 카드의 경우 PCI DSS)        |
| **Platform**              | 보안 자격증명 제공자를 통해 자격증명 수집, Tokenizer 호출, checkout 제출              | 보안 자격증명 제공자                                      |
| **Business**              | checkout용 handler 구성                                                               | 없음(PSP-hosted인 경우)                                   |

### 패턴 플로우

```text
+------------+                         +-----------------------------------+
|  Platform  |                         |       Tokenizer / Processor       |
| (Collector)|                         |      (Business or PSP)            |
+-----+------+                         +-----------------+-----------------+
      |                                                  |
      |  1. GET ucp.payment_handlers                     |
      |------------------------------------------------->|
      |                                                  |
      |  2. Handler Config (URL + Identity)              |
      |<-------------------------------------------------|
      |                                                  |
      |  3. POST /tokenize (Credential + Identity)       |
      |------------------------------------------------->|
      |                                                  |
      |  4. Token                                        |
      |<-------------------------------------------------|
      |                                                  |
      |  5. POST checkout with TokenCredential           |
      |------------------------------------------------->|
      |                                                  |
      |        (Internal Resolution: Token -> Info)      |
      |                                                  |
      |  6. Payment Result                               |
      |<-------------------------------------------------|
```

---

## 구성

비즈니스는 UCP 프로필의 `payment_handlers` 레지스트리에서
이 핸들러를 광고합니다.
구성값에 따라 플랫폼은 "PSP Mode"(identity 전송) 또는
"Direct Mode"(암묵적 identity)로 동작합니다.

### 비즈니스 구성(디스커버리)

비즈니스는 discovery 단계에서 토큰화 endpoint와 identity를 광고합니다.
핸들러 명세(`spec` 필드 참조)는 `/tokenize` endpoint URL을 문서화합니다.

| Field         | Type   | Required | Description                                 |
| :------------ | :----- | :------- | :------------------------------------------ |
| `environment` | string | Yes      | API 환경 (`sandbox` 또는 `production`)      |
| `business_id` | string | Yes      | processor 측 비즈니스 식별자                |

#### 비즈니스 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.example.processor_tokenizer": [
        {
          "id": "processor_tokenizer",
          "version": "2026-01-11",
          "spec": "https://example.com/ucp/processor-tokenizer.json",
          "schema": "https://example.com/ucp/processor-tokenizer/schema.json",
          "config": {
            "environment": "production",
            "business_id": "merchant_xyz789"
          }
        }
      ]
    }
  }
}
```

### 응답 구성(체크아웃)

response config에는 이 checkout에서 사용 가능한 런타임 정보가 포함됩니다.

| Field                | Type   | Required | Description                                  |
| :------------------- | :----- | :------- | :------------------------------------------- |
| `environment`        | string | Yes      | 해당 checkout에 사용된 API 환경              |
| `business_id`        | string | Yes      | 비즈니스 식별자                              |
| `supported_networks` | array  | No       | 해당 거래에서 지원되는 카드 네트워크         |

#### 응답 구성 예시

```json
{
  "config": {
    "environment": "production",
    "business_id": "merchant_xyz789",
    "supported_networks": ["visa", "mastercard", "amex"]
  }
}
```

## 플랫폼 통합

### 사전 조건

이 핸들러를 사용하기 전에 플랫폼은 다음을 충족해야 합니다.

1. 사용자로부터 민감 결제 데이터를 수집하는
   **규정 준수형 보안 결제 자격증명 제공자**를 보유해야 합니다.
   이 서비스는 처리하는 결제 수단의 규제 요구사항(예: PCI DSS)을 충족해야 합니다.
2. 핸들러 구성에 정의된 특정 `endpoint`를 호출할 수 있는
   인증 자격증명(예: API Key)을 확보해야 합니다.

**Prerequisites Output:**

| Field                        | Description                                                                   |
| :--------------------------- | :---------------------------------------------------------------------------- |
| payment credential providers | 사용자 민감 결제 데이터를 수집하는 **규정 준수형** 보안 서비스               |
| Authentication credentials   | `/tokenize` 호출 인증용 API key 또는 OAuth token                             |

### 결제 프로토콜

#### 1단계: 핸들러 탐색

플랫폼은 processor tokenizer handler를 식별하고,
비즈니스의 구성 정보를 가져옵니다.

```json
{
  "ucp": {
    "payment_handlers": {
      "com.example.processor_tokenizer": [
        {
          "id": "processor_tokenizer",
          "version": "2026-01-11",
          "config": {
            "environment": "production",
            "business_id": "merchant_xyz789"
          }
        }
      ]
    }
  }
}
```

#### 2단계: 민감 데이터 수집

플랫폼의 **규정 준수형 보안 결제 자격증명 제공자**가
사용자의 민감 결제 데이터를 수집합니다
(예: 민감 결제 수단 정보가 플랫폼에 닿지 않도록 하는 규정 준수 결제 폼).

#### 3단계: 데이터 토큰화

플랫폼의 payment credential provider가 구성된 `endpoint`를 호출합니다.

**참고:** 핸들러 구성에 `identity` 객체가 포함된 경우,
credential provider는 이를 `binding` 객체에 **MUST** 주입해야 합니다.

Response:

```json
{
  "token": "tok_a1b2c3d4e5f6"
}
```

### 4단계: 체크아웃 완료

플랫폼은 토큰을 제출합니다.

```json
POST /checkout-sessions/{checkout_id}/complete
UCP-Agent: profile="https://platform.example/profile"
Content-Type: application/json

{
  "payment": {
    "instruments": [
      {
        "id": "instr_1",
        "handler_id": "processor_tokenizer",
        "type": "card",
        "selected": true,
        "display": {
          "brand": "visa",
          "last_digits": "1111",
          "expiry_month": 12,
          "expiry_year": 2026
        },
        "credential": {
          "type": "token",
          "token": "tok_a1b2c3d4e5f6"
        }
      }
    ]
  },
  "risk_signal": {
    // ... the key value pair for potential risk signal data
  }
}
```

---

## 구현 가이드

### 시나리오 A: 엔터프라이즈 구현(Self-Hosted)

* **역할:** 비즈니스가 이 명세를 구현합니다.
* **요구사항:**
    1. 자체 인프라에 `endpoint`를 배포
    2. 내부 DB에서 토큰과 PAN 매핑
* **보안:** **CRITICAL.** 카드 자격증명의 경우,
    비즈니스 endpoint에서 원본 PAN을 수신하므로
    비즈니스는 PCI DSS를 **MUST** 준수해야 합니다.
    다른 자격증명 타입도 각 타입별 규제 요건을 따릅니다.

### 시나리오 B: PSP 구현(Third-Party)

* **역할:** PSP가 이 명세를 구현합니다.
* **요구사항:**
    1. merchant에 `endpoint` URL 제공
    2. merchant에 `identity.access_token`(Merchant Secure Identifier) 발급
    3. 최종 결제 청구를 요청하는 merchant와 `binding.identity` 일치 여부 검증
* **보안:** 자격증명 저장 규제 준수 부담은 PSP가 담당
    (예: 카드의 경우 PCI DSS).

---

## 보안 고려사항

| Requirement | Description |
| :---------- | :---------- |
| **TLS/HTTPS** | `config.endpoint`로 향하는 모든 트래픽은 암호화되어야 하며 **MUST** TLS를 사용해야 합니다. |
| **Compliance** | `config.endpoint`를 호스팅하는 주체는 자격증명 타입별 관련 데이터 표준(예: 카드의 PCI DSS, PII의 GDPR 등)을 **MUST** 준수해야 합니다. |
| **Scope Isolation** | 플랫폼의 메인 애플리케이션은 원본 자격증명을 보지 않아야 하며 **MUST NOT** 접근해야 합니다. 플랫폼의 보안 credential provider와 Tokenizer Host만 접근할 수 있어야 합니다. |
| **Binding Validation** | Tokenizer/Processor는 최종 결제 시 제출된 `checkout_id`가 토큰화 시 제공된 `checkout_id`와 일치하는지 **MUST** 검증해야 합니다. |
