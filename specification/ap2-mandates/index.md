# 에이피투(AP2) 위임 확장

## 개요

AP2 Mandates 확장은 **검증 가능한 디지털 자격증명(Verifiable Digital Credentials)** 을 사용해 사용자 의도와 승인 정보를 안전하게 교환할 수 있도록 합니다. 이는 표준 Shopping Service Checkout capability를 확장하여 **[AP2 Protocol](https://ap2-protocol.org/)** 을 지원합니다.

이 capability가 협상되어 활성화되면, 표준 checkout 세션은 암호학적으로 결합된 계약으로 전환됩니다.

- **Business**는 체크아웃 응답에 암호학적 서명을 **반드시(MUST)** 포함해야 하며, 이를 통해 약관(가격, 라인 아이템)의 진위를 증명해야 합니다.
- **Platform**은 `complete` 작업 시 암호학적으로 서명된 증명(Mandate)을 **반드시(MUST)** 제공해야 하며, 이를 통해 사용자가 특정 checkout 상태와 자금 이체를 명시적으로 승인했음을 증명해야 합니다.

**보안 바인딩(Security Binding):** capability 교집합에서 이 확장이 협상되면, 해당 세션은 **Security Locked** 상태가 됩니다. 어느 쪽도 표준(비보호) checkout 흐름으로 되돌릴 수 없습니다.

### 설계

AP2 전용 필드는 요청/응답 모두에서 `ap2` 객체 아래에 중첩됩니다. 이 설계는 다음을 제공합니다.

- **스키마 모듈성** - 기본 checkout 스키마를 깔끔하게 유지하고, AP2는 단일 필드로 데이터를 확장
- **일관된 정규화(canonicalization)** - 규칙 하나: business 서명 계산에서 `ap2` 제외. 이후 AP2 필드가 추가되어도 자동으로 처리
- **확장 공존성** - 여러 보안 확장이 네임스페이스 충돌 없이 공존 가능
- **Capability 신호** - `ap2` 객체 존재 자체가 AP2 활성화 상태를 명확히 표시

## 탐색(Discovery) 및 협상(Negotiation)

이 확장은 표준 UCP 협상 프로토콜을 따릅니다. business와 platform 양측 capability의 **교집합(Capability Intersection)** 에 나타날 때만 활성화됩니다.

### 비즈니스 프로필 광고

business는 `/.well-known/ucp`의 `capabilities` 목록에 `dev.ucp.shopping.ap2_mandate`를 추가하여 지원을 선언합니다.

**Business Profile 예시:**

```json
{
  "capabilities": {
    "dev.ucp.shopping.checkout": [
      {
        "version": "2026-01-11",
        "spec": "https://ucp.dev/specification/checkout",
        "schema": "https://ucp.dev/schemas/shopping/checkout.json"
      }
    ],
    "dev.ucp.shopping.ap2_mandate": [
      {
        "version": "2026-01-11",
        "spec": "https://ucp.dev/specification/ap2-mandates",
        "schema": "https://ucp.dev/schemas/shopping/ap2_mandate.json",
        "extends": "dev.ucp.shopping.checkout",
        "config": {
          "vp_formats_supported": {
            "dc+sd-jwt": { }
          }
        }
      }
    ]
  }
}
```

### 플랫폼 프로필 광고

platform도 자신의 프로필에서 지원을 선언합니다. platform이 trusted platform provider 모델로 동작한다면, platform은 프로필 최상위 `signing_keys` 배열에 최소 1개 이상의 키를 **반드시(MUST)** 제공해야 합니다.

### 활성화 및 세션 잠금

1. platform이 자신의 프로필 URI를 광고합니다(전송 방식별 메커니즘).
1. business가 프로필을 조회하고 교집합을 계산합니다.
1. 교집합에 `dev.ucp.shopping.ap2_mandate`가 존재하면:
1. business는 모든 checkout 응답에 `ap2.merchant_authorization`을 **반드시(MUST)** 포함해야 합니다.
1. business는 `ap2.checkout_mandate`가 없는 `complete_checkout` 요청을 **반드시 수락하면 안 됩니다(MUST NOT)**.
1. platform은 사용자에게 checkout을 제시하기 전에 business 서명을 **반드시(MUST)** 검증해야 합니다.

### 서명 키 요구사항

이 확장을 사용하려면 business가 mandate 서명을 검증할 수 있는 공개 서명 키가 **반드시(MUST)** 확보되어야 합니다.

- **Platform Provider 흐름:** platform 프로필의 `signing_keys`에 키 제공
- **User Credential 흐름:** 디지털 결제 자격증명에 키 바인딩

공개 키를 확인할 수 없거나 서명이 유효하지 않으면 business는 오류를 **반드시(MUST)** 반환해야 합니다.

## 암호학 요구사항

### 서명 알고리즘

모든 서명은 아래 알고리즘 중 하나를 **반드시(MUST)** 사용해야 합니다.

| 알고리즘 | 설명                                                    |
| -------- | ------------------------------------------------------- |
| `ES256`  | P-256 곡선 + SHA-256 기반 ECDSA (**권장(RECOMMENDED)**) |
| `ES384`  | P-384 곡선 + SHA-384 기반 ECDSA                         |
| `ES512`  | P-521 곡선 + SHA-512 기반 ECDSA                         |

### 비즈니스 승인(Business Authorization)

business는 checkout 응답 본문의 `ap2.merchant_authorization`에 **JWS Detached Content** 형식 ([RFC 7515 Appendix F](https://datatracker.ietf.org/doc/html/rfc7515#appendix-F)) 으로 서명을 **반드시(MUST)** 포함해야 합니다.

**서명이 포함된 Checkout 응답 예시:**

```json
{
  "id": "chk_abc123",
  "status": "ready_for_complete",
  "currency": "USD",
  "line_items": [...],
  "totals": [...],
  "ap2": {
    "merchant_authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6Im1lcmNoYW50XzIwMjUifQ..<signature>"
  }
}
```

`merchant_authorization` 값은 `<header>..<signature>` 형식의 detached payload JWS입니다. 점 두 개(`..`)는 payload가 분리 전송되며(즉 checkout 본문 자체), JWS 내부에는 포함되지 않음을 의미합니다.

**JWS 헤더 클레임:**

| 클레임 | 타입   | 필수 | 설명                                       |
| ------ | ------ | ---- | ------------------------------------------ |
| `alg`  | string | Yes  | 서명 알고리즘 (`ES256`, `ES384`, `ES512`)  |
| `kid`  | string | Yes  | business의 `signing_keys`를 참조하는 키 ID |

**서명 계산:**

서명은 JWS 헤더와 checkout payload를 모두 **반드시(MUST)** 포함해야 합니다. 이는 공격자가 `alg` 클레임을 변경해도 서명이 유효하게 남는 알고리즘 대체 공격을 방지합니다.

```text
sign_checkout(checkout, private_key, kid, alg="ES256"):
    // Extract payload (checkout minus ap2)
    payload = checkout without "ap2" field

    // Canonicalize using JCS (RFC 8785)
    canonical_bytes = jcs_canonicalize(payload)

    // Create protected header
    header = {"alg": alg, "kid": kid}
    encoded_header = base64url_encode(json_encode(header))

    // Sign header + payload per JWS
    signing_input = encoded_header + "." + base64url_encode(canonical_bytes)
    signature = sign(signing_input, private_key, alg)

    // Return detached JWS (header..signature, no payload)
    checkout.ap2.merchant_authorization = encoded_header + ".." + base64url_encode(signature)
    return checkout
```

### 위임(Mandate) 구조

mandate는 Key Binding(`+kb`)이 포함된 **SD-JWT** 자격증명입니다. platform은 서로 구분되는 두 가지 mandate 아티팩트를 **반드시(MUST)** 생성해야 합니다.

| Mandate              | UCP 배치 위치                             | 목적                                         |
| -------------------- | ----------------------------------------- | -------------------------------------------- |
| **checkout_mandate** | `ap2.checkout_mandate`                    | checkout 약관에 바인딩된 증명, business 보호 |
| **payment_mandate**  | `payment.instruments[*].credential.token` | 결제 승인에 바인딩된 증명, 자금 보호         |

checkout mandate는 `ap2.merchant_authorization` 필드를 포함한 전체 checkout 응답을 **반드시(MUST)** 포함해야 합니다. 이를 통해 platform 서명이 business 서명을 다시 감싸는 중첩된 암호학적 바인딩이 형성됩니다.

**명세 경계(Specification Boundary):** 이 확장은 mandate를 UCP 요청/응답 어디에 두는지(*where*)를 정의합니다. mandate 자격증명 구조(claim, 선택적 공개, key binding)는 [AP2 Protocol Specification](https://ap2-protocol.org/specification)에서 정의합니다.

### 정규화(Canonicalization)

JSON payload 서명 계산 시 구현체는 [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785)에서 정의한 **JSON Canonicalization Scheme (JCS)** 를 **반드시(MUST)** 사용해야 합니다.

JCS는 JSON 데이터를 바이트 단위로 결정론적 표현으로 만들어, 공백/키 순서/유니코드 정규화 차이와 관계없이 서명 검증을 가능하게 합니다.

**정규화 규칙:** business 서명 계산 시 `ap2` 필드를 전체 제외합니다. 이 규칙은 향후 AP2 필드 확장을 자동으로 수용합니다.

## 위임(Mandate) 흐름

`dev.ucp.shopping.ap2_mandate` capability가 협상되면 세션은 아래 흐름으로 고정됩니다. 암호학적 무결성을 위해 양측은 이 단계를 **반드시(MUST)** 준수해야 하며, 단계를 우회하거나 mandate 없는 완료 요청을 제출하려는 시도는 세션 실패로 **반드시(MUST)** 처리되어야 합니다.

### 1단계: 체크아웃 생성 및 서명

platform이 세션을 시작합니다. business는 응답 본문에 `ap2.merchant_authorization`이 포함된 `Checkout` 객체를 반환합니다.

| Name         | Type          | Required | Description                                                                                                                                                                                                                                                     |
| ------------ | ------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ucp          | any           | **Yes**  | UCP metadata for checkout responses.                                                                                                                                                                                                                            |
| id           | string        | **Yes**  | Unique identifier of the checkout session.                                                                                                                                                                                                                      |
| line_items   | Array[object] | **Yes**  | List of line items being checked out.                                                                                                                                                                                                                           |
| buyer        | object        | No       | Representation of the buyer.                                                                                                                                                                                                                                    |
| status       | string        | **Yes**  | Checkout state indicating the current phase and required action. See Checkout Status lifecycle documentation for state transition details. **Enum:** `incomplete`, `requires_escalation`, `ready_for_complete`, `complete_in_progress`, `completed`, `canceled` |
| currency     | string        | **Yes**  | ISO 4217 currency code reflecting the merchant's market determination. Derived from address, context, and geo IP—buyers provide signals, merchants determine currency.                                                                                          |
| totals       | Array[object] | **Yes**  | Different cart totals.                                                                                                                                                                                                                                          |
| messages     | Array[object] | No       | List of messages with error and info about the checkout session state.                                                                                                                                                                                          |
| links        | Array[object] | **Yes**  | Links to be displayed by the platform (Privacy Policy, TOS). Mandatory for legal compliance.                                                                                                                                                                    |
| expires_at   | string        | No       | RFC 3339 expiry timestamp. Default TTL is 6 hours from creation if not sent.                                                                                                                                                                                    |
| continue_url | string        | No       | URL for checkout handoff and session recovery. MUST be provided when status is requires_escalation. See specification for format and availability requirements.                                                                                                 |
| payment      | object        | No       | Payment configuration containing handlers.                                                                                                                                                                                                                      |
| order        | object        | No       | Details about an order created for this checkout session.                                                                                                                                                                                                       |
| ap2          | any           | No       |                                                                                                                                                                                                                                                                 |

**응답 예시:**

```json
{
  "id": "chk_abc123",
  "status": "ready_for_complete",
  "currency": "USD",
  "line_items": [
    {
      "id": "li_1",
      "item": {"id": "item_123", "title": "Widget", "price": 2500},
      "quantity": 2,
      "totals": [
        {"type": "subtotal", "amount": 5000},
        {"type": "total", "amount": 5000}
      ]
    }
  ],
  "totals": [
    {"type": "subtotal", "amount": 5000},
    {"type": "tax", "amount": 400},
    {"type": "total", "amount": 5400}
  ],
  "ap2": {
    "merchant_authorization": "eyJhbGciOiJFUzI1NiIsImtpZCI6Im1lcmNoYW50XzIwMjUifQ..<signature>"
  }
}
```

platform은 이 서명을 **반드시(MUST)** 검증해야 합니다.

```text
verify_merchant_authorization(checkout, merchant_profile):
    // Parse detached JWS (header..signature)
    jws = checkout.ap2.merchant_authorization
    [encoded_header, empty, encoded_signature] = jws.split(".")

    // Decode and validate header
    header = json_decode(base64url_decode(encoded_header))
    assert header.alg in ["ES256", "ES384", "ES512"]

    // Reconstruct signed payload (checkout minus ap2)
    payload = checkout without "ap2" field
    canonical_bytes = jcs_canonicalize(payload)

    // Reconstruct signing input (header + payload)
    signing_input = encoded_header + "." + base64url_encode(canonical_bytes)

    // Get business's public key and verify
    public_key = get_key_by_kid(merchant_profile.signing_keys, header.kid)
    return verify(encoded_signature, signing_input, public_key, header.alg)
```

### 2단계: 사용자 동의 및 위임 생성

사용자가 구매를 확정하면, platform은 암호학적으로 검증 가능한 mandate 생성을 **반드시(MUST)** 유도해야 합니다.

#### 옵션 1: Trusted Platform Provider

trusted platform provider가 사용자를 대리해 mandate 자격증명을 생성합니다. platform provider는 신뢰 가능한 결정적 채널에서의 명시적 사용자 동의 없이 mandate가 생성되지 않도록 **반드시(MUST)** 보장해야 합니다.

사용자 동의 후 platform은 서버 측 키로 mandate에 서명합니다. business는 platform 서명이 사용자 동의를 의미한다고 신뢰합니다.

#### 옵션 2: 디지털 결제 자격증명

이 모델에서는 사용자가 business가 신뢰하는 발급원(예: 은행/네트워크 발급 결제 자격증명)의 VDC를 보유합니다.

platform은 OpenID4VP 같은 프로토콜을 통해 프레젠테이션을 요청합니다. 사용자 지갑(또는 동등한 컴포넌트)은 요청을 처리하고 결제 자격증명에 연결된 개인키로 mandate에 서명합니다.

business는 자격증명 발급자(은행)를 신뢰하고 사용자 Key Binding(+kb) 서명을 검증합니다.

### 3단계: 제출(`complete_checkout`)

mandate 생성이 완료되면 platform은 완료 요청에 mandate를 포함해 제출합니다.

| Name             | Type                                                                          | Required | Description                                      |
| ---------------- | ----------------------------------------------------------------------------- | -------- | ------------------------------------------------ |
| checkout_mandate | [Checkout Mandate](/ucp-docs-ko/specification/ap2-mandates/#checkout-mandate) | No       | SD-JWT+kb proving user authorized this checkout. |

```json
{
  "payment": {
    "instruments": [
      {
        "id": "instr_1",
        "handler_id": "gpay_1234",
        "type": "card",
        "selected": true,
        "display": {
          "description": "Visa •••• 1234",
        },
        "billing_address": {
          "street_address": "123 Main St",
          "address_locality": "Anytown",
          "address_region": "CA",
          "address_country": "US",
          "postal_code": "12345"
        },
        "credential": {
          "type": "PAYMENT_GATEWAY",
          "token": "examplePaymentMethodToken"
        }
      }
    ]
  },
  "ap2": {
    "checkout_mandate": "eyJhbGciOiJFUzI1NiIsInR5cCI6InZjK3NkLWp3dCJ9..." // The User-Signed SD-JWT+kb / platform provider signed SD-JWT / delegated SD-JWT-KB
  }
}
```

- `ap2.checkout_mandate`: 전체 checkout(`ap2.merchant_authorization` 포함)을 담은 SD-JWT+kb checkout mandate
- `payment.instruments[*].credential.token`: payment mandate가 포함된 토큰(composite token)

## 검증 및 처리

### 비즈니스 검증

business는 `complete` 요청 수신 시 다음을 **반드시(MUST)** 수행해야 합니다.

1. **협상 강제:** AP2가 협상된 경우 `ap2.checkout_mandate`가 없으면 `mandate_required` 오류 코드로 요청을 거부합니다.

**Mandate 검증(AP2 명세 기준):**

1. **Mandate 검증:** [AP2 Protocol Specification](https://ap2-protocol.org/specification)에 따라 SD-JWT 서명, key binding, 만료를 검증합니다.
1. **내장 Checkout 추출:** 검증된 mandate claim에서 checkout 객체를 추출합니다.

**UCP 검증:**

1. **Business Authorization 검증:** 내장 checkout의 `ap2.merchant_authorization`이 business 자신의 유효한 서명인지 확인합니다.

```text
jws = embedded_checkout.ap2.merchant_authorization
[encoded_header, _, encoded_signature] = jws.split(".")
header = json_decode(base64url_decode(encoded_header))

payload = embedded_checkout without "ap2" field
signing_input = encoded_header + "." + base64url_encode(jcs_canonicalize(payload))

my_key = get_key_by_kid(my_signing_keys, header.kid)
verify(encoded_signature, signing_input, my_key, header.alg)
```

1. **약관 일치 검증:** 내장 checkout 약관(id, totals, line items)이 현재 세션 상태와 일치하는지 확인합니다.

### 피에스피(PSP) 검증

business는 `token`(복합 객체)을 Payment Handler/PSP로 전달합니다. PSP는 [AP2 Protocol Specification](https://ap2-protocol.org/specification)에 따라 `payment_mandate`를 검증하며, 여기에는 서명 검증, 만료 확인, checkout 상관관계 검증이 포함됩니다.

## 스키마

### 비즈니스 승인(Business Authorization)

JWS Detached Content signature (RFC 7515 Appendix F) over the checkout response body (excluding ap2 field). Format: `<base64url-header>..<base64url-signature>`. The header MUST contain 'alg' (ES256/ES384/ES512) and 'kid' claims. The signature covers both the header and JCS-canonicalized checkout payload.

**Pattern:** `^[A-Za-z0-9_-]+\.\.[A-Za-z0-9_-]+$`

### 에이피투(AP2) 체크아웃 응답

checkout 응답에 포함되는 `ap2` 객체입니다.

| Name                   | Type                                                                                      | Required | Description                                                |
| ---------------------- | ----------------------------------------------------------------------------------------- | -------- | ---------------------------------------------------------- |
| merchant_authorization | [Merchant Authorization](/ucp-docs-ko/specification/ap2-mandates/#merchant-authorization) | No       | Merchant's signature proving checkout terms are authentic. |

### 체크아웃 위임(Checkout Mandate)

SD-JWT+kb credential in `ap2.checkout_mandate`. Proving user authorization for the checkout. Contains the full checkout including `ap2.merchant_authorization`.

**Pattern:** `^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+(~[A-Za-z0-9_-]+)*$`

### 에이피투(AP2) 완료 요청

COMPLETE checkout 요청에 포함되는 `ap2` 객체입니다.

| Name             | Type                                                                          | Required | Description                                      |
| ---------------- | ----------------------------------------------------------------------------- | -------- | ------------------------------------------------ |
| checkout_mandate | [Checkout Mandate](/ucp-docs-ko/specification/ap2-mandates/#checkout-mandate) | No       | SD-JWT+kb proving user authorized this checkout. |

### 오류 코드

Error codes specific to AP2 mandate verification.

**Enum:** `mandate_required`, `agent_missing_key`, `mandate_invalid_signature`, `mandate_expired`, `mandate_scope_mismatch`, `merchant_authorization_invalid`, `merchant_authorization_missing`

| 오류 코드                        | 설명                                                    |
| -------------------------------- | ------------------------------------------------------- |
| `mandate_required`               | AP2가 협상되었지만 요청에 `ap2.checkout_mandate`가 없음 |
| `agent_missing_key`              | platform 프로필에 유효한 `signing_keys` 항목이 없음     |
| `mandate_invalid_signature`      | mandate 서명을 검증할 수 없음                           |
| `mandate_expired`                | mandate `exp` 타임스탬프가 만료됨                       |
| `mandate_scope_mismatch`         | mandate가 다른 checkout에 바인딩되어 있음               |
| `merchant_authorization_invalid` | business authorization 서명을 검증할 수 없음            |
