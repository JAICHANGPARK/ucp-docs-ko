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

# 스키마 레퍼런스

이 페이지는 UCP 내에서 사용되는 모든 capability 데이터 모델과 타입에 대한
참조 정보를 제공합니다.

## 기능(Capability) 스키마

{{ auto_generate_schema_reference('.', 'reference', include_extensions=False) }}

## 타입 스키마

{{ auto_generate_schema_reference('types', 'reference', include_extensions=False) }}

## 확장 스키마

{{ auto_generate_schema_reference('.', 'reference', include_capability=False) }}

## UCP 메타데이터

다음 스키마는 discovery 및 response에서 사용되는 UCP 메타데이터 구조를 정의합니다.

### 플랫폼 Discovery 프로필

플랫폼이 공지한 URI에 호스팅되는 플랫폼 프로필 문서의 최상위 구조입니다.

{{ extension_schema_fields('ucp.json#/$defs/platform_schema', 'reference') }}

### 비즈니스 Discovery 프로필

비즈니스 discovery 문서(`/.well-known/ucp`)의 최상위 구조입니다.

{{ extension_schema_fields('ucp.json#/$defs/business_schema', 'reference') }}

### 체크아웃 응답 메타데이터

checkout 응답에 포함되는 `ucp` 객체입니다.

{{ extension_schema_fields('ucp.json#/$defs/response_checkout_schema', 'reference') }}

### 주문 응답 메타데이터

order 응답 또는 이벤트에 포함되는 `ucp` 객체입니다.

{{ extension_schema_fields('ucp.json#/$defs/response_order_schema', 'reference') }}

### 기능(Capability)

이 객체는 단일 capability 또는 extension을 설명합니다.
이 객체는 discovery 프로필과 응답의 `capabilities` 배열에 나타나며,
컨텍스트에 따라 필수 필드가 약간 다릅니다.

#### 기능(Capability) - 디스커버리

discovery 프로필에서의 형식입니다.

{{ extension_schema_fields('capability.json#/$defs/platform_schema', 'reference') }}

#### 기능(Capability) - 응답

응답 메시지에서의 형식입니다.

{{ extension_schema_fields('capability.json#/$defs/response_schema', 'reference') }}
