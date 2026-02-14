<!--
   복사right 2026 UCP Authors

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

<!-- markdownlint-disable-file MD041 -->

<style>
/* ============================================
   Design System & Reset
   ============================================ */
:root {
  --bg: #ffffff;
  --panel: #f8f9fa;
  --text: #202124;
  --text-secondary: #5f6368;
  --border: #dadce0;
  --accent: #1a73e8;
  --accent-hover: #1557b0;
  --success: #1e8e3e;
  --success-bg: #e6f4ea;
  --error: #d93025;
  --error-bg: #fce8e6;
  --radius: 8px;
  --shadow: 0 1px 2px rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
  font-family: "Google Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); }

/* ============================================
   Stepper
   ============================================ */
.stepper {
  display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px;
  background: var(--panel); padding: 8px; border-radius: 50px;
}
.step-btn {
  height: 36px; /* FIXED HEIGHT */
  border: none; background: none; padding: 0 16px; border-radius: 40px;
  color: var(--text-secondary); font-weight: 500; cursor: pointer; transition: 0.2s;
  font-size: 0.85rem;
  display: inline-flex; align-items: center; justify-content: center;
}
.step-btn:hover { color: var(--text); background: rgba(0,0,0,0.05); }
.step-btn.active { background: var(--text); color: #fff; box-shadow: var(--shadow); }
.step-num { opacity: 0.6; margin-right: 8px; font-size: 0.9em; }

/* ============================================
   Components
   ============================================ */
.section { display: none; animation: fadeIn 0.3s ease; }
.section.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.title { font-size: 1.3rem; margin-bottom: 8px; font-weight: 400; margin-top: 0; }
.desc { color: var(--text-secondary); margin-bottom: 20px; line-height: 1.4; font-size: 0.9rem; }

/* COMPACT GRID LAYOUT */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}
.grid > * { min-width: 0; }

@media (max-width: 600px) { .grid { grid-template-columns: 1fr; } }

.card { border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; background: #fff; height: 100%; }
.card h3 { margin-top: 0; font-size: 1rem; margin-bottom: 12px; }

/* JSON Panels */
.json-panel {
  border: 1px solid var(--border); border-radius: var(--radius);
  background: #fafafa; overflow: hidden; display: flex; flex-direction: column;
  height: 350px;
  flex-shrink: 0;
}
.json-header {
  padding: 0 12px; height: 40px; /* Fixed Header Height */
  background: var(--panel); border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  overflow: hidden; /* Prevents layout breakage */
}
.json-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px; /* Adds space between title and badge */
}
.json-body {
  margin: 0; padding: 12px;
  overflow: auto;
  font-family: "Google Sans Mono", monospace;
  font-size: 11px;
  line-height: 1.5; white-space: pre-wrap; flex: 1;
}

/*
   -----------------------------------
   UNIFIED CONTROLS & BUTTONS
   -----------------------------------
*/
select, input {
  height: 40px; /* MATCH BUTTON HEIGHT */
  width: 100%; padding: 0 12px;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 0.9rem; margin-top: 4px;
  background: #fff;
}

/* Base Button */
.btn {
  height: 40px; /* FIXED HEIGHT */
  padding: 0 24px;
  border-radius: 50px; border: none; font-weight: 500; cursor: pointer;
  display: inline-flex; align-items: center; justify-content: center;
  gap: 8px; font-size: 0.9rem; transition: 0.2s;
  white-space: nowrap;
}

/* Primary Button */
.btn-primary { background: var(--text); color: white; }
.btn-primary:hover:not(:disabled) { background: #000; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Ghost Button (Back) */
.btn-ghost { background: transparent; color: var(--text-secondary); border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--panel); color: var(--text); }

/* Small Button (Inside Headers/Cards) */
.btn-sm {
  height: 32px; /* SMALLER FIXED HEIGHT */
  padding: 0 16px;
  font-size: 0.8rem;
}

.scenario-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f1f3f4;
  padding: 8px 12px;
  border-radius: 8px;
  margin-bottom: 24px;
  width: fit-content;
}

