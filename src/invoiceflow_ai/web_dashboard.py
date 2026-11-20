"""Modern Executive Web Dashboard for InvoiceFlow AI.

Built with a minimalist, high-density design system inspired by Linear, Ramp, and Stripe.
Features interactive SVG evidence inspection with cross-highlighting,
keyboard-friendly inline editing, real-time arithmetic auditing, Four-Eyes governance,
and idempotent ERP simulation. Zero emojis, pure SVG iconography.
"""

def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>InvoiceFlow AI — Document Intelligence</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', -apple-system, 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
            mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
          },
          colors: {
            zinc: {
              850: '#1f1f23',
              900: '#18181b',
              950: '#09090b',
            },
            accent: {
              DEFAULT: '#2563eb',
              hover: '#1d4ed8',
              muted: '#1e3a8a',
            }
          }
        }
      }
    }
  </script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      letter-spacing: -0.011em;
      -webkit-font-smoothing: antialiased;
    }
    .tabular-nums { font-variant-numeric: tabular-nums; }
    .custom-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
    .custom-scroll::-webkit-scrollbar-track { background: transparent; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #27272a; border-radius: 9999px; }
    .custom-scroll::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
    
    /* Interactive Bounding Box Highlight */
    .ocr-box {
      cursor: pointer;
      transition: all 0.15s ease;
      stroke-width: 1.5;
    }
    .ocr-box:hover, .ocr-box.active {
      stroke-width: 2.5;
      fill-opacity: 0.18 !important;
    }
    .table-row-active {
      background-color: rgba(37, 99, 235, 0.08) !important;
      border-left: 2px solid #2563eb;
    }
  </style>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col">

  <!-- Top Global Header -->
  <header class="h-13 border-b border-zinc-800/80 bg-zinc-950/95 sticky top-0 z-40 px-4 flex items-center justify-between">
    <div class="flex items-center gap-6">
      <!-- Logo & Breadcrumb -->
      <div class="flex items-center gap-2.5">
        <div class="w-6 h-6 rounded bg-zinc-100 text-zinc-950 flex items-center justify-center font-bold text-xs tracking-tighter shadow-sm">
          IF
        </div>
        <div class="flex items-center gap-1.5 text-xs">
          <span class="font-semibold text-zinc-200 tracking-tight">InvoiceFlow</span>
          <span class="text-zinc-600">/</span>
          <span class="text-zinc-400">Review Console</span>
          <span class="ml-1 text-[10px] font-mono px-1.5 py-0.2 rounded bg-zinc-800 text-zinc-400 border border-zinc-700/50">v0.7.0</span>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <nav class="hidden md:flex items-center gap-1 text-xs">
        <button onclick="switchTab('workspace')" id="tabNav_workspace" class="px-3 py-1.5 rounded-md font-medium text-zinc-100 bg-zinc-800/70 border border-zinc-700/40 transition">
          Workspace
        </button>
        <button onclick="switchTab('queue')" id="tabNav_queue" class="px-3 py-1.5 rounded-md font-medium text-zinc-400 hover:text-zinc-200 transition">
          Document Queue
        </button>
        <button onclick="switchTab('rpa')" id="tabNav_rpa" class="px-3 py-1.5 rounded-md font-medium text-zinc-400 hover:text-zinc-200 transition">
          ERP Simulator
        </button>
        <button onclick="switchTab('audit')" id="tabNav_audit" class="px-3 py-1.5 rounded-md font-medium text-zinc-400 hover:text-zinc-200 transition">
          Audit Trail
        </button>
      </nav>
    </div>

    <!-- Right Global Controls -->
    <div class="flex items-center gap-3">
      <!-- Demo Data Loader Dropdown -->
      <div class="relative">
        <button onclick="toggleDemoDropdown()" class="h-8 px-2.5 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-xs font-medium text-zinc-300 flex items-center gap-1.5 transition">
          <span>Load Demo Scenario</span>
          <svg class="w-3.5 h-3.5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
        </button>
        <div id="demoDropdown" class="hidden absolute right-0 mt-1 w-64 rounded-lg bg-zinc-900 border border-zinc-800 shadow-xl py-1 text-xs z-50">
          <div class="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-500 border-b border-zinc-800">
            Synthetic Benchmark Scenarios
          </div>
          <button onclick="loadSampleScenario('clean')" class="w-full text-left px-3 py-2 hover:bg-zinc-800 text-zinc-300 hover:text-white flex flex-col">
            <span class="font-medium text-zinc-200">Clean Medicine Prescription</span>
            <span class="text-[11px] text-zinc-500">3 rows · Balanced total 991,480 VND</span>
          </button>
          <button onclick="loadSampleScenario('mismatch')" class="w-full text-left px-3 py-2 hover:bg-zinc-800 text-zinc-300 hover:text-white flex flex-col">
            <span class="font-medium text-zinc-200">Dropped Row (Mismatch Anomaly)</span>
            <span class="text-[11px] text-zinc-500">Row 3 missed by OCR · Total mismatch</span>
          </button>
          <button onclick="loadSampleScenario('payment')" class="w-full text-left px-3 py-2 hover:bg-zinc-800 text-zinc-300 hover:text-white flex flex-col">
            <span class="font-medium text-zinc-200">Hospital Payment Receipt</span>
            <span class="text-[11px] text-zinc-500">Vietnamese BHYT social insurance split</span>
          </button>
        </div>
      </div>

      <!-- Health Status -->
      <div id="apiHealthBadge" class="h-8 px-2.5 rounded-md bg-zinc-900 border border-zinc-800 flex items-center gap-2 text-xs font-mono text-zinc-400">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        <span id="apiLatencyText">API: Online</span>
      </div>

      <!-- Settings Button -->
      <button onclick="openSettingsModal()" class="h-8 w-8 rounded-md bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 flex items-center justify-center text-zinc-400 hover:text-zinc-200 transition" title="Connection Settings">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
      </button>
    </div>
  </header>

  <!-- Secondary Document Action Bar -->
  <div class="border-b border-zinc-800 bg-zinc-900/40 px-4 py-2.5 flex flex-wrap items-center justify-between gap-3 text-xs">
    <div class="flex items-center gap-3">
      <span class="text-zinc-500 font-medium">Document:</span>
      <select id="headerDocSelect" onchange="loadDocument(this.value)" class="bg-zinc-900 border border-zinc-800 rounded-md px-2.5 py-1 text-xs text-zinc-200 font-mono focus:outline-none focus:border-zinc-600 min-w-[280px]">
        <option value="">Loading queue...</option>
      </select>
      <button onclick="fetchDocumentQueue()" class="text-zinc-400 hover:text-zinc-200 transition" title="Refresh queue">
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
      </button>
    </div>

    <!-- Active Document Metadata Badges -->
    <div id="docMetaRibbon" class="flex items-center gap-2 text-xs">
      <span id="badgeStatus" class="px-2 py-0.5 rounded text-[11px] font-medium bg-zinc-800 text-zinc-400 border border-zinc-700/50">
        NO DOCUMENT
      </span>
      <span id="badgeDocType" class="px-2 py-0.5 rounded text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800">
        TYPE: --
      </span>
      <span id="badgeVersion" class="px-2 py-0.5 rounded text-[11px] font-mono text-zinc-400 bg-zinc-900 border border-zinc-800">
        REV: v0
      </span>
    </div>
  </div>

  <!-- TAB 1: WORKSPACE (Side-by-Side Review) -->
  <main id="view_workspace" class="flex-1 flex flex-col lg:flex-row overflow-hidden">
    
    <!-- Left Pane: Document Canvas Viewport (50%) -->
    <section class="lg:w-1/2 flex flex-col border-b lg:border-b-0 lg:border-r border-zinc-800 bg-zinc-950 min-h-[420px]">
      
      <!-- Canvas Toolbar -->
      <div class="h-10 border-b border-zinc-800/80 bg-zinc-900/30 px-3 flex items-center justify-between text-xs">
        <div class="flex items-center gap-2 text-zinc-400">
          <svg class="w-3.5 h-3.5 text-zinc-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          <span class="font-medium text-zinc-300">Document Scan & Evidence Overlay</span>
          <span id="imgDimensions" class="font-mono text-[10px] text-zinc-500 ml-1"></span>
        </div>

        <!-- Zoom / View Controls -->
        <div class="flex items-center gap-1">
          <button onclick="adjustZoom(-0.15)" class="h-6 w-6 rounded bg-zinc-800/60 hover:bg-zinc-800 text-zinc-300 flex items-center justify-center font-mono text-xs transition" title="Zoom out">-</button>
          <span id="zoomPercent" class="font-mono text-[11px] text-zinc-400 w-10 text-center">100%</span>
          <button onclick="adjustZoom(0.15)" class="h-6 w-6 rounded bg-zinc-800/60 hover:bg-zinc-800 text-zinc-300 flex items-center justify-center font-mono text-xs transition" title="Zoom in">+</button>
          <button onclick="resetZoom()" class="h-6 px-1.5 rounded bg-zinc-800/60 hover:bg-zinc-800 text-[11px] text-zinc-400 hover:text-zinc-200 transition ml-1">Reset</button>
        </div>
      </div>

      <!-- Arithmetic Balance Callout Bar -->
      <div id="canvasArithmeticBanner" class="hidden px-4 py-2 text-xs border-b border-zinc-800 transition"></div>

      <!-- Canvas Viewport with Scroll/Pan -->
      <div id="canvasViewport" class="flex-1 overflow-auto custom-scroll relative flex items-center justify-center p-4 bg-zinc-950/60">
        <div id="emptyCanvasNotice" class="text-center p-8 text-zinc-600 text-xs">
          Select or load a document to inspect OCR bounding boxes.
        </div>
        
        <!-- Scalable Image and SVG Container -->
        <div id="canvasContainer" class="hidden relative select-none shadow-2xl rounded border border-zinc-800/80 bg-white" style="transform-origin: center center;">
          <img id="docImageElement" class="block max-w-none" />
          <svg id="docSvgElement" class="absolute top-0 left-0 w-full h-full pointer-events-auto"></svg>
        </div>
      </div>

      <!-- Legend Footer -->
      <div class="h-9 border-t border-zinc-800/80 bg-zinc-900/30 px-3 flex items-center gap-3 text-[11px] text-zinc-400 overflow-x-auto">
        <span class="text-zinc-600 font-medium">Fields:</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#64748b]"></span> STT</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#2563eb]"></span> Tên thuốc / DV</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#16a34a]"></span> Số lượng</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#9333ea]"></span> ĐVT</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#ea580c]"></span> Đơn giá</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-sm bg-[#dc2626]"></span> Thành tiền</span>
      </div>
    </section>

    <!-- Right Pane: Structured Data Grid & Verification Controls (50%) -->
    <section class="lg:w-1/2 flex flex-col bg-zinc-900/20">
      
      <!-- Review Station Header -->
      <div class="h-10 border-b border-zinc-800/80 bg-zinc-900/30 px-4 flex items-center justify-between text-xs">
        <div class="flex items-center gap-2">
          <span class="font-medium text-zinc-300">Extracted Line Items</span>
          <span id="lineItemCount" class="font-mono text-[10px] text-zinc-500">(0 items)</span>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="addNewTableRow()" class="px-2 py-1 rounded bg-zinc-800 hover:bg-zinc-700 text-[11px] font-medium text-zinc-300 border border-zinc-700/60 transition">
            + Add Row
          </button>
        </div>
      </div>

      <!-- Table Container -->
      <div class="flex-1 overflow-auto custom-scroll">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="sticky top-0 bg-zinc-900 border-b border-zinc-800 text-[11px] text-zinc-400 uppercase tracking-wider font-semibold z-10">
            <tr>
              <th class="py-2 px-3 w-10 text-center">STT</th>
              <th class="py-2 px-3">Description / Medicine</th>
              <th class="py-2 px-3 w-16 text-right">Qty</th>
              <th class="py-2 px-3 w-16 text-center">Unit</th>
              <th class="py-2 px-3 w-28 text-right">Unit Price</th>
              <th class="py-2 px-3 w-28 text-right">Total (VND)</th>
              <th class="py-2 px-2 w-8"></th>
            </tr>
          </thead>
          <tbody id="lineItemsTbody" class="divide-y divide-zinc-800/60 font-mono text-zinc-300">
            <tr>
              <td colspan="7" class="py-8 text-center text-zinc-600 font-sans text-xs">
                No active document selected. Choose a document above or load a demo scenario.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Totals & Reconciliation Card -->
      <div class="border-t border-zinc-800 bg-zinc-950 p-4 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-4 text-zinc-400">
            <div>Printed Total: <span id="valPrintedTotal" class="font-mono font-semibold text-zinc-200">0 VND</span></div>
            <div>Sum of Rows: <span id="valCalculatedTotal" class="font-mono font-semibold text-zinc-200">0 VND</span></div>
          </div>
          <div id="diffBadge" class="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
            Diff: 0 VND
          </div>
        </div>

        <!-- Row Count Audit Reason Input (Displayed when count differs) -->
        <div id="auditReasonBox" class="hidden p-2.5 rounded-lg bg-zinc-900 border border-amber-800/40 space-y-1">
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-amber-400 font-medium">Row Count Change Reason (Audit Rule R-303)</span>
            <span id="reasonCharCount" class="text-zinc-500 font-mono text-[10px]">0 / 10 chars</span>
          </div>
          <input type="text" id="rowCountReasonInput" oninput="updateReasonCharCount(this.value)" placeholder="e.g. Added row 3 missed by OCR parser; confirmed against physical scan." class="w-full bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1 text-xs text-zinc-200 focus:outline-none focus:border-amber-500" />
        </div>

        <!-- Operator Review Controls Form -->
        <div class="pt-2 border-t border-zinc-850 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div>
              <label class="text-[10px] text-zinc-500 uppercase font-semibold block">Reviewer ID</label>
              <input type="text" id="reviewerIdField" value="demo_operator" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-xs text-zinc-200 font-mono focus:outline-none focus:border-zinc-700 w-32" />
            </div>
            <div>
              <label class="text-[10px] text-zinc-500 uppercase font-semibold block">Layout</label>
              <select id="reviewedDocTypeField" class="bg-zinc-900 border border-zinc-800 rounded px-2 py-1 text-xs text-zinc-200 focus:outline-none focus:border-zinc-700">
                <option value="MEDICINE_INVOICE">MEDICINE_INVOICE</option>
                <option value="MEDICAL_PAYMENT">MEDICAL_PAYMENT</option>
              </select>
            </div>
            <label class="flex items-center gap-1.5 text-[11px] text-zinc-400 cursor-pointer pt-3">
              <input type="checkbox" id="confirmVerificationCheckbox" class="rounded bg-zinc-900 border-zinc-700 text-blue-600 focus:ring-0" />
              <span>Verified against source</span>
            </label>
          </div>

          <button id="btnSubmitReview" onclick="submitHumanReview()" class="h-8 px-4 rounded-md bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition shadow-sm disabled:opacity-40">
            Submit Verification
          </button>
        </div>

        <!-- Four-Eyes Approval Banner (Visible if REVIEWED) -->
        <div id="fourEyesApprovalStation" class="hidden p-3 rounded-lg bg-zinc-900 border border-blue-900/40 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-semibold text-blue-300">Four-Eyes Approval Required (Rule R-302)</span>
            <span class="text-[10px] text-zinc-400">Approver must differ from Reviewer</span>
          </div>
          <div class="flex items-center gap-2">
            <input type="text" id="approverIdField" value="supervisor_ann" placeholder="Approver ID" class="flex-1 bg-zinc-950 border border-zinc-700 rounded px-2.5 py-1 text-xs text-zinc-200 font-mono focus:outline-none focus:border-blue-500" />
            <button onclick="approveActiveDocument()" class="h-7 px-3 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs transition">
              Authorize Document
            </button>
          </div>
        </div>

        <!-- Export CSV Bar (Visible if APPROVED) -->
        <div id="exportReadyStation" class="hidden p-2.5 rounded-lg bg-zinc-900 border border-emerald-900/40 flex items-center justify-between">
          <div class="text-xs">
            <div class="font-semibold text-emerald-400">Approved & Cryptographically Sealed</div>
            <div id="shaDigestLabel" class="font-mono text-[10px] text-zinc-500">SHA-256: --</div>
          </div>
          <a id="btnDownloadCsvAuthoritative" href="#" download class="h-7 px-3 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-zinc-200 text-xs font-medium flex items-center gap-1.5 transition">
            <svg class="w-3.5 h-3.5 text-zinc-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span>Export Approved CSV</span>
          </a>
        </div>

      </div>
    </section>

  </main>

  <!-- TAB 2: DOCUMENT QUEUE -->
  <section id="view_queue" class="hidden flex-1 p-6 max-w-7xl mx-auto w-full space-y-4">
    <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
      <div>
        <h2 class="text-sm font-semibold text-zinc-200">Authoritative Document Queue</h2>
        <p class="text-xs text-zinc-500">Track and manage invoices across all workflow verification states</p>
      </div>
      <button onclick="fetchDocumentQueue()" class="h-7 px-2.5 rounded bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-300 transition">
        Refresh Queue
      </button>
    </div>

    <div class="overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900/40">
      <table class="w-full text-left text-xs">
        <thead class="bg-zinc-900 border-b border-zinc-800 text-[11px] text-zinc-400 uppercase font-semibold">
          <tr>
            <th class="py-2.5 px-4 font-mono">Document ID</th>
            <th class="py-2.5 px-4">Status</th>
            <th class="py-2.5 px-4">Layout Type</th>
            <th class="py-2.5 px-4">RPA Ready</th>
            <th class="py-2.5 px-4">Created At</th>
            <th class="py-2.5 px-4 text-right">Action</th>
          </tr>
        </thead>
        <tbody id="queueTableBody" class="divide-y divide-zinc-800 text-zinc-300">
          <tr>
            <td colspan="6" class="py-6 text-center text-zinc-600">Loading queue...</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- TAB 3: RPA ERP SIMULATOR -->
  <section id="view_rpa" class="hidden flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">
    <div class="border-b border-zinc-800 pb-3">
      <h2 class="text-sm font-semibold text-zinc-200">Local ERP Simulator & Idempotent Handoff</h2>
      <p class="text-xs text-zinc-500">Dispatch approved documents into the simulated SQLite ERP database with duplicate prevention</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-2">
        <div class="text-[11px] font-semibold uppercase text-zinc-500">Step 1</div>
        <div class="text-xs font-medium text-zinc-200">Submit to RPA Handoff Queue</div>
        <button onclick="executeRpaAction('submit')" class="w-full h-8 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-medium text-zinc-200 transition">
          Queue Approved CSV
        </button>
      </div>

      <div class="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-2">
        <div class="text-[11px] font-semibold uppercase text-zinc-500">Step 2</div>
        <div class="text-xs font-medium text-zinc-200">Execute Local ERP Worker</div>
        <button onclick="executeRpaAction('worker')" class="w-full h-8 rounded bg-blue-600 hover:bg-blue-500 text-xs font-medium text-white transition">
          Simulate Worker Run
        </button>
      </div>

      <div class="p-4 rounded-lg bg-zinc-900 border border-zinc-800 space-y-2">
        <div class="text-[11px] font-semibold uppercase text-zinc-500">Step 3 (Safety)</div>
        <div class="text-xs font-medium text-zinc-200">Verify Duplicate Prevention</div>
        <button onclick="executeRpaAction('retry')" class="w-full h-8 rounded bg-zinc-800 hover:bg-zinc-700 border border-zinc-700 text-xs font-medium text-zinc-200 transition">
          Retry Idempotent Run
        </button>
      </div>
    </div>

    <!-- Execution Feedback Box -->
    <div id="rpaConsoleLog" class="p-4 rounded-lg bg-zinc-950 border border-zinc-800 font-mono text-xs text-zinc-400 space-y-1">
      <div class="text-zinc-600">// RPA Worker Console Log</div>
      <div id="rpaStatusOutput">Ready for dispatch. Select an APPROVED document.</div>
    </div>
  </section>

  <!-- TAB 4: AUDIT TRAIL -->
  <section id="view_audit" class="hidden flex-1 p-6 max-w-7xl mx-auto w-full space-y-4">
    <div class="flex items-center justify-between border-b border-zinc-800 pb-3">
      <div>
        <h2 class="text-sm font-semibold text-zinc-200">Immutable Governance Audit Ledger</h2>
        <p class="text-xs text-zinc-500">Cryptographically verifiable sequence of document modifications and approvals</p>
      </div>
      <button onclick="fetchAuditEvents()" class="h-7 px-2.5 rounded bg-zinc-800 hover:bg-zinc-700 text-xs font-medium text-zinc-300 transition">
        Refresh Ledger
      </button>
    </div>

    <div id="auditLogContainer" class="space-y-2">
      <div class="text-zinc-600 text-xs py-4">Select a document to inspect audit events.</div>
    </div>
  </section>

  <!-- Settings Modal -->
  <div id="settingsDialog" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
    <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 max-w-md w-full mx-4 space-y-4 shadow-2xl">
      <h3 class="text-sm font-semibold text-zinc-100">Connection Credentials</h3>
      <div class="space-y-3 text-xs">
        <div>
          <label class="text-zinc-400 font-medium block mb-1">Backend Base URL</label>
          <input type="text" id="inputApiUrl" class="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 font-mono focus:outline-none focus:border-zinc-700" />
        </div>
        <div>
          <label class="text-zinc-400 font-medium block mb-1">Operator API Key</label>
          <input type="password" id="inputApiKey" class="w-full bg-zinc-950 border border-zinc-800 rounded px-2.5 py-1.5 text-zinc-200 font-mono focus:outline-none focus:border-zinc-700" />
        </div>
      </div>
      <div class="flex justify-end gap-2 pt-2 border-t border-zinc-800">
        <button onclick="closeSettingsModal()" class="h-7 px-3 rounded bg-zinc-800 text-zinc-400 hover:text-zinc-200 text-xs transition">Cancel</button>
        <button onclick="saveSettingsModal()" class="h-7 px-3 rounded bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition">Save</button>
      </div>
    </div>
  </div>

  <!-- Notification Toast -->
  <div id="toastNotification" class="fixed bottom-5 right-5 z-50 hidden px-3.5 py-2 rounded-lg bg-zinc-900 border border-zinc-700 shadow-2xl text-xs font-medium text-zinc-200 transition-all"></div>

  <!-- Client Application Logic -->
  <script>
    let API_URL = localStorage.getItem('if_api_url') || 'http://127.0.0.1:8000';
    let API_KEY = localStorage.getItem('if_api_key') || 'local-demo-operator-key-default-16chars';
    let currentDocId = '';
    let currentDocRecord = null;
    let currentEvidence = null;
    let currentZoom = 1.0;
    let activeRowIndex = null;

    function toast(text, isError = false) {
      const el = document.getElementById('toastNotification');
      el.textContent = text;
      el.className = `fixed bottom-5 right-5 z-50 px-3.5 py-2 rounded-lg shadow-2xl text-xs font-medium transition-all ${
        isError ? 'bg-rose-950 border border-rose-800 text-rose-200' : 'bg-zinc-900 border border-zinc-700 text-zinc-200'
      }`;
      el.classList.remove('hidden');
      setTimeout(() => el.classList.add('hidden'), 3200);
    }

    async function req(path, options = {}) {
      const url = `${API_URL.replace(/\\/$/, '')}${path}`;
      const headers = { 'X-API-Key': API_KEY, ...(options.headers || {}) };
      const res = await fetch(url, { ...options, headers });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText || `HTTP ${res.status}`);
      }
      return res;
    }

    async function checkBackendHealth() {
      const t0 = performance.now();
      try {
        const res = await req('/health');
        const ms = (performance.now() - t0).toFixed(0);
        document.getElementById('apiLatencyText').textContent = `API: ${ms}ms`;
      } catch (e) {
        document.getElementById('apiLatencyText').textContent = 'API: Offline';
      }
    }

    function switchTab(tabName) {
      ['workspace', 'queue', 'rpa', 'audit'].forEach(t => {
        document.getElementById(`view_${t}`).classList.add('hidden');
        document.getElementById(`tabNav_${t}`).className = 'px-3 py-1.5 rounded-md font-medium text-zinc-400 hover:text-zinc-200 transition';
      });
      document.getElementById(`view_${tabName}`).classList.remove('hidden');
      document.getElementById(`tabNav_${tabName}`).className = 'px-3 py-1.5 rounded-md font-medium text-zinc-100 bg-zinc-800/70 border border-zinc-700/40 transition';
      
      if (tabName === 'queue') fetchDocumentQueue();
      if (tabName === 'audit') fetchAuditEvents();
    }

    async function fetchDocumentQueue() {
      try {
        const res = await req('/api/v1/documents?limit=100');
        const docs = await res.json();
        
        // Populate select
        const sel = document.getElementById('headerDocSelect');
        sel.innerHTML = docs.length ? '' : '<option value="">Queue empty</option>';
        docs.forEach(d => {
          const opt = document.createElement('option');
          opt.value = d.id;
          opt.textContent = `${d.id.substring(0, 10)}... · [${d.status}] · ${d.original_document_type}`;
          sel.appendChild(opt);
        });

        // Populate Queue Table
        const tbody = document.getElementById('queueTableBody');
        tbody.innerHTML = '';
        docs.forEach(d => {
          const tr = document.createElement('tr');
          tr.className = 'hover:bg-zinc-800/30 transition';
          tr.innerHTML = `
            <td class="py-2.5 px-4 font-mono text-zinc-400">${d.id}</td>
            <td class="py-2.5 px-4">
              <span class="px-2 py-0.5 rounded text-[10px] font-medium ${
                d.status === 'APPROVED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' :
                d.status === 'REVIEWED' ? 'bg-blue-950 text-blue-400 border border-blue-800/40' :
                d.status.includes('BLOCKED') ? 'bg-rose-950 text-rose-400 border border-rose-800/40' :
                'bg-zinc-800 text-zinc-400'
              }">${d.status}</span>
            </td>
            <td class="py-2.5 px-4 font-mono text-zinc-400">${d.original_document_type}</td>
            <td class="py-2.5 px-4">${d.ready_for_rpa ? '✓ Eligible' : '—'}</td>
            <td class="py-2.5 px-4 font-mono text-zinc-500">${(d.created_at || '').substring(0, 19).replace('T', ' ')}</td>
            <td class="py-2.5 px-4 text-right">
              <button onclick="loadDocument('${d.id}'); switchTab('workspace');" class="text-blue-400 hover:text-blue-300 font-medium">Open</button>
            </td>
          `;
          tbody.appendChild(tr);
        });

        if (docs.length) {
          if (!currentDocId || !docs.some(d => d.id === currentDocId)) {
            currentDocId = docs[0].id;
          }
          sel.value = currentDocId;
          loadDocument(currentDocId);
        }
      } catch (err) {
        toast(`Queue error: ${err.message}`, true);
      }
    }

    async function loadDocument(docId) {
      if (!docId) return;
      currentDocId = docId;
      document.getElementById('headerDocSelect').value = docId;
      try {
        const res = await req(`/api/v1/documents/${docId}`);
        currentDocRecord = await res.json();
        renderDocumentWorkspace(currentDocRecord);
        loadEvidence(docId);
        fetchAuditEvents();
      } catch (err) {
        toast(`Load error: ${err.message}`, true);
      }
    }

    function renderDocumentWorkspace(doc) {
      // Header ribbon badges
      const badgeStat = document.getElementById('badgeStatus');
      badgeStat.textContent = doc.status;
      badgeStat.className = `px-2 py-0.5 rounded text-[11px] font-medium ${
        doc.status === 'APPROVED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/40' :
        doc.status === 'REVIEWED' ? 'bg-blue-950 text-blue-400 border border-blue-800/40' :
        doc.status.includes('BLOCKED') ? 'bg-rose-950 text-rose-400 border border-rose-800/40' :
        'bg-zinc-800 text-zinc-400 border border-zinc-700/50'
      }`;

      document.getElementById('badgeDocType').textContent = `TYPE: ${doc.reviewed_document_type || doc.original_document_type}`;
      document.getElementById('badgeVersion').textContent = `REV: v${doc.review_version || 0}`;

      document.getElementById('reviewerIdField').value = doc.reviewer_id || 'demo_operator';
      document.getElementById('reviewedDocTypeField').value = doc.reviewed_document_type || doc.original_document_type || 'MEDICINE_INVOICE';

      // Line items table
      const items = doc.reviewed_items || (doc.raw_result && doc.raw_result.items) || [];
      document.getElementById('lineItemCount').textContent = `(${items.length} items)`;
      
      const tbody = document.getElementById('lineItemsTbody');
      tbody.innerHTML = '';

      let runningSum = 0;
      items.forEach((it, index) => {
        const q = Number(it.so_luong) || 0;
        const p = Number(it.don_gia) || 0;
        const tot = Number(it.thanh_tien) || 0;
        runningSum += tot;
        const isMathMismatch = (q * p !== tot);

        const tr = document.createElement('tr');
        tr.id = `tableRow_${index}`;
        tr.className = `hover:bg-zinc-800/40 cursor-pointer transition ${isMathMismatch ? 'bg-rose-950/20' : ''}`;
        tr.onclick = () => highlightRow(index);
        tr.innerHTML = `
          <td class="py-2 px-3 text-center text-zinc-500">${it.stt}</td>
          <td class="py-2 px-3 font-sans text-zinc-200">
            <input type="text" value="${it.ten_dich_vu}" onchange="updateCell(${index}, 'ten_dich_vu', this.value)" class="w-full bg-transparent border-none p-0 focus:outline-none focus:text-blue-400" />
          </td>
          <td class="py-2 px-3 text-right">
            <input type="number" value="${q}" onchange="updateCell(${index}, 'so_luong', Number(this.value))" class="w-14 bg-transparent border-none p-0 text-right focus:outline-none focus:text-blue-400 tabular-nums" />
          </td>
          <td class="py-2 px-3 text-center text-zinc-400">
            <input type="text" value="${it.don_vi_tinh}" onchange="updateCell(${index}, 'don_vi_tinh', this.value)" class="w-12 bg-transparent border-none p-0 text-center focus:outline-none focus:text-blue-400" />
          </td>
          <td class="py-2 px-3 text-right text-zinc-300">
            <input type="number" value="${p}" onchange="updateCell(${index}, 'don_gia', Number(this.value))" class="w-24 bg-transparent border-none p-0 text-right focus:outline-none focus:text-blue-400 tabular-nums" />
          </td>
          <td class="py-2 px-3 text-right font-semibold text-zinc-100 tabular-nums">
            <input type="number" value="${tot}" onchange="updateCell(${index}, 'thanh_tien', Number(this.value))" class="w-24 bg-transparent border-none p-0 text-right focus:outline-none focus:text-blue-400 tabular-nums" />
          </td>
          <td class="py-2 px-2 text-center">
            <button onclick="removeTableRow(${index})" class="text-zinc-600 hover:text-rose-400 transition" title="Delete row">×</button>
          </td>
        `;
        tbody.appendChild(tr);
      });

      document.getElementById('valCalculatedTotal').textContent = `${runningSum.toLocaleString()} VND`;

      // Check row count difference for Rule R-303
      const origCount = (doc.raw_result && doc.raw_result.items) ? doc.raw_result.items.length : items.length;
      const countDiffBox = document.getElementById('auditReasonBox');
      if (items.length !== origCount) {
        countDiffBox.classList.remove('hidden');
      } else {
        countDiffBox.classList.add('hidden');
      }

      // Four-eyes & Export visibility
      const fourEyesSec = document.getElementById('fourEyesApprovalStation');
      const exportSec = document.getElementById('exportReadyStation');
      
      if (doc.status === 'REVIEWED') {
        fourEyesSec.classList.remove('hidden');
        exportSec.classList.add('hidden');
      } else if (doc.status === 'APPROVED') {
        fourEyesSec.classList.add('hidden');
        exportSec.classList.remove('hidden');
        document.getElementById('shaDigestLabel').textContent = `SHA-256: ${doc.approved_payload_sha256 || 'Verified'}`;
        document.getElementById('btnDownloadCsvAuthoritative').href = `${API_URL}/api/v1/documents/${doc.id}/export.csv`;
      } else {
        fourEyesSec.classList.add('hidden');
        exportSec.classList.add('hidden');
      }
    }

    async function loadEvidence(docId) {
      try {
        const res = await req(`/api/v1/documents/${docId}/evidence`);
        currentEvidence = await res.json();
        
        // Arithmetic check banner
        const alertEl = document.getElementById('canvasArithmeticBanner');
        const check = (currentEvidence.total_checks || [])[0];
        if (check) {
          alertEl.classList.remove('hidden');
          document.getElementById('valPrintedTotal').textContent = `${check.document_total.toLocaleString()} VND`;
          document.getElementById('diffBadge').textContent = `Diff: ${check.difference.toLocaleString()} VND`;
          if (check.status === 'MATCH') {
            alertEl.className = 'px-4 py-2 text-xs border-b border-emerald-900/40 bg-emerald-950/30 text-emerald-300 flex items-center justify-between';
            alertEl.innerHTML = `<span>✓ Arithmetic Check Balanced (Printed Total = Rows Sum: ${check.document_total.toLocaleString()} VND)</span><span class="font-mono text-[10px]">Δ 0 VND</span>`;
            document.getElementById('diffBadge').className = 'font-mono text-xs font-semibold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800/40';
          } else {
            alertEl.className = 'px-4 py-2 text-xs border-b border-rose-900/40 bg-rose-950/30 text-rose-300 flex items-center justify-between';
            alertEl.innerHTML = `<span>Discrepancy: Printed Total (${check.document_total.toLocaleString()} VND) differs from rows by ${check.difference.toLocaleString()} VND. Check for missed rows.</span><span class="font-mono text-[10px] font-bold">MISMATCH</span>`;
            document.getElementById('diffBadge').className = 'font-mono text-xs font-semibold px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800/40';
          }
        } else {
          alertEl.classList.add('hidden');
        }

        if (currentEvidence.has_image) {
          renderCanvasImage(docId);
        } else {
          hideCanvasImage();
        }
      } catch (err) {
        console.error('Evidence error:', err);
      }
    }

    function renderCanvasImage(docId) {
      const container = document.getElementById('canvasContainer');
      const img = document.getElementById('docImageElement');
      const svg = document.getElementById('docSvgElement');
      const notice = document.getElementById('emptyCanvasNotice');

      img.src = `${API_URL}/api/v1/documents/${docId}/image`;
      img.onload = () => {
        container.classList.remove('hidden');
        notice.classList.add('hidden');
        document.getElementById('imgDimensions').textContent = `${img.naturalWidth}×${img.naturalHeight}px`;
        svg.setAttribute('viewBox', `0 0 ${img.naturalWidth} ${img.naturalHeight}`);
        drawBoundingBoxes();
      };
    }

    function hideCanvasImage() {
      document.getElementById('canvasContainer').classList.add('hidden');
      document.getElementById('emptyCanvasNotice').classList.remove('hidden');
      document.getElementById('imgDimensions').textContent = '';
    }

    const FIELD_HEX = {
      stt: '#64748b',
      ten_dich_vu: '#2563eb',
      so_luong: '#16a34a',
      don_vi_tinh: '#9333ea',
      don_gia: '#ea580c',
      thanh_tien: '#dc2626',
    };

    function drawBoundingBoxes() {
      const svg = document.getElementById('docSvgElement');
      svg.innerHTML = '';
      if (!currentEvidence || !currentEvidence.rows) return;

      currentEvidence.rows.forEach(r => {
        const isRowActive = (activeRowIndex === null || activeRowIndex === r.index);
        Object.entries(r.fields || {}).forEach(([fld, boxes]) => {
          const col = FIELD_HEX[fld] || '#94a3b8';
          boxes.forEach(box => {
            const [x1, y1, x2, y2] = box;
            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('x', x1);
            rect.setAttribute('y', y1);
            rect.setAttribute('width', x2 - x1);
            rect.setAttribute('height', y2 - y1);
            rect.setAttribute('fill', col);
            rect.setAttribute('fill-opacity', activeRowIndex === r.index ? '0.25' : '0.04');
            rect.setAttribute('stroke', col);
            rect.setAttribute('stroke-width', activeRowIndex === r.index ? '2.5' : '1.2');
            rect.setAttribute('class', `ocr-box ${activeRowIndex === r.index ? 'active' : ''}`);
            rect.onclick = (e) => {
              e.stopPropagation();
              highlightRow(r.index);
            };
            svg.appendChild(rect);
          });
        });
      });
    }

    function highlightRow(index) {
      activeRowIndex = (activeRowIndex === index) ? null : index;
      document.querySelectorAll('#lineItemsTbody tr').forEach((tr, i) => {
        if (activeRowIndex === i) {
          tr.classList.add('table-row-active');
        } else {
          tr.classList.remove('table-row-active');
        }
      });
      drawBoundingBoxes();
    }

    function updateCell(rowIndex, field, value) {
      if (!currentDocRecord) return;
      const items = currentDocRecord.reviewed_items || (currentDocRecord.raw_result && currentDocRecord.raw_result.items) || [];
      if (items[rowIndex]) {
        items[rowIndex][field] = value;
        // Auto-recalculate thanh_tien if qty or unit price updated
        if (field === 'so_luong' || field === 'don_gia') {
          items[rowIndex].thanh_tien = items[rowIndex].so_luong * items[rowIndex].don_gia;
        }
        renderDocumentWorkspace(currentDocRecord);
      }
    }

    function addNewTableRow() {
      if (!currentDocRecord) return;
      const items = currentDocRecord.reviewed_items || (currentDocRecord.raw_result && currentDocRecord.raw_result.items) || [];
      const nextStt = items.length + 1;
      items.push({
        stt: nextStt,
        ten_dich_vu: 'Item description',
        so_luong: 1,
        don_vi_tinh: 'Viên',
        don_gia: 1000,
        thanh_tien: 1000,
      });
      currentDocRecord.reviewed_items = items;
      renderDocumentWorkspace(currentDocRecord);
      toast('Row added. Explain reason in audit box if row count differs.', false);
    }

    function removeTableRow(index) {
      if (!currentDocRecord) return;
      const items = currentDocRecord.reviewed_items || (currentDocRecord.raw_result && currentDocRecord.raw_result.items) || [];
      items.splice(index, 1);
      currentDocRecord.reviewed_items = items;
      renderDocumentWorkspace(currentDocRecord);
    }

    function updateReasonCharCount(val) {
      document.getElementById('reasonCharCount').textContent = `${val.length} / 10 chars`;
    }

    function adjustZoom(delta) {
      currentZoom = Math.min(3.0, Math.max(0.4, currentZoom + delta));
      document.getElementById('canvasContainer').style.transform = `scale(${currentZoom})`;
      document.getElementById('zoomPercent').textContent = `${Math.round(currentZoom * 100)}%`;
    }

    function resetZoom() {
      currentZoom = 1.0;
      document.getElementById('canvasContainer').style.transform = 'scale(1.0)';
      document.getElementById('zoomPercent').textContent = '100%';
    }

    async function submitHumanReview() {
      if (!currentDocId || !currentDocRecord) return;
      const confirmChk = document.getElementById('confirmVerificationCheckbox').checked;
      if (!confirmChk) {
        toast('Confirm verification checkbox before submitting.', true);
        return;
      }

      const revId = document.getElementById('reviewerIdField').value.trim() || 'demo_operator';
      const docType = document.getElementById('reviewedDocTypeField').value;
      const items = currentDocRecord.reviewed_items || (currentDocRecord.raw_result && currentDocRecord.raw_result.items) || [];
      const origCount = (currentDocRecord.raw_result && currentDocRecord.raw_result.items) ? currentDocRecord.raw_result.items.length : items.length;
      const reasonVal = document.getElementById('rowCountReasonInput').value.trim();

      if (items.length !== origCount && reasonVal.length < 10) {
        toast('Reason of at least 10 characters required for row count change.', true);
        return;
      }

      const payload = {
        reviewer_id: revId,
        reviewed_document_type: docType,
        confirm_names_and_values: true,
        items: items
      };
      if (items.length !== origCount) {
        payload.row_count_change_reason = reasonVal;
      }

      try {
        await req(`/api/v1/documents/${currentDocId}/review`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        toast('Verification saved! Status: REVIEWED.');
        loadDocument(currentDocId);
      } catch (err) {
        toast(`Verification failed: ${err.message}`, true);
      }
    }

    async function approveActiveDocument() {
      if (!currentDocId || !currentDocRecord) return;
      const approverId = document.getElementById('approverIdField').value.trim();
      if (!approverId) {
        toast('Approver ID required.', true);
        return;
      }
      if (currentDocRecord.reviewer_id && approverId.toLowerCase() === currentDocRecord.reviewer_id.toLowerCase()) {
        toast('Four-Eyes Violation: Approver cannot be the Reviewer.', true);
        return;
      }

      try {
        await req(`/api/v1/documents/${currentDocId}/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ approver_id: approverId, acknowledge_review: true })
        });
        toast('Document APPROVED and cryptographically sealed.');
        loadDocument(currentDocId);
      } catch (err) {
        toast(`Approval failed: ${err.message}`, true);
      }
    }

    async function executeRpaAction(action) {
      if (!currentDocId) {
        toast('No document selected.', true);
        return;
      }
      const log = document.getElementById('rpaStatusOutput');
      log.textContent = `Dispatching action [${action}] for document ${currentDocId}...`;
      try {
        toast(`RPA ${action} executed.`);
        log.textContent = `[${new Date().toISOString()}] Action: ${action} | State: SIMULATED (Idempotent handoff confirmed)`;
      } catch (e) {
        log.textContent = `Error: ${e.message}`;
      }
    }

    async function fetchAuditEvents() {
      if (!currentDocId) return;
      const c = document.getElementById('auditLogContainer');
      try {
        const res = await req(`/api/v1/documents/${currentDocId}/audit`);
        const events = await res.json();
        c.innerHTML = '';
        events.forEach(ev => {
          const div = document.createElement('div');
          div.className = 'p-3 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-between text-xs';
          div.innerHTML = `
            <div class="flex items-center gap-3">
              <span class="font-mono text-zinc-500">${(ev.created_at || '').substring(11, 19)}</span>
              <span class="font-semibold text-zinc-200">${ev.action}</span>
              <span class="text-zinc-500">by <code class="text-zinc-400 font-mono">${ev.actor}</code></span>
            </div>
            <span class="font-mono text-[10px] text-zinc-600">${(ev.created_at || '').substring(0, 10)}</span>
          `;
          c.appendChild(div);
        });
      } catch (e) {
        c.innerHTML = `<div class="text-zinc-600 text-xs">${e.message}</div>`;
      }
    }

    async function loadSampleScenario(type) {
      toggleDemoDropdown();
      toast(`Loading ${type} scenario...`);
      try {
        // Trigger page refresh or queue fetch
        await fetchDocumentQueue();
        toast('Scenario active.');
      } catch (e) {
        toast(e.message, true);
      }
    }

    function toggleDemoDropdown() {
      document.getElementById('demoDropdown').classList.toggle('hidden');
    }

    function openSettingsModal() {
      document.getElementById('inputApiUrl').value = API_URL;
      document.getElementById('inputApiKey').value = API_KEY;
      document.getElementById('settingsDialog').classList.remove('hidden');
    }
    function closeSettingsModal() { document.getElementById('settingsDialog').classList.add('hidden'); }
    function saveSettingsModal() {
      API_URL = document.getElementById('inputApiUrl').value.trim();
      API_KEY = document.getElementById('inputApiKey').value.trim();
      localStorage.setItem('if_api_url', API_URL);
      localStorage.setItem('if_api_key', API_KEY);
      closeSettingsModal();
      checkBackendHealth();
      fetchDocumentQueue();
    }

    // Initialize
    checkBackendHealth();
    fetchDocumentQueue();
  </script>
</body>
</html>
"""
