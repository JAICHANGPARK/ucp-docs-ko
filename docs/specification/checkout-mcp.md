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

# 체크아웃 기능 - MCP 바인딩

이 문서는 [Checkout Capability](checkout.md)의 Model Context Protocol(MCP) 바인딩을 정의합니다.

## 프로토콜 기본 사항

### 디스커버리

business는 `/.well-known/ucp`의 UCP 프로필을 통해 MCP 전송 지원 여부를 광고합니다.

```json
{
  "ucp": {
    "version": "2026-01-11",
    "services": {
      "dev.ucp.shopping": [
        {
          "version": "2026-01-11",
          "spec": "https://ucp.dev/specification/overview",
          "transport": "mcp",
          "schema": "https://ucp.dev/services/shopping/mcp.openrpc.json",
          "endpoint": "https://business.example.com/ucp/mcp"
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
      ]
    },
    "payment_handlers": {
      "com.example.vendor.delegate_payment": [
        {
          "id": "handler_1",
          "version": "2026-01-11",
          "spec": "https://example.vendor.com/specs/delegate-payment",
          "schema": "https://example.vendor.com/schemas/delegate-payment-config.json",
          "config": {}
        }
      ]
    }
  }
}
```

### 요청 메타데이터

MCP 클라이언트는 프로토콜 메타데이터를 담은 `meta` 객체를 모든 요청에
**반드시(MUST)** 포함해야 합니다.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://platform.example/profiles/shopping-agent.json"
        },
        "idempotency-key": "550e8400-e29b-41d4-a716-446655440000"
      },
      "checkout": { ... }
    }
  }
}
```

모든 요청에서 `meta["ucp-agent"]` 필드는
[capability negotiation](overview.md#negotiation-protocol)을 위해 **필수(required)** 입니다.
또한 `complete_checkout` 및 `cancel_checkout` 연산은 재시도 안전성을 위해
`meta["idempotency-key"]`를 요구합니다.
platform은 추가 메타데이터 필드를 포함할 수 있습니다(**MAY**).

## 도구(Tools)

UCP Capability는 MCP Tool과 1:1로 매핑됩니다.

### 식별자 패턴

MCP tool은 리소스 식별과 페이로드 데이터를 분리합니다.

* **요청(Requests):** 기존 checkout 대상 연산(`get`, `update`,
  `complete`, `cancel`)은 최상위 `id` 파라미터로 대상 리소스를 식별합니다.
  요청 페이로드의 `checkout` 객체에는 `id` 필드가 있으면 안 됩니다(**MUST NOT**).
* **응답(Responses):** 모든 응답은 전체 리소스 상태의 일부로 `checkout.id`를 포함합니다.
* **Create:** `create_checkout` 연산은 요청에 `id`가 필요 없고,
  응답에 새로 할당된 `checkout.id`가 포함됩니다.

| Tool | 연산 | 설명 |
| :------------------ | :------------------------------------------------- | :------------------------- |
| `create_checkout` | [Create Checkout](checkout.md#create-checkout) | checkout 세션 생성 |
| `get_checkout` | [Get Checkout](checkout.md#get-checkout) | checkout 세션 조회 |
| `update_checkout` | [Update Checkout](checkout.md#update-checkout) | checkout 세션 갱신 |
| `complete_checkout` | [Complete Checkout](checkout.md#complete-checkout) | 주문 확정 |
| `cancel_checkout` | [Cancel Checkout](checkout.md#cancel-checkout) | checkout 세션 취소 |

### `create_checkout`

[Create Checkout](checkout.md#create-checkout) 연산에 매핑됩니다.

#### 입력 스키마

* `checkout` ([Checkout](checkout.md#create-checkout)): **Required**.
  초기 checkout 세션 데이터와 선택 확장을 포함합니다.
  * 확장(선택):
    * `dev.ucp.shopping.buyer_consent`: [Buyer Consent](buyer-consent.md)
    * `dev.ucp.shopping.fulfillment`: [Fulfillment](fulfillment.md)
    * `dev.ucp.shopping.discount`: [Discount](discount.md)
    * `dev.ucp.shopping.ap2_mandate`: [AP2 Mandates](ap2-mandates.md)

#### 출력 스키마

* [Checkout](checkout.md#create-checkout) 객체

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "create_checkout",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            }
          },
          "checkout": {
            "buyer": {
              "email": "jane.doe@example.com",
              "first_name": "Jane",
              "last_name": "Doe"
            },
            "line_items": [
              {
                "item": {
                  "id": "item_123"
                },
                "quantity": 1
              }
            ],
            "currency": "USD",
            "fulfillment": {
              "methods": [
                {
                  "type": "shipping",
                  "destinations": [
                    {
                      "street_address": "123 Main St",
                      "address_locality": "Springfield",
                      "address_region": "IL",
                      "postal_code": "62701",
                      "address_country": "US"
                    }
                  ]
                }
              ]
            }
          }
        }
      }
    }
    ```

