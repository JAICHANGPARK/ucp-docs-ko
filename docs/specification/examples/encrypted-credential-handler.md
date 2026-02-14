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

# 암호화 자격증명 핸들러

* **Handler Name:** `com.example.encrypted_credential`
* **Type:** Payment Handler Example

## 소개

이 예시는 **플랫폼이 자격증명을 비즈니스용으로 직접 암호화하는**
결제 핸들러를 보여줍니다.
토큰화 패턴과 달리 `/tokenize`, `/detokenize` endpoint가 없으며,
플랫폼의 규정 준수 credential vault가 비즈니스 공개키로 자격증명을 암호화하고,
비즈니스는 이를 로컬에서 복호화합니다.

이 패턴은 결제 시점 tokenizer 왕복 지연(round-trip latency)을
피하고 싶은 비즈니스에 적합합니다.

**참고:** 이 예시는 카드 자격증명(PCI DSS 필요)을 사용하지만,
암호화 패턴 자체는 **모든 자격증명 타입**에 적용 가능합니다.
규제 준수 요건은 자격증명 타입별로 달라집니다.

### 핵심 이점

* **런타임 왕복 없음:** 비즈니스가 로컬 복호화하므로 `/detokenize` 호출 불필요
* **단순한 아키텍처:** 토큰 저장/토큰-자격증명 매핑 불필요
* **비즈니스 키 주도:** 비즈니스가 자체 복호화 키를 관리

### 빠른 시작

