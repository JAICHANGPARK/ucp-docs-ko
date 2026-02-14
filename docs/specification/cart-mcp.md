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

# 장바구니 기능 - MCP 바인딩

이 문서는 [Cart Capability](cart.md)의 Model Context Protocol(MCP) 바인딩을 정의합니다.

## 프로토콜 기본 사항

### 디스커버리

business는 `/.well-known/ucp`의 UCP 프로필을 통해 MCP 전송 사용 가능 여부를 광고합니다.

```json
{
  "ucp": {
    "version": "2026-01-15",
    "services": {
      "dev.ucp.shopping": {
        "version": "2026-01-15",
        "spec": "https://ucp.dev/specification/overview",
        "mcp": {
          "schema": "https://ucp.dev/services/shopping/mcp.openrpc.json",
          "endpoint": "https://business.example.com/ucp/mcp"
        }
      }
    },
    "capabilities": [
      {
        "name": "dev.ucp.shopping.checkout",
        "version": "2026-01-11",
        "spec": "https://ucp.dev/specification/checkout",
        "schema": "https://ucp.dev/schemas/shopping/checkout.json"
      },
      {
        "name": "dev.ucp.shopping.cart",
        "version": "2026-01-15",
        "spec": "https://ucp.dev/specification/cart",
        "schema": "https://ucp.dev/schemas/shopping/cart.json"
      }
    ]
  }
}
```

### 요청 메타데이터

MCP 클라이언트는 모든 요청에 프로토콜 메타데이터를 담은 `meta` 객체를
**반드시(MUST)** 포함해야 합니다.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "create_cart",
    "arguments": {
      "meta": {
        "ucp-agent": {
          "profile": "https://platform.example/profiles/shopping-agent.json"
        }
      },
      "cart": { ... }
    }
  }
}
```

모든 요청에서 `meta["ucp-agent"]` 필드는
[capability negotiation](overview.md#negotiation-protocol)을 위해 **필수(required)** 입니다.
platform은 추가 메타데이터 필드를 포함할 수 있습니다(**MAY**).

## 도구(Tools)

UCP Capability는 MCP Tool과 1:1로 매핑됩니다.

### 식별자 패턴

MCP tool은 리소스 식별과 페이로드 데이터를 분리합니다.

* **요청(Requests):** 기존 cart 대상 연산(`get`, `update`, `cancel`)은
  최상위 `id` 파라미터로 대상 리소스를 식별합니다.
  요청 페이로드의 `cart` 객체에는 `id` 필드가 있으면 안 됩니다(**MUST NOT**).
* **응답(Responses):** 모든 응답은 전체 리소스 상태의 일부로 `cart.id`를 포함합니다.
* **Create:** `create_cart` 연산은 요청에 `id`가 필요 없으며,
  응답에 새로 할당된 `cart.id`가 포함됩니다.

| Tool | 연산 | 설명 |
| :--- | :--- | :--- |
| `create_cart` | [Create Cart](cart.md#create-cart) | cart 세션 생성 |
| `get_cart` | [Get Cart](cart.md#get-cart) | cart 세션 조회 |
| `update_cart` | [Update Cart](cart.md#update-cart) | cart 세션 갱신 |
| `cancel_cart` | [Cancel Cart](cart.md#cancel-cart) | cart 세션 취소 |

### `create_cart`

[Create Cart](cart.md#create-cart) 연산에 매핑됩니다.

#### 입력 스키마

{{ schema_fields('cart_create_req', 'cart') }}

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "create_cart",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            }
          },
          "cart": {
            "line_items": [
              {
                "item": {
                  "id": "item_123"
                },
                "quantity": 2
              }
            ],
            "context": {
              "address_country": "US",
              "address_region": "CA",
              "postal_code": "94105"
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
          "cart": {
            "ucp": {
              "version": "2026-01-15",
              "capabilities": [
                {
                  "name": "dev.ucp.shopping.checkout",
                  "version": "2026-01-11"
                },
                {
                  "name": "dev.ucp.shopping.cart",
                  "version": "2026-01-15"
                }
              ]
            },
            "id": "cart_abc123",
            "line_items": [
              {
                "id": "li_1",
                "item": {
                  "id": "item_123",
                  "title": "Red T-Shirt",
                  "price": 2500
                },
                "quantity": 2,
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
                "type": "total",
                "amount": 5000
              }
            ],
            "continue_url": "https://business.example.com/checkout?cart=cart_abc123",
            "expires_at": "2026-01-16T12:00:00Z"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"cart\":{\"ucp\":{...},\"id\":\"cart_abc123\",...}}"
          }
        ]
      }
    }
    ```

