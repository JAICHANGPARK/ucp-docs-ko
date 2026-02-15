# 체크아웃 기능 - A2A 바인딩

이 문서는 [Checkout Capability](https://jaichangpark.github.io/ucp-docs-ko/specification/checkout/index.md)의 Agent2Agent Protocol(A2A) 바인딩을 명세합니다.

## 전송 디스커버리

A2A transport를 지원하는 비즈니스는 `/.well-known/ucp`의 UCP Profile 내 `services`에 agent card endpoint를 명시해야 합니다. 이를 통해 해당 기능을 지원하는 플랫폼이 A2A Protocol을 통해 비즈니스 서비스와 상호작용할 수 있습니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "services": {
      "dev.ucp.shopping": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "a2a",
          "endpoint": "https://example-business.com/.well-known/agent-card.json"
        }
      ]
    }
  }
}
```

## 쇼핑 에이전트 프로필 광고

비즈니스 에이전트와 상호작용하는 쇼핑 플랫폼은 모든 요청에서 `UCP-Agent` 요청 헤더로 자신의 profile URI를 전송해야 합니다.

```text
UCP-Agent: profile="https://agent.example/profiles/v2025-11/shopping-agent.json"
Content-Type: application/json
```

### 헤더 매핑 레퍼런스

다음 표는 A2A Agent가 플랫폼에 UCP 데이터 타입을 전달하기 위해 필요한 헤더를 정의합니다.

| Header Name        | Description                          |
| ------------------ | ------------------------------------ |
| `UCP-Agent`        | 쇼핑 플랫폼 애플리케이션 profile URI |
| `X-A2A-Extensions` | UCP Extension URI (아래 명시)        |

## 에이전트 간(A2A) 상호작용

A2A Protocol은 에이전트 간 통신의 강력한 기반을 제공합니다. [A2A extensions](https://a2a-protocol.org/latest/topics/extensions/)은 구조화된 데이터 타입을 사용한 에이전트 간 통신을 가능하게 합니다. 이를 통해 비즈니스는 플랫폼과의 통신에서 UCP 데이터 타입을 활용하는 AI 애플리케이션을 구축할 수 있습니다.

UCP A2A extension URI는 다음과 같습니다. `https://ucp.dev/specification/reference?v=2026-01-11`

UCP를 지원하는 비즈니스는 A2A Agent Card에 extension과 선택 capability를 광고해야 하며, 이를 통해 플랫폼이 extension을 활성화할 수 있어야 합니다.

예시:

```json
{
  "extensions": [
    {
      "uri": "https://ucp.dev/specification/reference?v=2026-01-11",
      "description": "Business agent supporting UCP",
      "params": {
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ],
          "dev.ucp.shopping.fulfillment": [
            {
              "version": "2026-01-11",
              "extends": "dev.ucp.shopping.checkout"
            }
          ]
        }
      }
    }
  ]
}
```

### 에이전트 간 협상

비즈니스 에이전트는 A2A `Message` 객체를 활용해 쇼핑 에이전트/플랫폼과 상호작용할 수 있습니다. 에이전트가 반환하는 A2A `Message` 객체는 메시지 내부 `DataPart`에 구조화 데이터를 담습니다. 플랫폼은 세션 내 후속 턴에서 현재 컨텍스트를 유지하기 위해, 비즈니스 에이전트가 생성한 `contextId`를 전달해야 합니다.

필요한 시나리오에서 비즈니스 에이전트는 A2A `Task` 객체를 사용할 수 있습니다. 이 경우 비즈니스 에이전트는 상호작용에 필요한 payload와 함께 `Task` 객체를 반환합니다. 플랫폼은 task 완료 전까지 후속 턴에 서버가 생성한 `taskId`와 `contextId`를 함께 전달해야 합니다.

