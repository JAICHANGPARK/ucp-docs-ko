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

# Cart Capability - REST 바인딩

이 문서는 [Cart Capability](cart.md)의 REST 바인딩을 정의합니다.

## 프로토콜 기본 사항

### Discovery

business는 `/.well-known/ucp`의 UCP 프로필을 통해 REST 전송 사용 가능 여부를 광고합니다.

```json
{
  "ucp": {
    "version": "2026-01-15",
    "services": {
      "dev.ucp.shopping": {
        "version": "2026-01-15",
        "spec": "https://ucp.dev/specification/overview",
        "rest": {
          "schema": "https://ucp.dev/services/shopping/openapi.json",
          "endpoint": "https://business.example.com/ucp/v1"
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

### Base URL

모든 UCP REST 엔드포인트는 business의 base URL을 기준으로 하며,
이 URL은 `/.well-known/ucp` UCP 프로필에서 탐색됩니다.
cart capability 엔드포인트는 business 프로필의 `rest.endpoint` 필드에 정의됩니다.

### Content Types

* **요청(Request)**: `application/json`
* **응답(Response)**: `application/json`

모든 요청/응답 바디는
[RFC 8259](https://tools.ietf.org/html/rfc8259){ target="_blank" }에 정의된
유효한 JSON이어야 합니다(**MUST**).

### 전송 보안

모든 REST 엔드포인트는 최소 TLS 1.3 이상의 HTTPS로 제공되어야 합니다(**MUST**).

## 연산(Operations)

| 연산 | 메서드 | 엔드포인트 | 설명 |
| :--- | :----- | :--------- | :--- |
| [Create Cart](#create-cart) | `POST` | `/carts` | cart 세션 생성 |
| [Get Cart](#get-cart) | `GET` | `/carts/{id}` | cart 세션 조회 |
| [Update Cart](#update-cart) | `PUT` | `/carts/{id}` | cart 세션 갱신 |
| [Cancel Cart](#cancel-cart) | `POST` | `/carts/{id}/cancel` | cart 세션 취소 |

### Create Cart

#### 입력 스키마

{{ schema_fields('cart_create_req', 'cart') }}

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    POST /carts HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
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
    ```

=== "Response"

    ```json
    HTTP/1.1 201 Created
    Content-Type: application/json

    {
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
          "amount": 5000,
          "display_text": "Estimated total (taxes calculated at checkout)"
        }
      ],
      "continue_url": "https://business.example.com/checkout?cart=cart_abc123",
      "expires_at": "2026-01-16T12:00:00Z"
    }
    ```

### Get Cart

#### 입력 스키마

* `id` (String, required): cart 세션 ID (path parameter).

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    GET /carts/{id} HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
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
    ```

=== "Not Found"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
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
    ```

### Update Cart

#### 입력 스키마

* `id` (String, required): cart 세션 ID (path parameter).

{{ schema_fields('cart_update_req', 'cart') }}

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    PUT /carts/{id} HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "id": "cart_abc123",
      "line_items": [
        {
          "item": {
            "id": "item_123"
          },
          "id": "li_1",
          "quantity": 3
        },
        {
          "item": {
            "id": "item_456"
          },
          "id": "li_2",
          "quantity": 1
        }
      ],
      "context": {
        "address_country": "US",
        "address_region": "CA",
        "postal_code": "94105"
      }
    }
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
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
    ```

### Cancel Cart

#### 입력 스키마

* `id` (String, required): cart 세션 ID (path parameter).

#### 출력 스키마

{{ schema_fields('cart_resp', 'cart') }}

#### 예시

=== "Request"

    ```json
    POST /carts/{id}/cancel HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {}
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
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
    ```

## HTTP 헤더

다음 헤더는 HTTP 바인딩에서 정의되며,
별도 명시가 없는 한 모든 연산에 적용됩니다.

{{ header_fields('create_cart', 'rest.openapi.json') }}

### 헤더별 요구사항

* **UCP-Agent**: 모든 요청은 Dictionary Structured Field 문법
  ([RFC 8941](https://datatracker.ietf.org/doc/html/rfc8941){target="_blank"})
  으로 플랫폼 프로필 URI를 담은 `UCP-Agent` 헤더를 **반드시(MUST)** 포함해야 합니다.
  형식: `profile="https://platform.example/profile"`.
* **Idempotency-Key**: 상태를 변경하는 연산은 멱등성을 지원하는 것이 **권장(SHOULD)** 됩니다.
  제공된 경우 서버는 다음을 **반드시(MUST)** 수행해야 합니다.
  1. 키와 연산 결과를 최소 24시간 저장.
  2. 중복 키 요청 시 캐시된 결과 반환.
  3. 다른 파라미터로 키를 재사용하면 `409 Conflict` 반환.

## 프로토콜 메커니즘

### 상태 코드

| 상태 코드 | 설명 |
| :-------- | :--- |
| `200 OK` | 요청 성공 |
| `201 Created` | cart 생성 성공 |
| `400 Bad Request` | 요청이 잘못되었거나 처리 불가 |
| `401 Unauthorized` | 인증 필요, 인증 실패 또는 미제공 |
| `403 Forbidden` | 인증은 되었지만 필요한 권한 없음 |
| `409 Conflict` | 충돌로 요청 완료 불가(예: idempotency 키 재사용) |
| `422 Unprocessable Entity` | 프로필 콘텐츠가 잘못됨(discovery 실패) |
| `424 Failed Dependency` | 프로필 URL은 유효하지만 조회 실패(discovery 실패) |
| `429 Too Many Requests` | 레이트 리밋 초과 |
| `500 Internal Server Error` | 서버 내부의 예기치 못한 오류 |
| `503 Service Unavailable` | 일시적 서비스 불가 |

### 오류 응답

전체 오류 코드 레지스트리와 전송 바인딩 예시는
[Core Specification](overview.md#error-handling)을 참고하세요.

* **프로토콜 오류**: 적절한 HTTP 상태 코드(401, 403, 409, 429, 503)와
  `code`, `content`를 포함한 JSON 바디 반환
* **비즈니스 결과**: UCP envelope과 `messages` 배열을 포함해 HTTP 200 반환

#### 비즈니스 결과

비즈니스 결과(미발견, 검증 오류 포함)는 HTTP 200과 함께 `messages`가 포함된
UCP envelope으로 반환됩니다.

```json
{
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
```

## 보안 고려사항

### 인증(Authentication)

인증은 선택 사항이며 business 요구사항에 따라 달라집니다.
인증이 필요한 경우 REST 전송은 다음을 사용할 수 있습니다(**MAY**).

1. **Open API**: 공개 연산에 인증 불필요
2. **API Keys**: `X-API-Key` 헤더 사용
3. **OAuth 2.0**: `Authorization: Bearer {token}` 헤더 사용,
   [RFC 6749](https://tools.ietf.org/html/rfc6749){ target="_blank" } 준수
4. **Mutual TLS**: 고보안 환경

business는 일부 연산만 인증을 요구하고 나머지는 공개로 둘 수 있습니다(**MAY**).
(예: 인증 없는 공개 cart)