### `get_cart`

[Get Cart](cart.md#get-cart) 연산에 매핑됩니다.

#### 입력 스키마

* `id` (String, required): cart 세션 ID.

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "get_cart",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            }
          },
          "id": "cart_abc123"
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
          "cart": {
            "ucp": {
              "version": "2026-01-15",
              "capabilities": [
                {
                  "name": "dev.ucp.shopping.checkout",
                  "version": "2026-01-11"
                },
                {
                  "name": "dev.ucp.shopping.cart",
                  "version": "2026-01-15"
                }
              ]
            },
            "id": "cart_abc123",
            "line_items": [
              {
                "id": "li_1",
                "item": {
                  "id": "item_123",
                  "title": "Red T-Shirt",
                  "price": 2500
                },
                "quantity": 2,
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
                "type": "total",
                "amount": 5000
              }
            ],
            "continue_url": "https://business.example.com/checkout?cart=cart_abc123",
            "expires_at": "2026-01-16T12:00:00Z"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"cart\":{\"ucp\":{...},\"id\":\"cart_abc123\",...}}"
          }
        ]
      }
    }
    ```

=== "Not Found"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "structuredContent": {
          "cart": {
            "ucp": {
              "version": "2026-01-15",
              "capabilities": [
                {
                  "name": "dev.ucp.shopping.cart",
                  "version": "2026-01-15"
                }
              ]
            },
            "messages": [
              {
                "type": "error",
                "code": "not_found",
                "content": "Cart not found or has expired"
              }
            ],
            "continue_url": "https://merchant.com/"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"cart\":{\"ucp\":{...},\"messages\":[...],\"continue_url\":\"...\"}}"
          }
        ]
      }
    }
    ```

### `update_cart`