| If you are a...                        | Start here                                    |
| :------------------------------------- | :-------------------------------------------- |
| **Business** accepting this handler    | [Business Integration](#business-integration) |
| **Platform** implementing this handler | [Platform Integration](#platform-integration) |

---

## 참여자

| Participant  | Role                                                                              | Prerequisites                 |
| :----------- | :-------------------------------------------------------------------------------- | :---------------------------- |
| **Business** | 공개키 등록, 암호화 자격증명 수신, 로컬 복호화                                   | Yes — 플랫폼 등록 필요        |
| **Platform** | 규정 준수 credential vault 운영, 비즈니스 공개키로 암호화                        | Yes — 암호화 구현 필요        |

### 패턴 플로우

```text
+-----------------+                              +------------+
|  Platform       |                              |  Business  |
|                 |                              |            |
+--------+--------+                              +------+-----+
         |                                              |
         |  1. Business registers public key (out-of-band)
         |<---------------------------------------------|
         |                                              |
         |  2. Confirmation                             |
         |--------------------------------------------->|
         |                                              |
         |  3. GET ucp.payment_handlers                 |
         |--------------------------------------------->|
         |                                              |
         |  4. Handler with business identity           |
         |<---------------------------------------------|
         |                                              |
         |  5. Platform's vaulting service encrypts     |
         |     credential with business's key           |
         |                                              |
         |  6. POST checkout with EncryptedCredential   |
         |--------------------------------------------->|
         |                                              |
         |       (Business decrypts locally)            |
         |                                              |
         |  7. Checkout complete                        |
         |<---------------------------------------------|
```

---

## 비즈니스 통합

### 사전 조건

#### 중요: 카드 자격증명은 규정 준수 필수

이 핸들러를 수락하기 전에,
비즈니스는 플랫폼에 공개 암호화 키를 등록해야 합니다.

checkout 시 비즈니스는 암호화된 `EncryptedCredential` payload만 수신하지만,
결제 처리를 위해 로컬에서 복호화하여 원본 자격증명을 얻습니다.
**카드 자격증명의 경우**, 비즈니스는 원본 PAN을 처리하게 되므로
PCI DSS를 **MUST** 준수해야 합니다. 여기에는 다음이 포함됩니다.

* 복호화 키의 안전한 키 관리
* 복호화 이후 원본 자격증명의 안전한 처리
* 카드의 경우 PAN 처리 관련 PCI DSS 전체 준수

**Prerequisites Output:**

| Field                   | Description                                                |
| :---------------------- | :--------------------------------------------------------- |
| `identity.access_token` | 온보딩 시 플랫폼이 할당한 비즈니스 식별자                 |
| Public key registered   | 플랫폼이 암호화용 비즈니스 공개키를 저장                  |

### 핸들러 구성

비즈니스는 플랫폼 handler를 광고합니다.
`business_id`는 암호화에 사용할 공개키를 조회하기 위한 비즈니스 식별자입니다.

지원되는 instrument schema는
[CardPaymentInstrument](https://ucp.dev/schemas/shopping/types/card_payment_instrument.json)만이며,
지원되는 checkout credential schema는 `EncryptedCredential`만,
지원되는 source credential schema는
[CardCredential](https://ucp.dev/schemas/shopping/types/card_credential.json)만입니다.

**참고:** `EncryptedCredential` 구조는
핸들러 선언의 `schema` 필드가 가리키는 handler schema에 정식 정의되어야 합니다.

**참고:** `CardCredential`에는 원본 PAN이 포함됩니다.
카드 자격증명의 경우,
플랫폼 vaulting service는 해당 자격증명 처리 시 PCI DSS를 **MUST** 준수해야 합니다.
비즈니스는 암호화 payload만 수신하지만,
카드 자격증명을 로컬 복호화하는 순간 PCI DSS 준수가 필요합니다.
다른 자격증명 타입은 각 타입별 규제 요건을 따릅니다.

#### 비즈니스 구성(디스커버리)

| Field           | Type   | Required | Description                                         |
| :-------------- | :----- | :------- | :-------------------------------------------------- |
| `environment`   | string | Yes      | API 환경 (`sandbox` 또는 `production`)              |
| `business_id`   | string | Yes      | 플랫폼이 할당한 비즈니스 식별자                     |
| `public_key_id` | string | Yes      | 등록된 비즈니스 공개키 식별자                       |

#### 비즈니스 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.example.platform_encrypted": [
        {
          "id": "platform_encrypted",
          "version": "2026-01-11",
          "spec": "https://platform.example.com/ucp/encrypted-handler.json",
          "schema": "https://platform.example.com/ucp/encrypted-handler/schema.json",
          "config": {
            "environment": "production",
            "business_id": "merchant_abc123",
            "public_key_id": "key_2026_01"
          }
        }
      ]
    }
  }
}
```

#### 응답 구성(체크아웃)

response config에는 사용된 암호화 정보가 포함됩니다.

| Field                  | Type   | Required | Description                           |
| :--------------------- | :----- | :------- | :------------------------------------ |
| `environment`          | string | Yes      | API 환경                              |
| `business_id`          | string | Yes      | 비즈니스 식별자                       |
| `encryption_algorithm` | string | Yes      | 사용 알고리즘 (예: `RSA-OAEP-256`)    |
| `key_id`               | string | Yes      | 암호화에 사용된 키 식별자             |

#### 응답 구성 예시

```json
{
  "config": {
    "environment": "production",
    "business_id": "merchant_abc123",
    "encryption_algorithm": "RSA-OAEP-256",
    "key_id": "key_2026_01"
  }
}
```

### 결제 처리

암호화 자격증명이 포함된 checkout을 수신하면 다음을 수행합니다.

1. **Validate Handler:** `instrument.handler_id`가 기대 handler ID와 일치하는지 확인
2. **Decrypt Credential:** 비즈니스 private key로 credential 복호화
3. **Verify Binding:** 복호화된 `checkout_id`가 현재 checkout과 일치하는지 확인
4. **Process Payment:** 복호화된 credential로 결제 처리
5. **Return Response:** 최종 checkout 상태 반환

---

## 플랫폼 통합

### 사전 조건

이 핸들러는 규정 준수 credential vault를 운영하고,
비즈니스용 자격증명 암호화를 수행할 수 있는 플랫폼이 구현합니다.
구현을 위해 플랫폼은 다음을 충족해야 합니다.

1. 자격증명 저장·처리 규정 준수 유지(예: 카드의 경우 PCI DSS)
2. 온보딩 시 비즈니스 공개키 저장
3. 핸들러 identity 기반으로 올바른 비즈니스 키를 사용해 암호화

**Implementation Requirements:**

| Requirement | Description                                                      |
| :---------- | :--------------------------------------------------------------- |
| Key storage | 비즈니스 identity와 공개키 매핑 관리                             |
| Encryption  | 비즈니스 공개키로 credential + binding context 암호화           |

### 핸들러 구성(플랫폼)

플랫폼은 UCP 프로필의 `payment_handlers` 레지스트리에서
`platform_config`를 사용해 이 핸들러를 광고합니다.

#### 플랫폼 구성(디스커버리)

| Field                  | Type   | Required | Description                                                |
| :--------------------- | :----- | :------- | :--------------------------------------------------------- |
| `environment`          | string | Yes      | API 환경 (`sandbox` 또는 `production`)                     |
| `platform_id`          | string | Yes      | 플랫폼 식별자                                              |
| `supported_algorithms` | array  | Yes      | 지원 암호화 알고리즘 (예: `['RSA-OAEP-256']`)             |

#### 플랫폼 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "com.example.platform_encrypted": [
        {
          "id": "platform_encrypted",
          "version": "2026-01-11",
          "spec": "https://platform.example.com/ucp/encrypted-handler.json",
          "schema": "https://platform.example.com/ucp/encrypted-handler/schema.json",
          "config": {
            "environment": "production",
            "platform_id": "platform_abc123",
            "supported_algorithms": ["RSA-OAEP-256", "RSA-OAEP-384"]
          }
        }
      ]
    }
  }
}
```