플랫폼은 task가 종료 상태에 도달한 이후에도 동일 세션에서 추가 협상을 처리할 수 있어야 합니다 (예: 사용자가 주문 완료 후 동일 컨텍스트에서 추가 주문, 혹은 예외로 인해 task가 실패 상태가 된 경우). Task가 종료 상태에 도달하면, 플랫폼은 에이전트와 추가 상호작용을 위해 `taskId`를 초기화해야 하며, `contextId`는 후속 상호작용에서 재사용할 수 있습니다.

## 요청 멱등성

비즈니스 에이전트는 플랫폼 재시도로 인한 중복 메시지를 감지하기 위해, A2A `Message`의 `messageId`를 활용해야 합니다.

## 체크아웃 기능

Checkout capability는 소비자가 checkout 세션의 아이템을 관리하고 구매 절차를 완료할 수 있게 합니다. 비즈니스 에이전트는 일반적으로 이 기능 제공을 위해 비즈니스 checkout API와 연동합니다.

이 extension은 checkout 관련 액션, checkout 완료 또는 취소 시 비즈니스 에이전트가 Checkout 기능을 표현하는 데이터 스키마를 정의합니다. `Checkout` 엔터티는 A2A `Message`의 profile입니다. Checkout 엔터티는 UCP-A2A Extension을 활성화한 플랫폼으로 반드시 반환되어야 하며, A2A `Message`의 `DataPart`에 포함되어야 합니다. checkout 객체는 key `a2a.ucp.checkout`를 가진 `DataPart` 객체의 일부로 **MUST** 반환되어야 합니다.

**Request format:** 에이전트 애플리케이션은 사용자의 자연어 입력을 받아 의도를 파악하고, 필요 정보 협상을 거쳐 적절한 도구를 호출해 작업을 수행할 수 있습니다. 플랫폼 입력은 A2A `Message`로 원격 비즈니스 에이전트에 전달할 수 있습니다.

예시:

- 자연어 입력

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "add Pixel 10 Pro to my checkout"
      }
    ],
    "messageId": "69da8f87-991b-479e-80dc-ed92fcb57cbe",
    "kind": "message",
    "contextId": "aad14abc-4082-4748-84ca-4afff85aedfa"
  }
}
```

- 사용자 액션 기반 구조화 입력

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "data",
        "data": {
          "action": "add_to_checkout",
          "product_id": "PIXEL-10-PRO",
          "quantity": 1
        }
      }
    ],
    "messageId": "e94a8c10-69f4-4c4c-b988-21a298302da6",
    "kind": "message",
    "contextId": "aad14abc-4082-4748-84ca-4afff85aedfa"
  }
}
```

**Response format:** 다음은 Checkout 기능을 구현한 비즈니스 에이전트 응답 예시입니다.

```json
{
  "id": 33,
  "jsonrpc": "2.0",
  "result": {
    "contextId": "4629ea79-7201-4ece-bc7a-ce19fff76e61",
    "kind": "message",
    "messageId": "8e8566e0-6d7c-4f29-bd90-26a132385baa",
    "parts": [
      {
        "data": {
          "a2a.ucp.checkout": {...checkoutObject}
        },
        "kind": "data"
      }
    ],
    "role": "agent"
  }
}
```

### 체크아웃 완료

사용자가 결제할 준비가 되면 checkout 완료를 위해 `payment`를 비즈니스 에이전트에 제출해야 합니다. `payment`는 UCP에 정의된 구조화 데이터 타입입니다. 결제 처리 시 `payment`는 속성 이름 `a2a.ucp.checkout.payment`를 갖는 `DataPart`로 제출되어야 합니다. 연관 risk signal은 속성 이름 `a2a.ucp.checkout.risk_signals`로 전송해야 합니다.

checkout 완료 후, 비즈니스 에이전트는 `order` 속성(`id`, `permalink_url`)을 포함한 checkout 객체를 반환해야 합니다.

