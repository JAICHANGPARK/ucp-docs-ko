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

# Identity Linking Capability

* **Capability Name:** `dev.ucp.common.identity_linking`

## 개요

Identity Linking capability는 **플랫폼**(예: Google, agentic 서비스)이
사용자를 대신해 **비즈니스** 사이트에서 작업을 수행할 수 있는
권한을 획득하도록 합니다.

이 연결은 로열티 혜택 접근, 개인화 오퍼 활용,
위시리스트 관리, 인증된 체크아웃 실행과 같은
커머스 경험의 기반이 됩니다.

**이 명세는 플랫폼 계정과 비즈니스 계정을 안전하게 연결하기 위한 메커니즘으로
[OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749){ target="_blank" }을 사용합니다.**

## 일반 가이드라인

(상위 가이드라인에 추가하여)

### 플랫폼용

* 플랫폼은 토큰 교환 시
    HTTP Basic Authentication을 통해
    [RFC 6749 2.3.1](https://datatracker.ietf.org/doc/html/rfc6749#section-2.3.1){target="_blank"}에 따른
    `client_id` 및 `client_secret`으로 **MUST** 인증해야 합니다.
    ([RFC 7617](https://datatracker.ietf.org/doc/html/rfc7617){target="_blank"})
    * Client Metadata를 **MAY** 지원할 수 있습니다.
    * 정적 자격증명 교환을 대체하기 위한 Dynamic Client Registration 메커니즘을
        **MAY** 지원할 수 있습니다.
* 플랫폼은 HTTP Authorization 헤더에
    Bearer 스키마(`Authorization: Bearer <access_token>`)를 사용해
    토큰을 포함해야 합니다.
* 플랫폼은 기본 연결 메커니즘으로
    OAuth 2.0 Authorization Code flow
    ([RFC 6749 4.1](https://datatracker.ietf.org/doc/html/rfc6749#section-4.1){target="_blank"})를
    **MUST** 구현해야 합니다.
* CSRF 방지를 위해 authorization request에
    고유하고 예측 불가능한 state 파라미터를 포함하는 것을
    **SHOULD** 권장합니다.
    ([RFC 6749 10.12](https://datatracker.ietf.org/doc/html/rfc6749#section-10.12){target="_blank"})
    (이는
    [OAuth 2.1 draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-14#name-preventing-csrf-attacks){target="_blank"}
    의 일부입니다).
* Revocation 및 보안 이벤트
    * 플랫폼 측에서 사용자가 연결 해제(unlink)를 시작하면,
        비즈니스의 revocation endpoint
        ([RFC 7009](https://datatracker.ietf.org/doc/html/rfc7009))를 호출하는 것을
        **SHOULD** 권장합니다.
    * 비동기 계정 업데이트, unlink 이벤트, 교차 계정 보호를 처리하기 위해
        [OpenID RISC Profile 1.0](https://openid.net/specs/openid-risc-1_0-final.html)
        지원을 **SHOULD** 권장합니다.

### 비즈니스용

* OAuth 2.0
    ([RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749))을 **MUST** 구현해야 합니다.
* OAuth 2.0 endpoint 위치를 선언하기 위해
    [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)를 **MUST** 준수해야 합니다.
    (`/.well-known/oauth-authorization-server`)
    * 특정 리소스와 연계된 Authorization Server를 플랫폼이 발견할 수 있도록
        [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728/) (HTTP Resource Metadata)를
        **SHOULD** 구현하는 것이 좋습니다.
    * [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414)의 일부로
        `scopes_supported`를 채우는 것을 **SHOULD** 권장합니다.
* Token Endpoint에서 Client Authentication을 **MUST** 강제해야 합니다.
* 사용자가 아직 계정이 없을 경우 계정 생성 흐름을 **MUST** 제공해야 합니다.
* Scopes 섹션에 정의된 표준 UCP scope를 **MUST** 지원해야 하며,
    해당 리소스의 관련 작업(Operation) 전체에 대한 권한을 토큰에 부여해야 합니다.
* 명시적으로 요청된 권한 외 추가 권한을 **MAY** 부여할 수 있으나,
    최소한 요청된 scope는 반드시 포함되어야 합니다.
* 플랫폼과 비즈니스는 최소 scope 요구사항을 넘어서는
    추가 커스텀 scope를 **MAY** 정의할 수 있습니다.
* Revocation 및 보안 이벤트
    * [RFC 7009](https://datatracker.ietf.org/doc/html/rfc7009)에 정의된 표준 Token Revocation을
        **MUST** 구현해야 합니다.
    * 지정된 토큰을 **MUST** 폐기해야 하며,
        연관된 모든 토큰을 재귀적으로 폐기하는 것을 **SHOULD** 권장합니다
        (예: `refresh_token` 폐기 시,
        여기서 발급된 활성 `access_token`도 즉시 **MUST** 폐기).
    * 토큰 endpoint에서 사용한 동일 클라이언트 자격증명으로 인증된
        revocation 요청을 **MUST** 지원해야 합니다.
    * 비즈니스 측에서 시작된 revocation 또는 계정 상태 변경을 안전하게 신호하고,
        Cross-Account Protection을 가능하게 하기 위해
        [OpenID RISC Profile 1.0](https://openid.net/specs/openid-risc-1_0-final.html)
        지원을 **SHOULD** 권장합니다.
        ([Cross-Account protection 참고](https://developers.google.com/identity/account-linking/unlinking#cross-account_protection_risc))

## Scopes

비즈니스의 실제 지원 여부와 무관하게,
사용자에게 UCP에 필요할 수 있는 모든 scope 접근을 플랫폼이 요청하도록 권장합니다.

### 구조

scope의 복잡성은 사용자 동의 화면에서 숨겨져야 합니다.
사용자에게 액션별로 한 줄씩 노출되기보다,
예를 들어 "Allow [platform] to manage checkout sessions"처럼
일반화된 형태로 제시되어야 합니다.

### 리소스, 액션, capability 간 매핑

Resources       | Operation                  | Scope Action
:-------------- | :------------------------- | :----------------------------
CheckoutSession | Get                        | `ucp:scopes:checkout_session`
CheckoutSession | Create                     | `ucp:scopes:checkout_session`
CheckoutSession | Update                     | `ucp:scopes:checkout_session`
CheckoutSession | Delete                     | `ucp:scopes:checkout_session`
CheckoutSession | Cancel                     | `ucp:scopes:checkout_session`
CheckoutSession | Complete                   | `ucp:scopes:checkout_session`

capability를 포괄하는 scope는 해당 capability와 연관된 모든 operation에 대한
접근 권한을 부여해야 합니다.
예를 들어 `ucp:scopes:checkout_session`은
Get, Create, Update, Delete, Cancel, Complete 모두를 허용해야 합니다.

## 예시

### Authorization server metadata

`/.well-known/oauth-authorization-server`에 호스팅되어야 하는
[RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414){target="_blank"} 기준
[metadata](https://datatracker.ietf.org/doc/html/rfc8414#section-2){target="_blank"}
예시는 다음과 같습니다.

```json
{
  "issuer": "https://merchant.example.com",
  "authorization_endpoint": "https://merchant.example.com/oauth2/authorize",
  "token_endpoint": "https://merchant.example.com/oauth2/token",
  "revocation_endpoint": "https://merchant.example.com/oauth2/revoke",
  "scopes_supported": [
    "ucp:scopes:checkout_session",
  ],
  "response_types_supported": [
    "code"
  ],
  "grant_types_supported": [
    "authorization_code",
    "refresh_token"
  ],
  "token_endpoint_auth_methods_supported": [
    "client_secret_basic"
  ],
  "service_documentation": "https://merchant.example.com/docs/oauth2"
}
```
