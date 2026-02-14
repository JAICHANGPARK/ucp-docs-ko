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

# UCP와 AP2

UCP는
[Agent Payments Protocol (AP2)](https://ap2-protocol.org/){ target="_blank" }와
완전히 호환됩니다.
AP2는 사용자를 대신해 수행되는 에이전트 기반 거래의 신뢰 계층으로 동작하며,
플랫폼과 비즈니스 간 의도(intent) 및 권한(authorizations)의
안전하고 검증 가능한 교환을 요구합니다.
AP2는 검증 가능한 디지털 자격증명(Verifiable Digital Credentials, VDCs)을 사용해
중간 "신뢰 중개자"의 필요를 제거합니다.
이를 통해 비즈니스는 가격과 조건이 흐름 중간에 변경되지 않음을 보장하는
서명된 체크아웃 확약을 받을 수 있고,
플랫폼은 카트의 특정 상태에 수학적으로 결합된
암호학적 서명 결제 승인 정보를 제공할 수 있습니다.

## 핵심 이점

* **구속력 있는 증명(Binding proof):** 양 당사자는
    무엇이 제안되었고 무엇에 합의했는지에 대한 암호학적 증거를 가지며,
    이를 통해 거래의 최종성과 진정성을 보장합니다.
* **사기 감소:** 결제 위임은 특정 checkout hash에 한정되어 적용되므로,
    "token replay" 또는 금액 조작을 방지합니다.
* **에이전트 준비성(Agentic readiness):** 자율형 AI 에이전트가
    사전에 정의되고 검증 가능한 경계 내에서 사용자를 대신해 거래할 수 있게 합니다.

## 프로토콜 흐름

1. **Discovery:** 비즈니스는 AP2 확장 지원을 선언하는 discovery 문서를 게시합니다.
2. **세션 활성화(Session Activation):** 체크아웃 세션 생성 또는 업데이트 시,
    플랫폼은 AP2 활성화를 신호로 보냅니다.
3. **서명(비즈니스):** 비즈니스는 `checkoutSignature`(체크아웃 상태에 서명한 detached JWT)를
    반환하고, 지원 가능한 검증 프리젠테이션 형식(예: `sd-jwt`)을 나열합니다.
4. **권한 부여(Authorization):** 사용자 동의 후 플랫폼은 두 개의
    자격증명을 생성합니다.
    * **CheckoutMandate:** `CheckoutObject`의 hash를 포함합니다.
    * **PaymentMandate:** 결제 승인 정보를 담은 SD-JWT-VC입니다.
5. **완료(Completion):** 플랫폼은 두 mandate를 비즈니스의
    `/complete` 엔드포인트에 제출합니다.
6. **검증(Verification):**
    * 비즈니스는 `CheckoutMandate`를 검증합니다.
    * Payment Processor는 `PaymentMandate`를 검증합니다.
7. **확정(Confirmation):** 유효성이 확인되면 결제가 처리되고 주문이 확정됩니다.

**의존성(Dependencies):** Checkout capability

[AP2 Mandates 확장 전체 보기](../specification/ap2-mandates.md)

[AP2 자세히 보기](https://ap2-protocol.org){target="_blank"}
