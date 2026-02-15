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

# {Handler Name} 결제 핸들러

* **핸들러 이름:** `{reverse-dns.name}`
* **버전:** `{YYYY-MM-DD}`

## 소개

{이 핸들러가 제공하는 기능과 지원하는 결제 흐름을 간단히 설명합니다.}

### 핵심 이점

* {이점 1}
* {이점 2}
* {이점 3}

### 통합 가이드

| 참여자 | 통합 섹션 |
| :----- | :-------- |
| **Business** | [Business Integration](#business-integration) |
| **Platform** | [Platform Integration](#platform-integration) |

---

## 참여자

{이 핸들러에 포함되는 모든 참여자와 역할을 설명합니다.}

> **용어 참고:**
> 이 명세에서는 참여자를 **"business"**로 표기하지만,
> 기술 스키마 필드는 업계 표준 명명인
> **`merchant_*`**(예: `merchant_id`)를 유지할 수 있습니다.
> 매핑은 아래에 문서화합니다.

| 참여자 | 역할 | 사전 요구사항 |
| :----- | :--- | :------------ |
| **Business** | {역할 설명} | {예/아니오 - 간단 설명} |
| **Platform** | {역할 설명} | {예/아니오 - 간단 설명} |
| **{Other Participant}** | {역할 설명} | {예/아니오 - 간단 설명} |

{선택 사항: 참여자 관계를 나타내는 ASCII 다이어그램}

```text
+---------+     +---------------+     +------------+
|Platform |     |   {Provider}  |     |  Business  |
+----+----+     +-------+-------+     +------+-----+
     |                  |                    |
     |  {step 1}        |                    |
     |----------------->|                    |
     |                  |                    |
     |  {step 2}        |                    |
     |<-----------------|                    |
     |                  |                    |
     |  {step 3}                             |
     |-------------------------------------->|
```

---

<!--
  PARTICIPANT INTEGRATION SECTIONS

  Include one section per participant. Each section follows the same structure:
  - Prerequisites (onboarding, setup)
  - Configuration or Protocol (what they need to do)
  - Examples

  Number sections starting from 3. Add more sections as needed for additional participants.
-->

## 비즈니스 통합(Business Integration)

### 사전 요구사항

비즈니스는 이 핸들러를 광고(advertise)하기 전에 다음을 **반드시(MUST)** 완료해야 합니다.

1. {사전 요구사항 1, 예: "{provider}에 등록하여 business 식별자를 발급받음"}
2. {사전 요구사항 2}

**사전 요구사항 결과:**

| 필드 | 설명 |
| :--- | :--- |
| `identity.access_token` | {할당되는 식별자, 예: business_id} |
| {additional config} | {온보딩에서 제공되는 추가 설정} |

### 핸들러 설정

비즈니스는 UCP 프로필의 `payment_handlers` 레지스트리에
이 핸들러 지원 정보를 게시합니다.

#### 핸들러 스키마

**스키마 URL:** `{schema_url}`

핸들러 스키마는 서로 다른 컨텍스트를 위한 3가지 설정 변형을 정의합니다.
전체 패턴은
[Payment Handler Guide: Defining the Schema](payment-handler-guide.md#defining-the-schema)
를 참고하세요.

| 설정 변형 | 컨텍스트 | 목적 |
| :-------- | :------- | :--- |
| `business_config` | 비즈니스 발견(discovery) | {비즈니스 전용 필드 설명} |
| `platform_config` | 플랫폼 발견(discovery) | {플랫폼 전용 필드 설명} |
| `response_config` | 체크아웃 응답 | {런타임 필드 설명} |

#### 비즈니스 구성(Business Config) 필드

| 필드 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| {field} | {type} | {Yes/No} | {description} |

#### 응답 구성(Response Config) 필드

| 필드 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| {field} | {type} | {Yes/No} | {설명 - 사용 가능한 instrument 등 런타임 필드 포함} |

#### 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "{handler_name}": [
        {
          "id": "{handler_id}",
          "version": "{version}",
          "spec": "{spec_url}",
          "schema": "{schema_url}",
          "config": {
            // Handler-specific configuration
          }
        }
      ]
    }
  }
}
```

### 결제 처리

비즈니스는 이 핸들러의 instrument로 결제를 수신하면 다음을 **반드시(MUST)** 수행해야 합니다.

1. **핸들러 검증:** `instrument.handler_id`가 광고된 핸들러와 일치하는지 확인합니다.
2. **멱등성 보장:** 요청이 재시도(`checkout_id` 또는 멱등 키가 기존 요청과 일치)인 경우,
  자금을 재처리하지 않고 이전 결과를 즉시 반환합니다.
3. **{단계 3}:** {설명}
4. **{단계 4}:** {설명}
5. **응답 반환:** 최종 확정된 체크아웃 상태를 반환합니다.

{비즈니스가 외부 서비스를 호출하는 경우 요청/응답 예시 포함}

---

## 플랫폼 통합(Platform Integration)

### 사전 요구사항

플랫폼은 이 핸들러를 사용하기 전에 다음을 **반드시(MUST)** 완료해야 합니다.

1. {사전 요구사항 1, 예: "{provider}에 등록하여 platform 식별자를 발급받음"}
2. {사전 요구사항 2}

**사전 요구사항 결과:**

| 필드 | 설명 |
| :--- | :--- |
| `identity.access_token` | {할당되는 식별자} |
| {additional config} | {온보딩에서 제공되는 추가 설정} |

### 핸들러 설정

플랫폼은 UCP 프로필의 `payment_handlers` 레지스트리에
`platform_config`를 사용해 이 핸들러 지원 정보를 게시합니다.

#### 플랫폼 구성(Platform Config) 필드

| 필드 | 타입 | 필수 | 설명 |
| :--- | :--- | :--- | :--- |
| {field} | {type} | {Yes/No} | {description} |

#### 플랫폼 핸들러 선언 예시

```json
{
  "ucp": {
    "version": "2026-01-11",
    "payment_handlers": {
      "{handler_name}": [
        {
          "id": "{handler_id}",
          "version": "{version}",
          "spec": "{spec_url}",
          "schema": "{schema_url}",
          "config": {
            // Platform-specific configuration
          }
        }
      ]
    }
  }
}
```

### 결제 프로토콜

플랫폼은 결제 instrument를 획득하기 위해 다음 흐름을 **반드시(MUST)** 따라야 합니다.

#### 1단계: 핸들러 탐색

플랫폼은 비즈니스의 UCP 프로필(`/.well-known/ucp`) `payment_handlers`
레지스트리에서 `{handler_name}`을 식별합니다.

```json
{
  "ucp": {
    "payment_handlers": {
      "{handler_name}": [
        {
          "id": "{handler_id}",
          "version": "{version}",
          "config": {
            // Business's configuration
          }
        }
      ]
    }
  }
}
```

#### 2단계: {작업 이름}

{이 단계에서 플랫폼이 수행하는 작업을 설명합니다.}

{해당 시 코드 예시 포함:}

```javascript
// Example SDK usage or API call
```

#### 3단계: {작업 이름}

{모든 단계에 대해 계속 작성...}

#### 마지막 단계: 체크아웃 완료

플랫폼은 구성된 결제 instrument를 사용해 체크아웃 완료를 제출합니다.

```json
POST /checkout-sessions/{checkout_id}/complete
Content-Type: application/json