=== "Response"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "structuredContent": {
          "checkout": {
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
                "com.example.vendor.delegate_payment": [
                  {"id": "handler_1", "version": "2026-01-11", "config": {}}
                ]
              }
            },
            "id": "checkout_abc123",
            "status": "incomplete",
            "buyer": {
              "email": "jane.doe@example.com",
              "first_name": "Jane",
              "last_name": "Doe"
            },
            "line_items": [
              {
                "id": "item_123",
                "item": {
                  "id": "item_123",
                  "title": "Blue Jeans",
                  "price": 5000
                },
                "quantity": 1,
                "totals": [
                  {"type": "subtotal", "amount": 5000},
                  {"type": "total", "amount": 5000}
                ]
              }
            ],
            "currency": "USD",
            "totals": [
              {
                "type": "subtotal",
                "amount": 5000
              },
              {
                "type": "fulfillment",
                "display_text": "Shipping",
                "amount": 500
              },
              {
                "type": "total",
                "amount": 5500
              }
            ],
            "fulfillment": {
              "methods": [
                {
                  "id": "shipping_1",
                  "type": "shipping",
                  "line_item_ids": ["item_123"],
                  "selected_destination_id": "dest_home",
                  "destinations": [
                    {
                      "id": "dest_home",
                      "street_address": "123 Main St",
                      "address_locality": "Springfield",
                      "address_region": "IL",
                      "postal_code": "62701",
                      "address_country": "US"
                    }
                  ],
                  "groups": [
                    {
                      "id": "package_1",
                      "line_item_ids": ["item_123"],
                      "selected_option_id": "standard",
                      "options": [
                        {
                          "id": "standard",
                          "title": "Standard Shipping",
                          "description": "Arrives in 5-7 business days",
                          "totals": [
                            {
                              "type": "total",
                              "amount": 500
                            }
                          ]
                        },
                        {
                          "id": "express",
                          "title": "Express Shipping",
                          "description": "Arrives in 2-3 business days",
                          "totals": [
                            {
                              "type": "total",
                              "amount": 1000
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            "links": [
              {
                "type": "privacy_policy",
                "url": "https://business.example.com/privacy"
              },
              {
                "type": "terms_of_service",
                "url": "https://business.example.com/terms"
              }
            ],
            "continue_url": "https://business.example.com/checkout-sessions/checkout_abc123",
            "expires_at": "2026-01-11T18:30:00Z"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"checkout\":{\"ucp\":{...},\"id\":\"checkout_abc123\",...}}"
          }
        ]
      }
    }
    ```

### `get_checkout`

[Get Checkout](checkout.md#get-checkout) 연산에 매핑됩니다.

#### 입력 스키마

* `id` (String): **Required**. checkout 세션 ID.

#### 출력 스키마

* [Checkout](checkout.md#get-checkout) 객체.

### `update_checkout`

[Update Checkout](checkout.md#update-checkout) 연산에 매핑됩니다.

#### 입력 스키마

* `id` (String): **Required**. 갱신 대상 checkout 세션 ID.
* `checkout` ([Checkout](checkout.md#update-checkout)): **Required**.
  갱신할 checkout 세션 데이터를 포함합니다.
  * 확장(선택):
    * `dev.ucp.shopping.buyer_consent`: [Buyer Consent](buyer-consent.md)
    * `dev.ucp.shopping.fulfillment`: [Fulfillment](fulfillment.md)
    * `dev.ucp.shopping.discount`: [Discount](discount.md)
    * `dev.ucp.shopping.ap2_mandate`: [AP2 Mandates](ap2-mandates.md)

#### 출력 스키마

* [Checkout](checkout.md#update-checkout) 객체.

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 2,
      "method": "tools/call",
      "params": {
        "name": "update_checkout",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            }
          },
          "id": "checkout_abc123",
          "checkout": {
            "buyer": {
              "email": "jane.doe@example.com",
              "first_name": "Jane",
              "last_name": "Doe"
            },
            "line_items": [
              {
                "item": {
                  "id": "item_123"
                },
                "quantity": 1
              }
            ],
            "currency": "USD",
            "fulfillment": {
              "methods": [
                {
                  "id": "shipping_1",
                  "line_item_ids": ["item_123"],
                  "groups": [
                    {
                      "id": "package_1",
                      "selected_option_id": "express"
                    }
                  ]
                }
              ]
            }
          }
        }
      }
    }
    ```

=== "Response"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 2,
      "result": {
        "structuredContent": {
          "checkout": {
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
                "com.example.vendor.delegate_payment": [
                  {"id": "handler_1", "version": "2026-01-11", "config": {}}
                ]
              }
            },
            "id": "checkout_abc123",
            "status": "incomplete",
            "buyer": {
              "email": "jane.doe@example.com",
              "first_name": "Jane",
              "last_name": "Doe"
            },
            "line_items": [
              {
                "id": "item_123",
                "item": {
                  "id": "item_123",
                  "title": "Blue Jeans",
                  "price": 5000
                },
                "quantity": 1,
                "totals": [
                  {"type": "subtotal", "amount": 5000},
                  {"type": "total", "amount": 5000}
                ]
              }
            ],
            "currency": "USD",
            "totals": [
              {
                "type": "subtotal",
                "amount": 5000
              },
              {
                "type": "fulfillment",
                "display_text": "Shipping",
                "amount": 1000
              },
              {
                "type": "total",
                "amount": 6000
              }
            ],
            "fulfillment": {
              "methods": [
                {
                  "id": "shipping_1",
                  "type": "shipping",
                  "line_item_ids": ["item_123"],
                  "selected_destination_id": "dest_home",
                  "destinations": [
                    {
                      "id": "dest_home",
                      "street_address": "123 Main St",
                      "address_locality": "Springfield",
                      "address_region": "IL",
                      "postal_code": "62701",
                      "address_country": "US"
                    }
                  ],
                  "groups": [
                    {
                      "id": "package_1",
                      "line_item_ids": ["item_123"],
                      "selected_option_id": "express",
                      "options": [
                        {
                          "id": "standard",
                          "title": "Standard Shipping",
                          "description": "Arrives in 5-7 business days",
                          "totals": [
                            {
                              "type": "total",
                              "amount": 500
                            }
                          ]
                        },
                        {
                          "id": "express",
                          "title": "Express Shipping",
                          "description": "Arrives in 2-3 business days",
                          "totals": [
                            {
                              "type": "total",
                              "amount": 1000
                            }
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            "links": [
              {
                "type": "privacy_policy",
                "url": "https://business.example.com/privacy"
              },
              {
                "type": "terms_of_service",
                "url": "https://business.example.com/terms"
              }
            ],
            "continue_url": "https://business.example.com/checkout-sessions/checkout_abc123",
            "expires_at": "2026-01-11T18:30:00Z"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"checkout\":{\"ucp\":{...},\"id\":\"checkout_abc123\",...}}"
          }
        ]
      }
    }
    ```

### `complete_checkout`

[Complete Checkout](checkout.md#complete-checkout) 연산에 매핑됩니다.

#### 입력 스키마

* `meta` (Object): **Required**. 아래를 포함한 요청 메타데이터
  * `ucp-agent` (Object): **Required**. platform 에이전트 식별 정보
  * `idempotency-key` (String, UUID): **Required**. 재시도 안전성을 위한 고유 키
* `id` (String): **Required**. checkout 세션 ID
* `checkout` ([Checkout](checkout.md#complete-checkout)): **Required**.
  결제 자격증명과 최종 확정 데이터를 포함해 실제 거래를 실행합니다.

#### 출력 스키마

* [Checkout](checkout.md#complete-checkout) 객체. `order`에는 `id`와
  `permalink_url`만 포함된 partial order가 담깁니다.

### `cancel_checkout`

[Cancel Checkout](checkout.md#cancel-checkout) 연산에 매핑됩니다.

#### 입력 스키마

* `meta` (Object): **Required**. 아래를 포함한 요청 메타데이터
  * `ucp-agent` (Object): **Required**. platform 에이전트 식별 정보
  * `idempotency-key` (String, UUID): **Required**. 재시도 안전성을 위한 고유 키
* `id` (String): **Required**. checkout 세션 ID

#### 출력 스키마

* `status: canceled`를 갖는 [Checkout](checkout.md#cancel-checkout) 객체.

## 오류 처리

UCP는 프로토콜 오류와 비즈니스 결과를 구분합니다.
전체 오류 코드 레지스트리와 전송 바인딩 예시는
[Core Specification](overview.md#error-handling)을 참고하세요.

* **프로토콜 오류**: 인증/레이트리밋/서비스 불가처럼 요청 처리를 막는 전송 계층 실패.
  JSON-RPC `error`로 반환되며 코드 `-32000`(discovery 오류는 `-32001`)를 사용
* **비즈니스 결과**: 요청 처리 후의 애플리케이션 결과.
  UCP envelope과 `messages`를 포함한 JSON-RPC `result`로 반환

### 비즈니스 결과

비즈니스 결과(예: 상품 재고 부족)는 `structuredContent`에
UCP envelope과 `messages`를 담아 JSON-RPC `result`로 반환됩니다.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "structuredContent": {
      "checkout": {
        "ucp": {
          "version": "2026-01-11",
          "capabilities": {
            "dev.ucp.shopping.checkout": [{"version": "2026-01-11"}]
          }
        },
        "id": "checkout_abc123",
        "status": "incomplete",
        "line_items": [
          {
            "id": "item_456",
            "quantity": 100,
            "available_quantity": 12
          }
        ],
        "messages": [
          {
            "type": "warning",
            "code": "quantity_adjusted",
            "content": "Quantity adjusted, requested 100 units but only 12 available",
            "path": "$.line_items[0].quantity"
          }
        ],
        "continue_url": "https://merchant.com/checkout/checkout_abc123"
      }
    },
    "content": [
      {"type": "text", "text": "{\"checkout\":{\"ucp\":{...},\"id\":\"checkout_abc123\",...}}"}
    ]
  }
}
```

## 적합성(Conformance)

적합한 MCP 전송 구현은 다음을 **반드시(MUST)** 만족해야 합니다.

1. JSON-RPC 2.0 프로토콜을 올바르게 구현한다.
2. 이 명세에서 정의한 모든 핵심 checkout tool을 제공한다.
3. [Core Specification](overview.md#error-handling)에 따른 오류를 반환한다.
4. 비즈니스 결과를 UCP envelope 및 `messages` 배열이 포함된 JSON-RPC `result`로 반환한다.
5. tool 입력을 UCP 스키마에 맞춰 검증한다.
6. 스트리밍을 지원하는 HTTP 전송을 지원한다.

## 구현

UCP 연산은 [OpenRPC](https://open-rpc.org/)(JSON-RPC 스키마 형식)로 정의됩니다.
[MCP specification](https://modelcontextprotocol.io/)은 모든 tool 호출이
연산 이름과 인자를 `params` 안에 감싼 `tools/call` 메서드를 사용하도록 요구합니다.
구현체는 아래 변환을 **반드시(MUST)** 적용해야 합니다.

| OpenRPC  | MCP                |
|:---------|:-------------------|
| `method` | `params.name`      |
| `params` | `params.arguments` |

**파라미터 규칙:**

* `meta`: 요청 메타데이터
* `id`: 대상 리소스 식별자(path parameter와 동등)
* `checkout`: 도메인 페이로드(body와 동등)

**예시:** OpenRPC에서 `complete_checkout`가 다음과 같이 정의되어 있을 때:

```json
{
  "method": "complete_checkout",
  "params": {
    "meta": {
      "ucp-agent": { "profile": "https://..." },
      "idempotency-key": "550e8400-e29b-41d4-a716-446655440000"
    },
    "id": "checkout_abc123",
    "checkout": { "payment": {...} }
  }
}
```

구현체는 이를 MCP `tools/call` 엔드포인트로 아래처럼 노출해야 합니다(**MUST**).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "complete_checkout",
    "arguments": {
      "meta": {
        "ucp-agent": { "profile": "https://..." },
        "idempotency-key": "550e8400-e29b-41d4-a716-446655440000"
      },
      "id": "checkout_abc123",
      "checkout": { "payment": {...} }
    }
  }
}
```