[Update Cart](cart.md#update-cart) 연산에 매핑됩니다.

#### 입력 스키마

* `id` (String, required): 갱신할 cart 세션 ID.

{{ schema_fields('cart_update_req', 'cart') }}

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 2,
      "method": "tools/call",
      "params": {
        "name": "update_cart",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            }
          },
          "id": "cart_abc123",
          "cart": {
            "line_items": [
              {
                "item": {
                  "id": "item_123"
                },
                "quantity": 3
              },
              {
                "item": {
                  "id": "item_456"
                },
                "quantity": 1
              }
            ],
            "context": {
              "address_country": "US",
              "address_region": "CA",
              "postal_code": "94105"
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
          "cart": {
            "ucp": {
              "version": "2026-01-15",
              "capabilities": [
                {
                  "name": "dev.ucp.shopping.checkout",
                  "version": "2026-01-11"
                },
                {
                  "name": "dev.ucp.shopping.cart",
                  "version": "2026-01-15"
                }
              ]
            },
            "id": "cart_abc123",
            "line_items": [
              {
                "id": "li_1",
                "item": {
                  "id": "item_123",
                  "title": "Red T-Shirt",
                  "price": 2500
                },
                "quantity": 3,
                "totals": [
                  {"type": "subtotal", "amount": 7500},
                  {"type": "total", "amount": 7500}
                ]
              },
              {
                "id": "li_2",
                "item": {
                  "id": "item_456",
                  "title": "Blue Jeans",
                  "price": 7500
                },
                "quantity": 1,
                "totals": [
                  {"type": "subtotal", "amount": 7500},
                  {"type": "total", "amount": 7500}
                ]
              }
            ],
            "currency": "USD",
            "totals": [
              {
                "type": "subtotal",
                "amount": 15000
              },
              {
                "type": "total",
                "amount": 15000
              }
            ],
            "continue_url": "https://business.example.com/checkout?cart=cart_abc123",
            "expires_at": "2026-01-16T12:00:00Z"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"cart\":{\"ucp\":{...},\"id\":\"cart_abc123\",...}}"
          }
        ]
      }
    }
    ```

### `cancel_cart`

[Cancel Cart](cart.md#cancel-cart) 연산에 매핑됩니다.

#### 입력 스키마

* `id` (String, required): cart 세션 ID.

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "tools/call",
      "params": {
        "name": "cancel_cart",
        "arguments": {
          "meta": {
            "ucp-agent": {
              "profile": "https://platform.example/profiles/v2026-01/shopping-agent.json"
            },
            "idempotency-key": "660e8400-e29b-41d4-a716-446655440001"
          },
          "id": "cart_abc123"
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
          "cart": {
            "ucp": {
              "version": "2026-01-15",
              "capabilities": [
                {
                  "name": "dev.ucp.shopping.checkout",
                  "version": "2026-01-11"
                },
                {
                  "name": "dev.ucp.shopping.cart",
                  "version": "2026-01-15"
                }
              ]
            },
            "id": "cart_abc123",
            "line_items": [
              {
                "id": "li_1",
                "item": {
                  "id": "item_123",
                  "title": "Red T-Shirt",
                  "price": 2500
                },
                "quantity": 2,
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
                "type": "total",
                "amount": 5000
              }
            ],
            "continue_url": "https://business.example.com/checkout?cart=cart_abc123"
          }
        },
        "content": [
          {
            "type": "text",
            "text": "{\"cart\":{\"ucp\":{...},\"id\":\"cart_abc123\",...}}"
          }
        ]
      }
    }
    ```

## 오류 처리

UCP는 프로토콜 오류와 비즈니스 결과를 구분합니다.
전체 오류 코드 레지스트리와 전송 바인딩 예시는
[Core Specification](overview.md#error-handling)을 참고하세요.

* **프로토콜 오류**: 인증, 레이트 리밋, 서비스 불가 등 요청 처리를 막는 전송 계층 실패.
  JSON-RPC `error`로 반환되며 코드 `-32000`(discovery 오류는 `-32001`)를 사용.
* **비즈니스 결과**: 요청이 정상 처리된 뒤의 애플리케이션 결과.
  UCP envelope과 `messages`를 포함한 JSON-RPC `result`로 반환.

### 비즈니스 결과

비즈니스 결과(미발견, 검증 오류 포함)는 `structuredContent`에
UCP envelope과 `messages`를 담아 JSON-RPC `result`로 반환됩니다.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "structuredContent": {
      "cart": {
        "ucp": {
          "version": "2026-01-11",
          "capabilities": {
            "dev.ucp.shopping.cart": [{"version": "2026-01-11"}]
          }
        },
        "messages": [
          {
            "type": "error",
            "code": "not_found",
            "content": "Cart not found or has expired"
          }
        ],
        "continue_url": "https://merchant.com/"
      }
    },
    "content": [
      {"type": "text", "text": "{\"cart\":{...}}"}
    ]
  }
}
```

## 적합성(Conformance)

적합한 MCP 전송 구현은 다음을 **반드시(MUST)** 만족해야 합니다.

1. JSON-RPC 2.0 프로토콜을 올바르게 구현한다.
2. 이 명세에서 정의한 모든 핵심 cart tool을 제공한다.
3. [Core Specification](overview.md#error-handling)에 따른 오류를 반환한다.
4. 비즈니스 결과를 UCP envelope 및 `messages` 배열이 포함된 JSON-RPC `result`로 반환한다.
5. tool 입력을 UCP 스키마에 따라 검증한다.
6. 스트리밍을 지원하는 HTTP 전송을 지원한다.
