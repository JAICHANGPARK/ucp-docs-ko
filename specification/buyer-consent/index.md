# 구매자 동의 확장(Buyer Consent Extension)

## 개요

구매자 동의 확장은 플랫폼이 데이터 사용 및 커뮤니케이션 선호와 관련된 구매자 동의 선택 사항을 비즈니스에 전달할 수 있도록 합니다. 이를 통해 구매자는 분석, 마케팅, 데이터 판매 등의 카테고리에 대한 동의 상태를 전달할 수 있으며, 비즈니스는 CCPA 및 GDPR 같은 개인정보 보호 규정을 준수하는 데 도움을 받을 수 있습니다.

이 확장을 지원하면 checkout의 `buyer` 객체가 불리언 동의 상태를 담는 `consent` 필드로 확장됩니다.

이 확장은 `create_checkout` 및 `update_checkout` 작업에 포함될 수 있습니다.

## 디스커버리

비즈니스는 프로필에서 동의 지원 여부를 광고합니다.

```json
{
  "capabilities": {
    "dev.ucp.shopping.buyer_consent": [
      {
        "version": "2026-01-11",
        "extends": "dev.ucp.shopping.checkout"
      }
    ]
  }
}
```

## 스키마 구성(Schema Composition)

동의 확장은 checkout 내부의 **buyer 객체**를 확장합니다.

- **확장 대상 기본 스키마**: `buyer` 객체를 통한 `checkout`
- **경로**: `checkout.buyer.consent`
- **스키마 참조**: `buyer_consent.json`

## 스키마 정의

### 동의(Consent) 객체

| Name         | Type    | Required | Description                                       |
| ------------ | ------- | -------- | ------------------------------------------------- |
| analytics    | boolean | No       | Consent for analytics and performance tracking.   |
| preferences  | boolean | No       | Consent for storing user preferences.             |
| marketing    | boolean | No       | Consent for marketing communications.             |
| sale_of_data | boolean | No       | Consent for selling data to third parties (CCPA). |

## 사용 방법

플랫폼은 checkout 작업 시 `buyer` 객체 안에 consent를 포함합니다.

### 예시: 동의를 포함한 체크아웃 생성

```json
POST /checkouts

{
  "line_items": [
    {
      "item": {
        "id": "prod_123",
        "title": "Blue T-Shirt",
        "price": 1999
      },
      "id": "li_1",
      "quantity": 1
    }
  ],
  "buyer": {
    "email": "jane.doe@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "consent": {
      "analytics": true,
      "preferences": true,
      "marketing": false,
      "sale_of_data": false
    }
  }
}
```

### 예시: 동의를 포함한 체크아웃 응답

```json
{
  "id": "checkout_456",
  "status": "ready_for_payment",
  "currency": "USD",
  "buyer": {
    "email": "jane.doe@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "consent": {
      "analytics": true,
      "preferences": true,
      "marketing": false,
      "sale_of_data": false
    }
  },
  "line_items": [...],
  "totals": [...],
  "links": [
    {
      "type": "privacy_policy",
      "url": "https://example.com/privacy"
    }
  ]
}
```

## 보안 및 개인정보 고려사항

1. **동의는 선언적 정보입니다** - 프로토콜은 동의를 전달하지만 이를 강제하지는 않습니다.
1. **법적 준수 책임**은 비즈니스에 있습니다.
1. 플랫폼은 **명시적 사용자 행동 없이 동의를 가정해서는 안 됩니다**.
1. 동의가 제공되지 않은 경우의 **기본 동작**은 비즈니스별 정책을 따릅니다.