**Request format:**

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "data",
        "data": {"action":"complete_checkout"}
      },
      {
        "kind": "data",
        "data": {
          "a2a.ucp.checkout.payment": {
            ...paymentObject
          },
          "a2a.ucp.checkout.risk_signals":{...content}
        }
      }
    ],
    "messageId": "e94a8c10-69f4-4c4c-b988-21a298302da6",
    "kind": "message",
    "contextId": "aad14abc-4082-4748-84ca-4afff85aedfa"
  }
}
```

**Response format:** 다음은 Checkout 기능을 구현한 비즈니스 에이전트 응답 예시입니다.

```json
{
  "id": 33,
  "jsonrpc": "2.0",
  "result": {
    "contextId": "4629ea79-7201-4ece-bc7a-ce19fff76e61",
    "kind": "message",
    "messageId": "8e8566e0-6d7c-4f29-bd90-26a132385baa",
    "parts": [
      {
        "data": {
          "a2a.ucp.checkout": { ...checkoutObject }
        },
        "kind": "data"
      }
    ],
    "role": "agent"
  }
}
```

#### 에이피투(AP2) 기반 체크아웃 완료

비즈니스 에이전트는 에이전트 간 결제 상호작용에서 사용자 의도와 권한을 안전하게 교환할 수 있도록 AP2 mandates extension을 구현할 수 있습니다. UCP용 AP2 mandates extension을 지원하는 비즈니스는 UCP discovery 문서와 A2A agent card에 이를 명시해야 합니다. 플랫폼과 비즈니스 에이전트가 각 프로필에서 AP2 mandates extension을 광고하면, AP2 mandates extension은 암묵적으로 활성화된 것으로 간주됩니다.

AP2 mandates extension이 활성화되면, 비즈니스 에이전트는 checkout 객체에 대해 detached JWS를 생성하고, 생성된 서명을 `DataPart`의 `ap2.merchant_authorization`으로 반환해야 합니다. 이를 통해 플랫폼은 비즈니스 공개키를 사용해 checkout payload를 암호학적으로 검증할 수 있습니다.

```json
{
  "id": 33,
  "jsonrpc": "2.0",
  "result": {
    "contextId": "4629ea79-7201-4ece-bc7a-ce19fff76e61",
    "kind": "message",
    "messageId": "8e8566e0-6d7c-4f29-bd90-26a132385baa",
    "parts": [
      {
        "data": {
          "a2a.ucp.checkout": {
            ...checkoutObject,
            "ap2": {
              "merchant_authorization": "<detached jws signature>"
            }
          }
        },
        "kind": "data"
      }
    ],
    "role": "agent"
  }
}
```

사용자가 플랫폼에서 결제를 확정하면, 사용자 서명 checkout mandate와 payment mandate 객체를 checkout 완료를 위해 `DataPart`로 비즈니스 에이전트에 전송해야 합니다. payment mandate를 포함한 `payment`는 속성 이름 `a2a.ucp.checkout.payment`인 `DataPart`로 제출해야 하며, 서명된 checkout mandate는 `ap2.checkout_mandate`로 지정해야 합니다. `payment.instruments[*].credential`의 `token` 속성에는 payment mandate가 들어갑니다. checkout 완료를 위한 mandate 검증/처리 상세는 [AP2 Mandates Extension](https://jaichangpark.github.io/ucp-docs-ko/specification/ap2-mandates/index.md) 문서를 참고하세요.

**Request format:**

```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "data",
        "data": {
          "action": "complete_checkout"
        }
      },
      {
        "kind": "data",
        "data": {
          "a2a.ucp.checkout.payment": {
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
            "checkout_mandate": "eyJhbGciOiJFUz..."
          }
        }
      }
    ],
    "messageId": "e94a8c10-69f4-4c4c-b988-21a298302da6",
    "kind": "message",
    "contextId": "aad14abc-4082-4748-84ca-4afff85aedfa"
  }
}
```