/* Handler Selection */
.handler-opt {
  border: 2px solid var(--border); border-radius: 8px; padding: 12px; cursor: pointer; margin-bottom: 8px;
  transition: 0.2s;
}
.handler-opt:hover { border-color: var(--text-secondary); }
.handler-opt.selected { border-color: var(--accent); background: #f0f7ff; }

/* Utilities */
.hidden { display: none !important; }
.actions { margin-top: 24px; display: flex; gap: 12px; }
.callout { background: var(--success-bg); border: 1px solid var(--success); color: #0d652d; padding: 12px; border-radius: 8px; margin-top: 16px; font-size: 0.9rem; }
.badge { background: #e8f0fe; color: var(--accent); padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; white-space: nowrap; flex-shrink: 0; }
</style>

<div class="container">
  <div class="sectionDescription">
    <h1>UCP 플레이그라운드</h1>
    <p>전체 UCP checkout 흐름을 단계별로 체험해 보세요. 이 인터랙티브
    데모는 브라우저에서 완전히 동작하며, 각 단계에서 payload를 시뮬레이션하고
    실제 UCP 스키마 기준으로 검증합니다.</p>
  </div>

  <!-- Stepper Navigation -->
  <div class="stepper" id="stepper"></div>

  <!-- VIEW: Profiles -->
  <div id="view-profiles" class="section active">
    <h2 class="title">1. 플랫폼 프로필</h2>
    <p class="desc">플랫폼 capability 프로필을 선택하세요. 이 선택에 따라 협상되는 확장(예: fulfillment, discount)이 결정됩니다.</p>
    <div class="grid">
      <div class="card">
        <h3>Configuration</h3>
        <label style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 500;">
          플랫폼 유형
          <select id="input-agent-type">
            <option value="basic">표준 (코어만)</option>
            <option value="full">고급 (모든 확장)</option>
          </select>
        </label>
        <p id="agent-desc" style="margin-top: 12px; color: var(--text-secondary); font-size: 0.85rem;">
          기본 checkout 및 주문 조회를 지원합니다.
        </p>
      </div>
      <div class="json-panel">
        <div class="json-header">
          <span class="json-title">Capabilities (지원 기능)</span>
          <button class="btn btn-ghost btn-sm" data-copy="json-profiles">복사</button>
        </div>
        <pre id="json-profiles" class="json-body"></pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-primary" data-nav="discovery">다음으로 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Discovery -->
  <div id="view-discovery" class="section">
    <h2 class="title">2. Discovery</h2>
    <p class="desc">플랫폼이 <code>/.well-known/ucp</code>를 조회합니다. 아래 응답은 Business capability와 Platform 프로필의 교집합만 보이도록 필터링되어 있습니다.</p>
    <div class="grid">
      <div class="json-panel">
        <div class="json-header"><span class="json-title">GET 요청</span></div>
        <pre id="json-disc-req" class="json-body">GET /.well-known/ucp HTTP/1.1
Host: business.example.com
Accept: application/json</pre>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">응답 (필터링됨)</span></div>
        <pre id="json-disc-res" class="json-body"></pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="profiles">&larr; 이전</button>
      <button class="btn btn-primary" data-nav="negotiation">다음으로 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Negotiation -->
  <div id="view-negotiation" class="section">
    <h2 class="title">3. Capability 협상</h2>
    <p class="desc">Platform과 Business capability의 교집합입니다. 부모가 없는(orphaned) 확장은 제거됩니다.</p>
    <div class="grid">
      <div class="json-panel">
        <div class="json-header"><span class="json-title">Business Capabilities</span></div>
        <pre id="json-neg-biz" class="json-body"></pre>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">결과 교집합</span></div>
        <pre id="json-neg-active" class="json-body"></pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="discovery">&larr; 이전</button>
      <button class="btn btn-primary" data-nav="createCheckout">다음으로 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Create Checkout -->
  <div id="view-createCheckout" class="section">
    <h2 class="title">4. Checkout 생성</h2>
    <p class="desc">플랫폼이 세션을 시작합니다. 아래 오류 응답은 엄격한 <code>message.json</code> 스키마를 따릅니다.</p>
    <div class="grid">
      <div class="json-panel">
        <div class="json-header"><span class="json-title">요청 Payload</span></div>
        <pre id="json-create-req" class="json-body"></pre>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">Response</span></div>
        <pre id="json-create-res" class="json-body"></pre>
      </div>
    </div>
    <!-- MOVED: Scenario Selector to Bottom, Smaller -->
    <div class="scenario-toolbar">
      <span class="scenario-label">시뮬레이션 시나리오:</span>
      <select id="input-create-scenario" style="width: 220px; height: 32px; font-size: 0.85rem; margin: 0;">
        <option value="missing_buyer">구매자 이메일 누락</option>
        <option value="missing_shipping">배송지 누락</option>
      </select>
      <button class="btn btn-primary btn-sm" id="btn-run-create">요청 실행</button>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="negotiation">&larr; 이전</button>
      <button class="btn btn-primary" id="nav-to-update" disabled data-nav="updateCheckout">다음 단계 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Update Checkout -->
  <div id="view-updateCheckout" class="section">
    <h2 class="title">5. Checkout 업데이트</h2>
    <p class="desc">검증 오류를 해소할 수 있도록 누락 정보를 채워 checkout을 업데이트합니다.</p>
    <div class="grid">
      <div class="json-panel">
        <div class="json-header">
          <span class="json-title">PATCH 요청</span>
          <button class="btn btn-primary btn-sm" id="btn-run-update">업데이트 실행</button>
        </div>
        <pre id="json-update-req" class="json-body"></pre>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">Response</span></div>
        <pre id="json-update-res" class="json-body"></pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="createCheckout">&larr; 이전</button>
      <button class="btn btn-primary" id="nav-to-mint" disabled data-nav="mintInstrument">다음 단계 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Mint Instrument -->
  <div id="view-mintInstrument" class="section">
    <h2 class="title">6. 결제 Instrument 발급</h2>
    <p class="desc">payment handler 흐름을 시뮬레이션해 결제 credential을 획득합니다.</p>
    <div class="grid">
      <div class="card">
        <h3>핸들러 선택</h3>
        <div class="handler-opt selected" data-handler="shop_pay">
          <strong>Shop Pay</strong><br>
          <small>com.shopify.shop_pay</small>
        </div>
        <div class="handler-opt" data-handler="gpay">
          <strong>Google Pay</strong><br>
          <small>com.google.pay</small>
        </div>
        <button class="btn btn-primary" style="margin-top: 12px; width: 100%;" id="btn-run-mint">Credential 발급</button>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">발급된 Instrument</span></div>
        <pre id="json-mint-res" class="json-body"></pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="updateCheckout">&larr; 이전</button>
      <button class="btn btn-primary" id="nav-to-complete" disabled data-nav="completeCheckout">다음 단계 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Complete Checkout -->
  <div id="view-completeCheckout" class="section">
    <h2 class="title">7. Checkout 완료</h2>
    <p class="desc">발급된 instrument를 제출해 거래를 최종 확정하고 주문을 생성합니다.</p>
    <div class="grid">
      <div class="json-panel">
        <div class="json-header">
          <span class="json-title">요청</span>
          <button class="btn btn-primary btn-sm" id="btn-run-complete">완료 실행</button>
        </div>
        <pre id="json-complete-req" class="json-body"></pre>
      </div>
      <div class="json-panel">
        <div class="json-header"><span class="json-title">응답 (주문 생성)</span></div>
        <pre id="json-complete-res" class="json-body"></pre>
      </div>
    </div>
    <div class="callout hidden" id="order-success-msg" style="margin-bottom: 24px;">
      <strong>성공!</strong> 주문 ID: <span id="display-order-id"></span> 생성됨.
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="mintInstrument">&larr; 이전</button>
      <button class="btn btn-primary hidden" id="nav-to-webhook" data-nav="webhookSimulation">다음 단계 &rarr;</button>
    </div>
  </div>

  <!-- VIEW: Webhook Simulation (Step 8) -->
  <div id="view-webhookSimulation" class="section">
    <h2 class="title">8. Webhook 시뮬레이션</h2>
    <p class="desc">백엔드 이벤트(예: 배송센터 업데이트)가 Agent로 webhook을 푸시하는 과정을 시뮬레이션합니다.</p>
    <div class="grid">
      <div class="card">
        <h3>이벤트 트리거</h3>
        <p style="color:var(--text-secondary); margin-bottom: 12px; font-size: 0.85rem;">이 동작은 Business 서버에서 실행되며 Platform webhook URL로 데이터를 푸시합니다.</p>
        <button class="btn btn-primary" id="btn-run-webhook">"배송됨" 이벤트 시뮬레이션</button>
      </div>
      <div class="json-panel">
        <div class="json-header">
          <span class="json-title">Webhook Payload (POST)</span>
          <span class="badge">푸시 알림</span>
        </div>
        <pre id="json-webhook-req" class="json-body">// 이벤트 트리거를 기다리는 중...</pre>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" data-nav="completeCheckout">&larr; 이전</button>
    </div>
  </div>

  <!-- About callout footer -->
  <div class="callout" style="margin-top: 48px;">
    <div class="calloutTitle">이 데모에 대해</div>
    <div class="calloutBody">이 playground는 브라우저에서 동작하는 시뮬레이션입니다. UCP 프로토콜 흐름을 설명하기 위한 mock 로직을 사용하며, 프로덕션 코드 레퍼런스로 사용되도록 설계되지는 않았습니다. 실제 구현 예시와 모범 사례는 <a href="https://github.com/Universal-Commerce-Protocol/samples" target="_blank">GitHub samples</a>를 참고하세요.</div>
  </div>

</div>

<script>
(() => {
/**
 * ------------------------------------------------------------------
 * 1. MOCK DATA
 * ------------------------------------------------------------------
 */
const UcpData = {
  version: "2026-01-11",

  inventory: {
    "sku_stickers": { title: "UCP Demo Sticker Pack", price: 599, image_url: "https://example.com/images/stickers.jpg" },
    "sku_mug": { title: "UCP Demo Mug", price: 1999, image_url: "https://example.com/images/mug.jpg" }
  },

  payment_handlers: {
    "com.shopify.shop_pay": [
      {
        id: "shop_pay",
        version: "2026-01-11",
        spec: "https://shopify.dev/docs/agents/checkout/shop-pay-handler",
        config_schema: "https://shopify.dev/ucp/shop-pay-handler/2026-01-11/config.json",
        instrument_schemas: ["https://shopify.dev/ucp/shop-pay-handler/2026-01-11/instrument.json"],
        config: { shop_id: "shopify-559128571" }
      }
    ],
    "com.google.pay": [
      {
        id: "gpay",
        version: "2026-01-11",
        spec: "https://pay.google.com/gp/p/ucp/2026-01-11/",
        config_schema: "https://pay.google.com/gp/p/ucp/2026-01-11/schemas/config.json",
        instrument_schemas: [
          "https://pay.google.com/gp/p/ucp/2026-01-11/schemas/card_payment_instrument.json"
        ],
        config: {
          api_version: 2,
          api_version_minor: 0,
          environment: "TEST",
          merchant_info: {
            merchant_name: "Example Merchant",
            merchant_id: "01234567890123456789",
            merchant_origin: "checkout.merchant.com",
            auth_jwt: "edxsdfoaisjdfapsodjf...."
          },
          allowed_payment_methods: [
            {
              type: "CARD",
              parameters: {
                allowed_auth_methods: ["PAN_ONLY", "CRYPTOGRAM_3DS"],
                allowed_card_networks: ["VISA", "MASTERCARD"]
              },
              tokenization_specification: {
                type: "PAYMENT_GATEWAY",
                parameters: {
                  gateway: "example",
                  gatewayMerchantId: "exampleGatewayMerchantId"
                }
              }
            }
          ]
        }
      }
    ]
  },

  capabilities: {
    "dev.ucp.shopping.checkout": [
      {
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/checkout",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/checkout.json"
      }
    ],
    "dev.ucp.shopping.order": [
      {
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/order",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/order.json"
      }
    ],
    "dev.ucp.shopping.fulfillment": [
      {
        extends: "dev.ucp.shopping.checkout",
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/fulfillment",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/fulfillment.json",
        config: {
          allows_multi_destination: {
            shipping: false,
            pickup: false
          },
          allows_method_combinations: [
            ["shipping"],
            ["pickup"]
          ]
        }
      }
    ],
    "dev.ucp.shopping.discount": [
      {
        extends: "dev.ucp.shopping.checkout",
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/discount",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/discount.json"
      }
    ],
    "dev.ucp.shopping.buyer_consent": [
      {
        extends: "dev.ucp.shopping.checkout",
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/buyer-consent",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/buyer_consent.json"
      }
    ],
    "dev.ucp.shopping.ap2_mandates": [
      {
        extends: "dev.ucp.shopping.checkout",
        version: "2026-01-23",
        spec: "https://ucp.dev/2026-01-23/specification/ap2-mandates",
        schema: "https://ucp.dev/2026-01-23/schemas/shopping/ap2_mandate.json"
      }
    ]
  },

  agents: {
    basic: {
      label: "표준",
      description: "코어 Checkout 및 Order capability를 지원합니다.",
      caps: ["dev.ucp.shopping.checkout", "dev.ucp.shopping.order"]
    },
    full: {
      label: "전체",
      description: "코어 + Fulfillment 및 Discount 확장을 지원합니다.",
      caps: ["dev.ucp.shopping.checkout", "dev.ucp.shopping.order", "dev.ucp.shopping.fulfillment", "dev.ucp.shopping.discount", "dev.ucp.shopping.buyer_consent", "dev.ucp.shopping.ap2_mandates"]
    }
  },

  mock_instruments: {
    shop_pay: {
      "handler_id": "shop_pay_1234",
      "type": "shop_pay",
      "email": "buyer@example.com",
      "id": "instr_sp_1338ef2c-3913-4267-83a2-a84d07d9a6a6"
    },
    gpay: {
      "handler_id": "gpay_1234",
      "type": "card",
      "display": {
        "brand": "visa",
        "last_digits": "4242"
      },
      "billing_address": {
        "street_address": "123 Main Street",
        "extended_address": "Suite 400",
        "address_locality": "Charleston",
        "address_region": "SC",
        "postal_code": "29401",
        "address_country": "US",
        "first_name": "Jane",
        "last_name": "Smith"
      },
      "id": "instr_gp_msg_084a3d56-3491-4b5e-ae3e-b1c45b22fa50"
    }
  }
};

/**
 * ------------------------------------------------------------------
 * 2. BACKEND SIMULATION
 * ------------------------------------------------------------------
 */
class UcpBackend {
  constructor() {
    this.session = null;
    this.currentOrder = null;
  }

  genId(prefix) {
    const r = crypto.randomUUID ? crypto.randomUUID().substring(0, 8) : Math.random().toString(36).substr(2, 9);
    return `${prefix}_${r}`;
  }

  getDiscoveryProfile() {
    return {
      ucp: {
        version: UcpData.version,
        capabilities: UcpData.capabilities,
        payment_handlers: UcpData.payment_handlers
      }
    };
  }

  createCheckout(requestPayload, activeCaps) {
    const lineItems = requestPayload.line_items.map((li, index) => {
      const product = UcpData.inventory[li.item.id];
      const qty = li.quantity || 1;
      const totalAmount = product.price * qty;
      return {
        id: `li_${index + 1}`,
        item: { ...li.item, title: product.title, price: product.price, image_url: product.image_url },
        quantity: qty,
        totals: [{ type: "subtotal", amount: totalAmount }, { type: "total", amount: totalAmount }]
      };
    });

    const subtotal = lineItems.reduce((acc, li) => acc + li.totals.find(t=>t.type==='total').amount, 0);

    const messages = [];
    const isFullAgent = Object.keys(activeCaps).some(name => name.includes("fulfillment"));

    if (!requestPayload.buyer?.email) {
      messages.push({
        type: "error",
        code: "missing",
        path: "$.buyer.email",
        severity: "requires_buyer_input",
        content: "Checkout을 위해 구매자 이메일이 필요합니다."
      });
    }

    if (isFullAgent) {
      const hasShipping = requestPayload.fulfillment?.methods?.some(m => m.type === 'shipping' && m.destinations?.length > 0);
      if (!hasShipping && requestPayload.fulfillment) {
         messages.push({
          type: "error",
          code: "missing",
          path: "$.fulfillment.methods[0].destinations",
          severity: "requires_buyer_input",
          content: "배송지가 누락되었습니다."
        });
      }
    }

    this.session = {
      ucp: { version: UcpData.version, capabilities: activeCaps, payment_handlers: UcpData.payment_handlers },
      id: this.genId('chk'),
      status: messages.length > 0 ? "incomplete" : "ready_for_complete",
      line_items: lineItems,
      currency: "USD",
      totals: [{ type: "subtotal", amount: subtotal }, { type: "total", amount: subtotal }],
      messages: messages
    };

    return this.session;
  }

  updateCheckout(patchPayload) {
    if (!this.session) throw new Error("Session not found");

    if (patchPayload.buyer) {
      this.session.buyer = { ...this.session.buyer, ...patchPayload.buyer };
    }

    if (patchPayload.fulfillment) {
      this.session.fulfillment = { ...this.session.fulfillment, ...patchPayload.fulfillment };

      const methods = this.session.fulfillment.methods || [];
      const hasValidDest = methods.some(m => m.destinations && m.destinations.length > 0);

      if (hasValidDest) {
        const shippingCost = 500;
        this.session.totals = this.session.totals.filter(t => t.type !== 'fulfillment');
        this.session.totals.push({ type: "fulfillment", amount: shippingCost, display_text: "표준 배송" });

        const sub = this.session.totals.find(t => t.type === 'subtotal')?.amount || 0;
        const totalObj = this.session.totals.find(t => t.type === 'total');
        if (totalObj) totalObj.amount = sub + shippingCost;
      }
    }

    const newMessages = [];
    if (!this.session.buyer?.email) {
      newMessages.push({
        type: "error", code: "missing", path: "$.buyer.email", severity: "requires_buyer_input", content: "Buyer email is required."
      });
    }

    const isFullAgent = Object.keys(this.session.ucp.capabilities).some(name => name.includes("fulfillment"));
    if(isFullAgent) {
        const hasDest = this.session.fulfillment?.methods?.[0]?.destinations?.length > 0;
        if(!hasDest && this.session.fulfillment) {
            newMessages.push({
                type: "error", code: "missing", path: "$.fulfillment.methods[0].destinations", severity: "requires_buyer_input", content: "배송지가 필요합니다."
            });
        }
    }

    this.session.messages = newMessages;
    this.session.status = newMessages.length > 0 ? "incomplete" : "ready_for_complete";

    return this.session;
  }

  completeCheckout(paymentInstrument) {
    if (!this.session) throw new Error("Session expired");

    const orderId = this.genId('ord');

    const orderLineItems = this.session.line_items.map(li => ({
        id: li.id,
        item: li.item,
        quantity: {
            total: li.quantity,
            fulfilled: 0
        },
        totals: li.totals,
        status: "processing"
    }));

    let fulfillmentObj = {};
    const method = this.session.fulfillment?.methods?.[0];

    if (method && method.type === 'shipping' && method.destinations?.[0]) {
        fulfillmentObj = {
            expectations: [{
                id: this.genId('exp'),
                line_items: orderLineItems.map(li => ({ id: li.id, quantity: li.quantity.total })),
                method_type: "shipping",
                destination: method.destinations[0],
                description: "Standard Shipping (Arrives in 3-5 days)",
                fulfillable_on: new Date().toISOString()
            }],
            events: []
        };
    }

    const order = {
      ucp: {
          version: UcpData.version,
          capabilities: this.session.ucp.capabilities
      },
      id: orderId,
      checkout_id: this.session.id,
      permalink_url: `https://example-merchant.com/orders/${orderId}`,
      line_items: orderLineItems,
      fulfillment: fulfillmentObj,
      adjustments: [],
      totals: this.session.totals
    };

    this.session.status = "completed";
    this.currentOrder = order;
    return order;
  }

  triggerDeliveryWebhook() {
    if (!this.currentOrder) throw new Error("No active order found.");

    const order = this.currentOrder;
    const eventId = this.genId("evt");
    const eventTime = new Date().toISOString();

    const eventLineItems = order.line_items.map(li => ({
        id: li.id,
        quantity: li.quantity.total
    }));

    const newEvent = {
        id: eventId,
        occurred_at: eventTime,
        type: "shipped",
        line_items: eventLineItems,
        tracking_number: "1Z999AA10123456784",
        tracking_url: "https://example-carrier.com/track/1Z999AA10123456784",
        carrier: "Mock Express",
        description: "패키지가 운송사에 인계되었습니다."
    };

    if (!order.fulfillment) order.fulfillment = { events: [], expectations: [] };
    if (!order.fulfillment.events) order.fulfillment.events = [];
    order.fulfillment.events.push(newEvent);

    order.line_items.forEach(li => {
        li.quantity.fulfilled = li.quantity.total;
        li.status = "fulfilled";
    });

    const webhookPayload = {
        ...order,
        event_id: eventId,
        created_time: eventTime
    };

    return webhookPayload;
  }
}

/**
 * ------------------------------------------------------------------
 * 3. FRONTEND CONTROLLER
 * ------------------------------------------------------------------
 */
class UcpApp {
  constructor() {
    this.backend = new UcpBackend();
    this.state = {
      step: 'profiles',
      agent: 'basic',
      activeCaps: [],
      scenario: 'missing_buyer',
      selectedHandler: 'shop_pay',
      lastRequests: {}
    };

    // Added 'webhookSimulation' as the official 8th step
    this.steps = [
      'profiles', 'discovery', 'negotiation',
      'createCheckout', 'updateCheckout',
      'mintInstrument', 'completeCheckout', 'webhookSimulation'
    ];
    this.init();
  }

  init() {
    this.renderStepper();
    this.bindEvents();
    this.updateProfilesView();
  }

  renderStepper() {
    const container = document.getElementById('stepper');
    container.innerHTML = this.steps.map((s, i) => `
      <button class="step-btn ${s === this.state.step ? 'active' : ''}" data-step="${s}">
        <span class="step-num">${i + 1}</span> ${s.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
      </button>
    `).join('');
  }

  setJson(elementId, data) {
    document.getElementById(elementId).textContent = JSON.stringify(data, null, 2);
  }

  navigateTo(stepName) {
    this.state.step = stepName;
    document.querySelectorAll('.section').forEach(el => el.classList.remove('active'));
    document.getElementById(`view-${stepName}`).classList.add('active');
    document.querySelectorAll('.step-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.step === stepName);
    });

    if (stepName === 'profiles') this.updateProfilesView();
    if (stepName === 'discovery') this.runDiscovery();
    if (stepName === 'negotiation') this.runNegotiation();
    if (stepName === 'createCheckout') this.prepareCreatePayload();
  }

  updateProfilesView() {
    const type = this.state.agent;
    const profile = UcpData.agents[type];

    document.getElementById('agent-desc').textContent = profile.description;

    const capabilities = {};
    profile.caps.forEach(name => {
      if (UcpData.capabilities[name]) {
        capabilities[name] = UcpData.capabilities[name];
      }
    });

    this.setJson('json-profiles', { ucp: { version: UcpData.version, capabilities, payment_handlers: UcpData.payment_handlers } });
  }

  runDiscovery() {
    const fullProfile = this.backend.getDiscoveryProfile();
    const agentCapNames = UcpData.agents[this.state.agent].caps;

    const filteredCaps = {};
    agentCapNames.forEach(name => {
      if (fullProfile.ucp.capabilities[name]) {
        filteredCaps[name] = fullProfile.ucp.capabilities[name];
      }
    });

    const displayProfile = {
      ...fullProfile,
      ucp: { ...fullProfile.ucp, capabilities: filteredCaps, payment_handlers: fullProfile.ucp.payment_handlers }
    };

    this.setJson('json-disc-res', displayProfile);
  }

  runNegotiation() {
    const bizProfile = this.backend.getDiscoveryProfile();
    this.setJson('json-neg-biz', bizProfile.ucp.capabilities);

    const agentCapsNames = UcpData.agents[this.state.agent].caps;
    const active = {};
    agentCapsNames.forEach(name => {
      if (bizProfile.ucp.capabilities[name]) {
        active[name] = bizProfile.ucp.capabilities[name];
      }
    });
    this.state.activeCaps = active;

    this.setJson('json-neg-active', active);
  }

  prepareCreatePayload() {
    const scenarioSelect = document.getElementById('input-create-scenario');
    const isFull = this.state.agent === 'full';
    scenarioSelect.innerHTML = `
      <option value="missing_buyer">구매자 이메일 누락</option>
      ${isFull ? '<option value="missing_shipping">배송지 누락</option>' : ''}
    `;
    if (!isFull && this.state.scenario === 'missing_shipping') {
        this.state.scenario = 'missing_buyer';
        scenarioSelect.value = 'missing_buyer';
    } else {
        scenarioSelect.value = this.state.scenario;
    }

    const payload = {
      line_items: [{ item: { id: "sku_stickers" }, quantity: 2 }, { item: { id: "sku_mug" }, quantity: 1 }],
      buyer: {},
      payment: { instruments: [UcpData.mock_instruments.shop_pay] }
    };

    if (Object.keys(this.state.activeCaps).some(name => name.includes('fulfillment'))) {
        payload.fulfillment = { methods: [] };
    }

    this.state.lastRequests.create = payload;
    this.setJson('json-create-req', payload);
    this.setJson('json-create-res', { hint: "Click '요청 실행' to send..." });
    document.getElementById('nav-to-update').disabled = true;
  }

  executeCreateCheckout() {
    const req = JSON.parse(JSON.stringify(this.state.lastRequests.create));
    const scenario = this.state.scenario;

    if (scenario === 'missing_buyer') {
        delete req.buyer.email;
    } else {
        req.buyer.email = "test@example.com";
        req.buyer.name = "Test User";
    }

    if (scenario === 'missing_shipping' || req.fulfillment) {
        if (!req.fulfillment) {
            req.fulfillment = { methods: [] };
        }
        if (scenario === 'missing_shipping') {
            req.fulfillment.methods = [{ type: 'shipping', destinations: [] }];
            req.buyer.email = "test@example.com";
            req.buyer.name = "Test User";
        } else {
            req.fulfillment.methods = [{ type: 'shipping', destinations: [{ id: "addr_1", street: "123 Main St", city: "Tech City", country: "US", postal_code: "94103" }] }];
        }
    }

    this.setJson('json-create-req', req);
    try {
      const res = this.backend.createCheckout(req, this.state.activeCaps);
      this.setJson('json-create-res', res);
      document.getElementById('nav-to-update').disabled = false;
      this.prepareUpdatePayload(res);
    } catch (e) {
      this.setJson('json-create-res', { error: e.message });
    }
  }

  prepareUpdatePayload(checkoutResponse) {
    const patch = { id: checkoutResponse.id };
    const errors = checkoutResponse.messages || [];

    if (errors.some(e => e.path === "$.buyer.email")) {
      patch.buyer = { email: "fixed_user@example.com", name: "Fixed User" };
    }

    if (errors.some(e => e.path.includes('destinations'))) {
      patch.fulfillment = {
        methods: [{
            type: "shipping",
            destinations: [{ id: "addr_1", street: "123 Main St", city: "Tech City", country: "US", postal_code: "94103" }]
        }]
      };
    }

    this.state.lastRequests.update = patch;
    this.setJson('json-update-req', patch);
    this.setJson('json-update-res', { hint: "Click '업데이트 실행'..." });
    document.getElementById('nav-to-mint').disabled = true;
  }

  executeUpdateCheckout() {
    try {
      const res = this.backend.updateCheckout(this.state.lastRequests.update);
      this.setJson('json-update-res', res);

      if(res.status === 'ready_for_complete') {
        document.getElementById('nav-to-mint').disabled = false;
      }
    } catch (e) {
      this.setJson('json-update-res', { error: e.message });
    }
  }

  executeMint() {
    const handlerId = this.state.selectedHandler;
    const baseInstrument = UcpData.mock_instruments[handlerId];
    const instrument = JSON.parse(JSON.stringify(baseInstrument));

    const tokenStr = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substring(2);

    if (handlerId === 'gpay') {
      instrument.credential = { type: "PAYMENT_GATEWAY", token: "gpaytok_" + tokenStr };
    } else if (handlerId === 'shop_pay') {
      instrument.credential = { type: "ShopPayToken", token: "shoppay_tok_" + tokenStr };
    }

    instrument.selected = true;

    this.state.lastRequests.instrument = instrument;
    this.setJson('json-mint-res', instrument);
    document.getElementById('nav-to-complete').disabled = false;
    this.setJson('json-complete-req', { payment: instrument });
  }

  executeComplete() {
    try {
      const res = this.backend.completeCheckout(this.state.lastRequests.instrument);
      this.setJson('json-complete-res', res);
      document.getElementById('display-order-id').textContent = res.id;
      document.getElementById('order-success-msg').classList.remove('hidden');

      // Reveal link to next step
      document.getElementById('nav-to-webhook').classList.remove('hidden');
    } catch (e) {
      this.setJson('json-complete-res', { error: e.message });
    }
  }

  executeWebhook() {
    try {
      const payload = this.backend.triggerDeliveryWebhook();
      this.setJson('json-webhook-req', payload);
    } catch(e) {
      this.setJson('json-webhook-req', { error: e.message });
    }
  }

  bindEvents() {
    document.getElementById('input-agent-type').addEventListener('change', (e) => {
      this.state.agent = e.target.value;
      this.updateProfilesView();
    });

    document.getElementById('input-create-scenario').addEventListener('change', (e) => {
      this.state.scenario = e.target.value;
    });

    document.body.addEventListener('click', (e) => {
      const navTarget = e.target.closest('[data-nav]');
      if (navTarget && !navTarget.disabled) this.navigateTo(navTarget.dataset.nav);

      const stepTarget = e.target.closest('[data-step]');
      if (stepTarget) this.navigateTo(stepTarget.dataset.step);

      const copyTarget = e.target.closest('[data-copy]');
      if (copyTarget) {
         navigator.clipboard.writeText(document.getElementById(copyTarget.dataset.copy).textContent);
      }
    });

    document.getElementById('btn-run-create').addEventListener('click', () => this.executeCreateCheckout());
    document.getElementById('btn-run-update').addEventListener('click', () => this.executeUpdateCheckout());
    document.getElementById('btn-run-mint').addEventListener('click', () => this.executeMint());
    document.getElementById('btn-run-complete').addEventListener('click', () => this.executeComplete());
    document.getElementById('btn-run-webhook').addEventListener('click', () => this.executeWebhook());

    document.querySelectorAll('.handler-opt').forEach(el => {
      el.addEventListener('click', () => {
        document.querySelectorAll('.handler-opt').forEach(x => x.classList.remove('selected'));
        el.classList.add('selected');
        this.state.selectedHandler = el.dataset.handler;
      });
    });
  }
}

function startUcpPlayground() {
  if (document.getElementById('stepper')) {
    new UcpApp();
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', startUcpPlayground);
} else {
  startUcpPlayground();
}

window.addEventListener('popstate', startUcpPlayground);
})();
</script>