{
  "payment": {
    "instruments": [
      {
        "id": "{instrument_id}",
        "handler_id": "{handler_id}",
        "type": "{instrument_type}",
        "credential": {
          "type": "{credential_type}",
          // Credential fields
        }
        // Additional instrument fields
      }
    ]
  },
  "risk_signals": {
    // risk signal objects here
  }
}
```

---

<!--
  ADDITIONAL PARTICIPANT SECTIONS

  Add one section per additional participant (PSP, Tokenizer, Wallet Provider, etc.)
  following the same pattern as Business and Platform integration.
-->

## {Participant} 통합

### 사전 요구사항

이 핸들러 흐름에 참여하기 전에 {participants}는 다음을 **반드시(MUST)** 완료해야 합니다.

1. {사전 요구사항 1}
2. {사전 요구사항 2}

**사전 요구사항 결과:**

| 필드 | 설명 |
| :--- | :--- |
| `identity.access_token` | {할당되는 식별자} |
| {additional config} | {온보딩에서 제공되는 추가 설정} |

### {Action or Configuration}

{이 참여자가 수행해야 할 작업을 설명합니다.}

{필요한 예시를 포함합니다.}

---

## 보안 고려사항

| 요구사항 | 설명 |
| :------- | :--- |
| **Binding required** | 재사용 방지를 위해 자격증명은 `checkout_id`와 `identity`에 **반드시(MUST)** 바인딩되어야 합니다. |
| **Binding placement** | 바인딩 데이터(예: `checkout_id`)는 전송 헤더가 아니라 서명 범위에 포함되도록 `credential` 페이로드 내부에 포함하는 것을 **권장(SHOULD)** 합니다. |
| **Binding verified** | 처리 참여자는 처리 전에 바인딩 일치 여부를 **반드시(MUST)** 검증해야 합니다. |
| **Token Expiry** | {토큰 사용 시: 토큰은 {duration} 이후 만료되거나 single-use여야 합니다.} |
| **Data Residency** | {로컬 법규 준수를 위해 PII를 특정 지역(예: EU, US)에서 처리/저장해야 하는지 명시합니다.} |
| **{Additional requirement}** | {설명} |

---

## 참고 자료

* **핸들러 명세:** `{spec_url}`
* **핸들러 스키마:** `{schema_url}` (config, instrument, credential 구조를 정의)