### 자격증명 암호화

플랫폼 애플리케이션은 결제 흐름을 오케스트레이션하지만,
**원본 자격증명에는 접근하지 않습니다**.
대신 다음 흐름으로 처리됩니다.

1. 플랫폼의 **규정 준수 vaulting service**가 사용자로부터 원본 credential 수신
2. vaulting service가 비즈니스 공개키로 credential과 binding context를 암호화
3. vaulting service가 암호화 payload를 플랫폼 애플리케이션에 반환
4. 플랫폼 애플리케이션이 checkout 제출에 이 암호화 payload 포함

이 분리 구조는 플랫폼 애플리케이션 자체가 원본 PAN을 처리하지 않도록 보장합니다.

### 체크아웃 제출

플랫폼 애플리케이션은 vaulting service에서 받은 암호화 credential로 checkout을 제출합니다.

```json
POST /checkout-sessions/{checkout_id}/complete
UCP-Agent: profile="https://platform.example/profile"
Content-Type: application/json

{
  "payment": {
    "instruments": [
      {
        "id": "instr_1",
        "handler_id": "platform_encrypted",
        "type": "card",
        "selected": true,
        "display": {
          "brand": "visa",
          "last_digits": "1111",
          "expiry_month": 12,
          "expiry_year": 2026
        },
        "credential": {
          "type": "encrypted",
          "encrypted_data": "base64-encoded-encrypted-payload..."
        }
      }
    ]
  },
  "risk_signals": {
    // ... the key value pair for potential risk signal data
  }
}
```

---

## 보안 고려사항

| Requirement | Description |
| :---------- | :---------- |
| **Compliance (Platform)** | 플랫폼 vaulting service는 원본 PAN을 처리하는 카드 시나리오에서 PCI DSS 등 자격증명 타입별 관련 표준을 **MUST** 준수해야 합니다. |
| **Compliance (Business)** | 비즈니스는 로컬에서 원본 자격증명 복호화·처리를 수행하므로 자격증명 타입별 관련 표준(예: 카드의 PCI DSS)을 **MUST** 준수해야 합니다. |
| **No platform app credential access** | 플랫폼 애플리케이션은 원본 자격증명을 **MUST NOT** 처리해야 하며, 규정 준수 vaulting service만 처리해야 합니다. |
| **Asymmetric encryption** | 플랫폼 credential vault는 비즈니스 공개키로 암호화하고, 비즈니스만 복호화할 수 있어야 합니다. |
| **Binding embedded** | 재사용 공격 방지를 위해 암호화 payload에는 `checkout_id`가 **MUST** 포함되어야 합니다. |
| **Key rotation** | 비즈니스는 키를 주기적으로 교체하는 것을 **SHOULD** 권장하며, 플랫폼은 키 업데이트를 지원해야 합니다. |
| **No credential storage** | 플랫폼은 암호화 credential을 저장하지 않으며, 암호화는 일방향 처리입니다. |
| **HTTPS required** | 모든 checkout 제출은 TLS를 사용해야 합니다. |

---

## 참고자료

* **Identity Schema:** `https://ucp.dev/schemas/shopping/types/payment_identity.json`
* **Instrument Schema:** `https://ucp.dev/schemas/shopping/types/card_payment_instrument.json`
