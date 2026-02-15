# 토큰화 가이드

**OpenAPI:** [Tokenization API](https://ucp.dev/handlers/tokenization/openapi.json)

## 개요

이 가이드는 **토큰화 결제 핸들러를 구현하는 개발자**를 위한 문서입니다. 모든 토큰화 핸들러가 따라야 하는 공통 API, 보안 요구사항, 적합성(Conformance) 기준을 정의합니다.

**참고:** 이 가이드의 예시는 카드 자격증명을 사용하지만, 토큰화 패턴은 **모든 민감 자격증명 유형**(은행 계좌, 디지털 월렛, 멤버십 계정 등)에 적용할 수 있습니다. 준수 요구사항(예: 카드의 PCI DSS)은 자격증명 유형에 따라 달라집니다.

UCP에서 토큰화를 활용하는 다양한 예시는 다음과 같습니다.

| 예시                                                                                                                                    | 사용 사례                                          |
| --------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| [Processor Tokenizer](https://jaichangpark.github.io/ucp-docs-ko/specification/examples/processor-tokenizer-payment-handler/index.md)   | 비즈니스 또는 PSP가 토큰화와 결제 처리를 함께 수행 |
| [Platform Tokenizer](https://jaichangpark.github.io/ucp-docs-ko/specification/examples/platform-tokenizer-payment-handler/index.md)     | 플랫폼이 비즈니스/PSP를 위해 자격증명을 토큰화     |
| [Encrypted Credential Handler](https://jaichangpark.github.io/ucp-docs-ko/specification/examples/encrypted-credential-handler/index.md) | 플랫폼이 토큰화 대신 자격증명을 암호화             |

______________________________________________________________________

## 핵심 개념

### 자격증명 흐름 (Credential Flow)

토큰화 핸들러는 자격증명을 원본 형태에서 체크아웃 형태로 변환합니다.

```text
+-------------------------------------------------------------------------+
|                     Tokenization Payment Flow                           |
+-------------------------------------------------------------------------+
|                                                                         |
|   Platform has:            Tokenizer            Business receives:      |
|   Source Credential    -->  /tokenize  -->         TokenCredential      |
|                                                                         |
|   +-----------------+                      +-------------------------+  |
|   | source_         |                      | checkout_               |  |
|   | credentials     |    What goes IN      | credentials             |  |
|   |                 |<---------------      |                         |  |
|   | * card/fpan     |                      | What comes OUT          |  |
|   | * card/dpan     |                ----->| * token                 |  |
|   |                 |                      |                         |  |
|   +-----------------+                      +-------------------------+  |
|                                                                         |
+-------------------------------------------------------------------------+
```

토큰화 핸들러는 원본 자격증명(예: FPAN이 포함된 카드)을 받아 체크아웃 자격증명(예: 토큰)으로 생성합니다.

### 토큰 생명주기 (Token Lifecycle)

토큰은 여러 단계의 수명 주기를 거칩니다. 핸들러 명세에는 어떤 생명주기 정책을 사용하는지 반드시 문서화해야 합니다.

```text
+--------------+    +--------------+    +--------------+    +--------------+
|  Generation  |--->|   Storage    |--->| Detokenize   |--->| Invalidation |
|              |    |              |    |              |    |              |
|Platform calls|    | Tokenizer    |    | Business/PSP |    | Token expires|
| /tokenize    |    | holds token  |    | calls        |    | or is used   |
|              |    | -> credential|    | /detokenize  |    |              |
+--------------+    +--------------+    +--------------+    +--------------+
```

| 정책               | 설명                          | 사용 사례                         |
| ------------------ | ----------------------------- | --------------------------------- |
| **Single-use**     | 첫 detokenization 이후 무효화 | 가장 안전하며 기본 권장값         |
| **TTL-based**      | 고정 시간(예: 15분) 후 만료   | 일시적 장애 재시도 허용           |
| **Session-scoped** | 체크아웃 세션 동안 유효       | 다중 결제 시도가 있는 복잡한 흐름 |

### 바인딩 (Binding)

모든 토큰화 요청에는 토큰을 특정 컨텍스트에 묶는 `binding` 객체가 필요합니다.

| 필드          | 필수 여부 | 설명                                                    |
| ------------- | --------- | ------------------------------------------------------- |
| `checkout_id` | 예        | 이 토큰이 유효한 체크아웃 세션                          |
| `identity`    | 조건부    | 참가자 대리 호출 시 필수인 바인딩 대상 참가자 식별 정보 |

토크나이저는 `/detokenize`에서 바인딩 일치 여부를 **반드시(MUST)** 검증해야 합니다. [Binding Schema](https://ucp.dev/schemas/shopping/types/binding.json)를 참고하세요.

______________________________________________________________________

## OpenAPI

토큰화 핸들러는 두 개의 엔드포인트를 구현합니다. 아키텍처에 따라 하나만 또는 둘 다 구현할 수 있습니다. 암호화 페이로드 예시처럼 자체 암호화 메커니즘을 정의하여 둘 다 구현하지 않는 방식도 가능합니다.

### POST /tokenize

원본 자격증명을 체크아웃/식별 바인딩이 적용된 토큰으로 변환합니다.

**구현 시점:** 내부적으로 토큰을 생성하는 에이전트가 아니라면 기본적으로 구현합니다.

```json
POST /tokenize
Content-Type: application/json

{
  "credential": {
    "type": "card",
    "card_number_type": "fpan",
    "number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2026,
    "cvc": "123"
  },
  "binding": {
    "checkout_id": "abc123",
    "identity": {
      "access_token": "merchant_001"
    }
  }
}
```

**응답:**

```json
{
  "token": "tok_abc123xyz789"
}
```

### POST /detokenize

유효한 토큰에 대해 원본 자격증명을 반환합니다. 바인딩은 반드시 일치해야 합니다.

**구현 시점:** detokenization을 결제 처리와 결합한 구조(PSP 예시)라면 제외 가능, 그 외에는 구현합니다.

```json
POST /detokenize
Content-Type: application/json
Authorization: Bearer {caller_access_token}

{
  "token": "tok_abc123xyz789",
  "binding": {
    "checkout_id": "abc123"
  }
}
```

**응답:**

```json
{
  "type": "card",
  "card_number_type": "fpan",
  "number": "4111111111111111",
  "expiry_month": 12,
  "expiry_year": 2026,
  "cvc": "123"
}
```

**참고:** 인증된 호출자가 바인딩 대상과 동일하면 `binding.identity`는 생략합니다. 다른 참가자를 대신해 호출할 때(예: 비즈니스를 대신해 PSP가 detokenize)에는 포함해야 합니다.

전체 요청/응답 스키마는 [OpenAPI 명세](https://ucp.dev/handlers/tokenization/openapi.json)에서 확인하세요.

______________________________________________________________________

## 보안 요구사항

| 요구사항                     | 설명                                                                                               |
| ---------------------------- | -------------------------------------------------------------------------------------------------- |
| **Binding required**         | 재사용 방지를 위해 자격증명은 `checkout_id`와 참가자 `identity`에 **반드시(MUST)** 바인딩되어야 함 |
| **Binding verified**         | 자격증명 반환 전 토크나이저는 바인딩 일치 여부를 **반드시(MUST)** 검증해야 함                      |
| **Cryptographically random** | 예측 불가능한 토큰 생성을 위해 안전한 난수 생성기 사용                                             |
| **Sufficient length**        | 최소 128비트 엔트로피 확보                                                                         |
| **Non-reversible**           | 토큰으로부터 원본 자격증명을 역산할 수 없어야 함                                                   |
| **Scoped**                   | 토큰은 해당 토크나이저 범위 내에서만 유효해야 함                                                   |
| **Time-limited**             | 사용 사례에 맞는 TTL(일반적으로 5~30분) 강제                                                       |
| **Single-use preferred**     | 가능하면 첫 detokenization 이후 즉시 무효화                                                        |

______________________________________________________________________

## 핸들러 명세 요구사항

핸들러를 공개할 때, 명세 문서에는 다음 항목이 **반드시(MUST)** 포함되어야 합니다.

| 요구사항                        | 예시                                                  |
| ------------------------------- | ----------------------------------------------------- |
| **Unique handler name**         | `com.example.tokenization_payment` (reverse-DNS 형식) |
| **Endpoint URLs**               | 프로덕션/샌드박스 base URL                            |
| **Authentication requirements** | OAuth 2.0, API 키 등                                  |
| **Onboarding process**          | 참가자 등록 및 identity 발급 절차                     |
| **Accepted credentials**        | 토큰화를 지원하는 자격증명 유형                       |
| **Token lifecycle policy**      | Single-use, TTL, Session-scoped 중 무엇을 쓰는지      |
| **Security acknowledgements**   | 원본 자격증명을 받는 참가자의 보안 책임 수락 방식     |

### 명세 개요 예시

```markdown
**Handler Name:** `com.acme.tokenization_payment`
**OpenAPI:** [Tokenization API](https://ucp.dev/handlers/tokenization/openapi.json)

| Environment | Base URL                           |
| :---------- | :--------------------------------- |
| Production  | `https://api.acme.com/ucp`         |
| Sandbox     | `https://sandbox.api.acme.com/ucp` |

**Supported Instruments:**

| Instrument | Source Credentials           | Checkout Credentials |
| :--------- | :--------------------------- | :------------------- |
| `card`     | `card` (fpan, network_token) | `token`              |

**Token Lifecycle:** Single-use (invalidated after detokenization)

**Authentication:** OAuth 2.0 client credentials

**Onboarding:** Register at portal.acme.com. Businesses receive `access_token` for handler identity.
```

______________________________________________________________________

## 적합성 체크리스트

토크나이저 핸들러는 아래 조건을 만족하면 이 패턴에 적합합니다.

- 고유한 reverse-DNS `handler_name`과 함께, 안정적인 URL에 핸들러 명세를 공개한다.
- OpenAPI에 따라 `/tokenize` 및/또는 `/detokenize`를 구현한다.
- 인증 및 온보딩 요구사항을 정의한다.
- 원본 자격증명과 체크아웃 자격증명 간 변환 규칙을 문서화한다.
- `TokenCredential` 스키마와 호환되는 토큰을 생성한다.
- 토큰 생명주기 정책(TTL, single-use 등)을 명시한다.
- 토큰화 요청에 `checkout_id`를 포함한 `binding`을 요구한다.
- 참가자 식별에 `PaymentIdentity`를 사용한다.
- detokenization 요청에서 바인딩 일치 여부를 검증한다.
- 원본 자격증명을 받는 참가자에게 보안 책임 수락을 요구한다.

______________________________________________________________________

## 참고 자료

| 리소스                  | URL                                                                   |
| ----------------------- | --------------------------------------------------------------------- |
| Tokenization OpenAPI    | `https://ucp.dev/handlers/tokenization/openapi.json`                  |
| Identity Schema         | `https://ucp.dev/schemas/shopping/types/payment_identity.json`        |
| Binding Schema          | `https://ucp.dev/schemas/shopping/types/binding.json`                 |
| Token Credential Schema | `https://ucp.dev/schemas/shopping/types/token_credential.json`        |
| Card Instrument Schema  | `https://ucp.dev/schemas/shopping/types/card_payment_instrument.json` |

______________________________________________________________________

## 함께 보기

- **[Encrypted Credential Handler](https://jaichangpark.github.io/ucp-docs-ko/specification/examples/encrypted-credential-handler/index.md)**: tokenize/detokenize 왕복 대신 암호화를 사용하는 대안 패턴
- **[AP2 Mandates Extension](https://jaichangpark.github.io/ucp-docs-ko/specification/ap2-mandates/index.md)**: PSP 검증을 위한 체크아웃 합의의 암호학적 증명 확장
