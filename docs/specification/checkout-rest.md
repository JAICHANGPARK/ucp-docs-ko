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

# 체크아웃 기능 - REST 바인딩

이 문서는 [Checkout Capability](checkout.md)의 REST 바인딩을 정의합니다.

## 프로토콜 기본 사항

### 기본 URL

모든 UCP REST 엔드포인트는 business의 base URL을 기준으로 하며,
이 URL은 `/.well-known/ucp` UCP 프로필에서 탐색됩니다.
checkout capability 엔드포인트는 business 프로필의 `rest.endpoint` 필드에 정의됩니다.

### 콘텐츠 타입

* **요청(Request)**: `application/json`
* **응답(Response)**: `application/json`

모든 요청/응답 바디는 [RFC 8259](https://tools.ietf.org/html/rfc8259){ target="_blank" }에 정의된
유효한 JSON이어야 합니다(**MUST**).

### 전송 보안

모든 REST 엔드포인트는 최소 TLS 1.3 이상의 HTTPS로 제공되어야 합니다(**MUST**).

## 연산(Operations)

| 연산 | 메서드 | 엔드포인트 | 설명 |
| :--- | :----- | :--------- | :--- |
| [Create Checkout](checkout.md#create-checkout) | `POST` | `/checkout-sessions` | checkout 세션 생성 |
| [Get Checkout](checkout.md#get-checkout) | `GET` | `/checkout-sessions/{id}` | checkout 세션 조회 |
| [Update Checkout](checkout.md#update-checkout) | `PUT` | `/checkout-sessions/{id}` | checkout 세션 갱신 |
| [Complete Checkout](checkout.md#complete-checkout) | `POST` | `/checkout-sessions/{id}/complete` | 주문 확정 |
| [Cancel Checkout](checkout.md#cancel-checkout) | `POST` | `/checkout-sessions/{id}/cancel` | checkout 세션 취소 |

## 예시

### Checkout 생성 { #create-checkout }

=== "Request"

    ```json
    POST /checkout-sessions HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "line_items": [
        {
          "item": {
            "id": "item_123",
            "title": "Red T-Shirt",
            "price": 2500
          },
          "id": "li_1",
          "quantity": 2
        }
      ]
    }
    ```

=== "Response"

    ```json
    HTTP/1.1 201 Created
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.shopify.shop_pay": [
            {
              "id": "shop_pay_1234",
              "version": "2026-01-11",
              "config": {
                "merchant_id": "shop_merchant_123"
              }
            }
          ]
        }
      },
      "id": "chk_1234567890",
      "status": "incomplete",
      "messages": [
        {
          "type": "error",
          "code": "missing",
          "path": "$.buyer.email",
          "content": "Buyer email is required",
          "severity": "recoverable"
        }
      ],
      "currency": "USD",
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
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://business.example.com/terms"
        }
      ],
      "payment": {
        "instruments": [
          {
            "id": "instr_shop_pay_1",
            "handler_id": "shop_pay_1234",
            "type": "shop_pay",
            "selected": true,
            "display": {
              "email": "buyer@example.com"
            }
          }
        ]
      }
    }
    ```

### Checkout 업데이트 { #update-checkout }

#### 구매자 정보 업데이트

`buyer`의 모든 필드는 선택 사항이며, 클라이언트는 여러 호출에 걸쳐
checkout 상태를 점진적으로 구성할 수 있습니다. 각 PUT은 세션 전체를 교체하므로
유지하려는 기존 필드는 반드시 함께 포함해야 합니다.

=== "Request"

    ```json
    PUT /checkout-sessions/{id} HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "id": "chk_123456789",
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "line_items": [
        {
          "item": {
            "id": "item_123",
            "title": "Red T-Shirt",
            "price": 2500
          },
          "id": "li_1",
          "quantity": 2
        }
      ]
    }
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.shopify.shop_pay": [
            {
              "id": "shop_pay_1234",
              "version": "2026-01-11",
              "config": {
                "merchant_id": "shop_merchant_123"
              }
            }
          ]
        }
      },
      "id": "chk_1234567890",
      "status": "incomplete",
      "messages": [
        {
          "type": "error",
          "code": "missing",
          "path": "$.fulfillment.method[0].selected_destination_id",
          "content": "Fulfillment address is required",
          "severity": "recoverable"
        }
      ],
      "currency": "USD",
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://business.example.com/terms"
        }
      ],
      "payment": {
        "instruments": [
          {
            "id": "instr_shop_pay_1",
            "handler_id": "shop_pay_1234",
            "type": "shop_pay",
            "selected": true,
            "display": {
              "email": "buyer@example.com"
            }
          }
        ]
      }
    }
    ```

#### Fulfillment 업데이트

Fulfillment는 checkout capability의 확장입니다. 대부분의 필드는
구매자 입력(희망 fulfillment 타입 및 주소 등)을 바탕으로 business가 계산해 제공합니다.

=== "Request"

    ```json
    PUT /checkout-sessions/{id} HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "id": "chk_123456789",
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "line_items": [
        {
          "item": {
            "id": "item_123",
            "title": "Red T-Shirt",
            "price": 2500
          },
          "id": "li_1",
          "quantity": 2
        }
      ],
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
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.google.pay": [
            {
              "id": "gpay_1234",
              "version": "2026-01-11",
              "config": {
                "allowed_payment_methods": [
                  {
                    "type": "CARD",
                    "parameters": {
                      "allowed_card_networks": ["VISA", "MASTERCARD", "AMEX"]
                    }
                  }
                ]
              }
            }
          ]
        }
      },
      "id": "chk_1234567890",
      "status": "incomplete",
      "messages": [
        {
          "type": "error",
          "code": "missing",
          "path": "$.selected_fulfillment_option",
          "content": "Please select a fulfillment option",
          "severity": "recoverable"
        }
      ],
      "currency": "USD",
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://merchant.com/terms"
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
      "payment": {
        "instruments": [
          {
            "id": "pi_gpay_5678",
            "handler_id": "gpay_1234",
            "type": "card",
            "selected": true,
            "display": {
              "brand": "mastercard",
              "last_digits": "5678",
              "rich_text_description": "Google Pay •••• 5678"
            }
          }
        ]
      }
    }
    ```

#### Fulfillment 선택 업데이트

초기 `fulfillment` 데이터 설정 이후, 선택값을 변경하기 위한 후속 호출입니다.

=== "Request"

    ```json
    PUT /checkout-sessions/{id} HTTP/1.1
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "id": "chk_123456789",
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "line_items": [
        {
          "item": {
            "id": "item_123",
            "title": "Red T-Shirt",
            "price": 2500
          },
          "id": "li_1",
          "quantity": 2,
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
                "selected_option_id": "express"
              }
            ]
          }
        ]
      }
    }
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.shopify.shop_pay": [
            {
              "id": "shop_pay_1234",
              "version": "2026-01-11",
              "config": {
                "merchant_id": "shop_merchant_123"
              }
            }
          ]
        }
      },
      "id": "chk_1234567890",
      "status": "ready_for_complete",
      "currency": "USD",
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://merchant.com/terms"
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
      "payment": {
        "instruments": [
          {
            "id": "instr_shop_pay_1",
            "handler_id": "shop_pay_1234",
            "type": "shop_pay",
            "selected": true,
            "display": {
              "email": "buyer@example.com"
            }
          }
        ]
      }
    }
    ```

### Checkout 완료 { #complete-checkout }

business가 `buyer` 및 주소(`fulfillment_address`, `billing_address`) 필수 여부를
강제하는 로직을 가진 경우, `messages`를 통해 해당 요구사항을 명시하는 적절한 지점입니다.

=== "Request"

    ```json
    POST /checkout-sessions/{id}/complete
    UCP-Agent: profile="https://platform.example/profile"
    Content-Type: application/json

    {
      "payment": {
        "instruments": [
          {
            "id": "pi_gpay_5678",
            "handler_id": "gpay_1234",
            "type": "card",
            "selected": true,
            "display": {
              "brand": "mastercard",
              "last_digits": "5678",
              "card_art": "https://cart-art-1.html",
              "description": "Google Pay •••• 5678"
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
      "risk_signals": {
        //... risk signal related data (device fingerprint / risk token)
      }
    }
    ```

=== "Response"

    ```json
    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "ucp": {
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.google.pay": [
            {
              "id": "gpay_1234",
              "version": "2026-01-11",
              "config": {
                "allowed_payment_methods": [
                  {
                    "type": "CARD",
                    "parameters": {
                      "allowed_card_networks": ["VISA", "MASTERCARD", "AMEX"]
                    }
                  }
                ]
              }
            }
          ]
        }
      },
      "id": "chk_123456789",
      "status": "completed",
      "currency": "USD",
      "order": {
        "id": "ord_99887766",
        "permalink_url": "https://merchant.com/orders/ord_99887766"
      },
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://merchant.com/terms"
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
      "payment": {
        "instruments": [
          {
            "id": "pi_gpay_5678",
            "handler_id": "gpay_1234",
            "type": "card",
            "selected": true,
            "display": {
              "brand": "mastercard",
              "last_digits": "5678",
              "rich_text_description": "Google Pay •••• 5678"
            }
          }
        ]
      }
    }
    ```

### Checkout 조회 { #get-checkout }

=== "Request"

    ```json
    GET /checkout-sessions/{id}
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
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.shopify.shop_pay": [
            {
              "id": "shop_pay_1234",
              "version": "2026-01-11",
              "config": {
                "merchant_id": "shop_merchant_123"
              }
            }
          ]
        }
      },
      "id": "chk_123456789",
      "status": "completed",
      "currency": "USD",
      "order": {
        "id": "ord_99887766",
        "permalink_url": "https://merchant.com/orders/ord_99887766"
      },
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://merchant.com/terms"
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
      "payment": {
        "instruments": [
          {
            "id": "instr_shop_pay_1",
            "handler_id": "shop_pay_1234",
            "type": "shop_pay",
            "selected": true,
            "display": {
              "email": "buyer@example.com"
            }
          }
        ]
      }
    }
    ```

### Checkout 취소 { #cancel-checkout }

=== "Request"

    ```json
    POST /checkout-sessions/{id}/cancel
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
        "version": "2026-01-11",
        "capabilities": {
          "dev.ucp.shopping.checkout": [
            {"version": "2026-01-11"}
          ]
        },
        "payment_handlers": {
          "com.google.pay": [
            {
              "id": "gpay_1234",
              "version": "2026-01-11",
              "config": {
                "allowed_payment_methods": [
                  {
                    "type": "CARD",
                    "parameters": {
                      "allowed_card_networks": ["VISA", "MASTERCARD", "AMEX"]
                    }
                  }
                ]
              }
            }
          ]
        }
      },
      "id": "chk_123456789",
      "status": "canceled", // Status is updated to canceled.
      "currency": "USD",
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
      "buyer": {
        "email": "jane@example.com",
        "first_name": "Jane",
        "last_name": "Doe"
      },
      "totals": [
        {
          "type": "subtotal",
          "amount": 5000
        },
        {
          "type": "tax",
          "amount": 400
        },
        {
          "type": "total",
          "amount": 5400
        }
      ],
      "links": [
        {
          "type": "terms_of_service",
          "url": "https://merchant.com/terms"
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
      "payment": {
        "instruments": [
          {
            "id": "pi_gpay_5678",
            "handler_id": "gpay_1234",
            "type": "card",
            "selected": true,
            "display": {
              "brand": "mastercard",
              "last_digits": "5678",
              "rich_text_description": "Google Pay •••• 5678"
            }
          }
        ]
      }
    }
    ```

## HTTP 헤더

다음 헤더는 HTTP 바인딩에서 정의되며,
별도 명시가 없는 한 모든 연산에 적용됩니다.

{{ header_fields('create_checkout', 'rest.openapi.json') }}

### 헤더별 요구사항

* **UCP-Agent**: 모든 요청은 Dictionary Structured Field 문법
  ([RFC 8941](https://datatracker.ietf.org/doc/html/rfc8941){target="_blank"})으로
  플랫폼 프로필 URI를 담은 `UCP-Agent` 헤더를 **반드시(MUST)** 포함해야 합니다.
  형식: `profile="https://platform.example/profile"`.
* **Idempotency-Key**: 상태를 변경하는 연산은 멱등성을 지원하는 것이 **권장(SHOULD)** 됩니다.
  제공된 경우 서버는 다음을 **반드시(MUST)** 수행해야 합니다.
  1. 키와 연산 결과를 최소 24시간 저장
  2. 중복 키 요청 시 캐시된 결과 반환
  3. 다른 파라미터로 키를 재사용하면 `409 Conflict` 반환

## 프로토콜 메커니즘

### 상태 코드

UCP는 API 요청의 성공/실패를 표준 HTTP 상태 코드로 표현합니다.

| 상태 코드 | 설명 |
| :-------- | :--- |
| `200 OK` | 요청 성공 |
| `201 Created` | 리소스 생성 성공 |
| `400 Bad Request` | 요청이 잘못되었거나 처리 불가 |
| `401 Unauthorized` | 인증 필요, 인증 실패 또는 미제공 |
| `403 Forbidden` | 인증되었지만 권한 부족 |
| `409 Conflict` | 충돌로 요청 완료 불가(예: idempotency 키 재사용) |
| `422 Unprocessable Entity` | 프로필 콘텐츠 형식 오류(discovery 실패) |
| `424 Failed Dependency` | 프로필 URL은 유효하지만 조회 실패(discovery 실패) |
| `429 Too Many Requests` | 레이트 리밋 초과 |
| `503 Service Unavailable` | 일시적 서비스 불가 |
| `500 Internal Server Error` | 서버 내부의 예기치 못한 오류 |

### 오류 응답

전체 오류 코드 레지스트리와 전송 바인딩 예시는
[Core Specification](overview.md#error-handling)을 참고하세요.

* **프로토콜 오류**: 적절한 HTTP 상태 코드(401, 403, 409, 429, 503)와
  `code`, `content`를 포함한 JSON 바디 반환
* **비즈니스 결과**: UCP envelope과 `messages` 배열을 포함해 HTTP 200 반환

#### 비즈니스 결과

비즈니스 결과(상품 불가 오류 포함)는 HTTP 200과 `messages`를 담은
UCP envelope으로 반환됩니다:

```json
{
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
(예: 인증 없는 공개 checkout)
