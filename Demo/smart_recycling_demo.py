import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
import json
import random

app = FastAPI(title="Smart Recycling Demo")

# --- MOCK DATA GENERATOR ---
WASTE_TYPES = [
    {"class": "Plastic Bottle", "subType": "PET (Nhựa)", "grade": "A", "danger": False, "points": 50},
    {"class": "Aluminum Can", "subType": "Nhôm", "grade": "A", "danger": False, "points": 60},
    {"class": "Cardboard Box", "subType": "Giấy carton", "grade": "B", "danger": False, "points": 15},
    {"class": "Battery", "subType": "Nguy hại (Pin)", "grade": "D", "danger": True, "points": 0},
    {"class": "Chemical Bottle", "subType": "Hóa chất CN", "grade": "D", "danger": True, "points": 0},
    {"class": "Glass Bottle", "subType": "Thủy tinh", "grade": "A", "danger": False, "points": 40},
]

# --- HTML TEMPLATE WITH PREMIUM UI ---
html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Recycling EcoSystem</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
        body { font-family: 'Outfit', sans-serif; background: #0b1120; color: #f8fafc; margin:0; padding:0; height: 100vh; overflow: hidden; }
        
        /* Premium Background Gradient */
        .bg-animated {
            position: fixed;
            top: -50%; left: -50%; width: 200%; height: 200%;
            background: radial-gradient(circle at 50% 50%, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 1) 40%);
            animation: rotateBG 20s linear infinite;
            z-index: -1;
        }
        @keyframes rotateBG { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* Glassmorphism */
        .glass { background: rgba(30, 41, 59, 0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 1rem; }
        .glass-panel { background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(14, 165, 233, 0.2); border-radius: 1rem; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5); }
        
        /* Gradients & Glows */
        .text-gradient { background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .glow-box { box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #475569; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #64748b; }

        .slide-in { animation: slideIn 0.3s ease-out forwards; opacity: 0; transform: translateY(10px); }
        @keyframes slideIn { to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="flex flex-col h-screen">
    <div class="bg-animated"></div>

    <!-- HEADER -->
    <header class="glass mx-4 mt-4 mb-2 p-4 flex justify-between items-center shadow-lg z-10 hover:border-sky-500/30 transition-all">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-sky-500/20 flex items-center justify-center glow-box">
                <i class="fa-solid fa-leaf text-sky-400 text-xl"></i>
            </div>
            <div>
                <h1 class="text-2xl font-bold text-gradient leading-tight">EcoSmart Architecture</h1>
                <p class="text-xs text-slate-400">YOLOv8 + Spring Boot + n8n + AI Agent</p>
            </div>
        </div>
        <div class="flex gap-4 items-center">
            <div class="text-right">
                <p class="text-xs text-slate-400">Total Points Awarded</p>
                <div class="text-emerald-400 font-bold text-xl"><i class="fa-solid fa-star text-yellow-400 text-sm"></i> <span id="totalPoints">2,450</span> pts</div>
            </div>
            <div class="w-px h-8 bg-slate-700 mx-2"></div>
            <div class="flex items-center gap-2 text-sm font-medium">
                <span class="relative flex h-3 w-3">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
                <span class="text-emerald-400">System Online</span>
            </div>
        </div>
    </header>

    <!-- MAIN GRID -->
    <main class="flex-1 grid grid-cols-12 gap-4 p-4 overflow-hidden z-10">
        
        <!-- LEFT COLUMN: AI Detection Flow -->
        <div class="col-span-4 flex flex-col gap-4 overflow-hidden">
            <!-- Camera Simulation (YOLO) -->
            <div class="glass-panel p-4 flex flex-col">
                <h2 class="text-sm font-bold text-sky-400 mb-3 uppercase tracking-wider flex items-center"><i class="fa-solid fa-camera mr-2"></i> Edge Layer: Live Camera</h2>
                <div class="relative w-full aspect-video bg-black rounded-lg overflow-hidden border border-slate-700">
                    <img src="https://images.unsplash.com/photo-1611284446314-60a58ac0deb9?q=80&w=1470&auto=format&fit=crop" class="w-full h-full object-cover opacity-30">
                    <div class="absolute inset-0 bg-blue-500/10 animate-pulse"></div>
                    <div id="scannerLine" class="absolute top-0 left-0 w-full h-[2px] bg-sky-400 shadow-[0_0_8px_#38bdf8] opacity-80" style="animation: scan 2s linear infinite alternate;"></div>
                    
                    <!-- Bounding Box -->
                    <div id="bbox" class="absolute hidden border-2 border-emerald-400 bg-emerald-400/20 rounded z-10 transition-all duration-300">
                        <div id="bboxLabel" class="absolute -top-6 left-[-2px] bg-emerald-400 text-black text-[10px] font-bold px-1 whitespace-nowrap">Detection 99%</div>
                    </div>
                </div>
                
                <!-- FastAPI Results Box -->
                <h2 class="text-sm font-bold text-purple-400 mt-4 mb-2 uppercase tracking-wider flex items-center"><i class="fa-solid fa-microchip mr-2"></i> Inference Services Result</h2>
                <div id="detectionDetails" class="bg-slate-900/80 rounded p-3 text-xs font-mono space-y-1 min-h-[90px] border border-slate-700">
                    <p class="text-slate-500 italic">Waiting... Use the triggers in the middle panel.</p>
                </div>
            </div>

            <!-- Bins Status -->
            <div class="glass flex-1 p-4 flex flex-col overflow-hidden">
                <h2 class="text-sm font-bold text-slate-300 mb-3 uppercase tracking-wider flex items-center"><i class="fa-solid fa-trash-can mr-2"></i> Bin Status (Spring Boot)</h2>
                <div class="space-y-3 overflow-y-auto pr-1">
                    <div class="p-2 bg-slate-800/50 rounded border border-slate-700">
                        <div class="flex justify-between text-xs mb-1"><span>Bin #P-101 (Nhựa)</span><span id="pBinText" class="text-emerald-400">45%</span></div>
                        <div class="h-2 w-full bg-slate-900 rounded-full overflow-hidden"><div id="pBinBar" class="h-full bg-emerald-500 w-[45%] transition-all duration-500"></div></div>
                    </div>
                    <div class="p-2 bg-slate-800/50 rounded border border-slate-700">
                        <div class="flex justify-between text-xs mb-1"><span>Bin #M-202 (Kim loại)</span><span class="text-blue-400">20%</span></div>
                        <div class="h-2 w-full bg-slate-900 rounded-full overflow-hidden"><div class="h-full bg-blue-500 w-[20%]"></div></div>
                    </div>
                    <div class="p-2 bg-rose-900/30 rounded border border-rose-500/30">
                        <div class="flex justify-between text-xs mb-1"><span>Bin #H-999 (Nguy hại)</span><span id="hBinText" class="text-rose-400 font-bold">85%</span></div>
                        <div class="h-2 w-full bg-slate-900 rounded-full overflow-hidden"><div id="hBinBar" class="h-full bg-rose-500 w-[85%] transition-all duration-500 shadow-[0_0_10px_#f43f5e]"></div></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- MIDDLE COLUMN: n8n Automation Workflows -->
        <div class="col-span-4 flex flex-col gap-4 overflow-hidden">
            <div class="glass-panel flex-1 p-4 flex flex-col h-full border-indigo-500/30">
                <div class="flex justify-between items-center mb-4">
                    <h2 class="text-sm font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                        <i class="fa-solid fa-gears mr-2"></i> n8n Automation Engine
                    </h2>
                    <span class="text-[10px] bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded">Webhook Listening</span>
                </div>
                
                <div id="n8nLogs" class="flex-1 overflow-y-auto space-y-3 pr-2 scroll-smooth">
                    <div class="text-center text-xs text-slate-500 mt-10" id="n8nEmpty">No active automations. (Mock logs will appear here)</div>
                </div>

                <div class="mt-4 pt-3 border-t border-slate-700 flex justify-between gap-2">
                    <button onclick="triggerSim('normal')" class="flex-1 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/50 text-emerald-400 text-xs py-2 rounded transition font-bold">Simulate Recyclable Event</button>
                    <button onclick="triggerSim('hazard')" class="flex-1 bg-rose-600/20 hover:bg-rose-600/40 border border-rose-500/50 text-rose-400 text-xs py-2 rounded transition font-bold">Trigger Hazmat Workflow</button>
                </div>
            </div>
        </div>

        <!-- RIGHT COLUMN: RAG Agent Interface -->
        <div class="col-span-4 flex flex-col gap-4 overflow-hidden">
            <div class="glass-panel flex-1 p-0 flex flex-col h-full border-fuchsia-500/30">
                <div class="p-4 border-b border-white/10 bg-black/20 flex items-center justify-between">
                    <div>
                        <h2 class="text-sm font-bold text-fuchsia-400 uppercase tracking-wider flex items-center"><i class="fa-solid fa-brain mr-2"></i> RAG AI Chat Agent</h2>
                        <p class="text-[10px] text-slate-400 mt-1">ChromaDB + GPT-4o (Luật Tái chế VN)</p>
                    </div>
                </div>
                
                <div id="chatBox" class="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
                    <div class="flex gap-3">
                        <div class="w-8 h-8 rounded-full bg-fuchsia-500/20 flex-shrink-0 flex items-center justify-center border border-fuchsia-500/50"><i class="fa-solid fa-robot text-fuchsia-400 text-xs"></i></div>
                        <div class="bg-slate-800/80 rounded-2xl rounded-tl-sm px-4 py-2 border border-slate-700 text-slate-300">
                            Xin chào! Tôi lấy dữ liệu từ ChromaDB (Nghị định 08/2022/NĐ-CP). Bạn cần hỏi gì về phân loại rác?
                        </div>
                    </div>
                </div>

                <div class="p-3 border-t border-white/10 bg-black/30">
                    <form id="chatForm" class="relative">
                        <input type="text" id="chatInput" autocomplete="off" placeholder="Hải: Pin cũ vứt đâu?..." 
                            class="w-full bg-slate-900 border border-slate-700 rounded-full pl-4 pr-10 py-2 text-sm text-white focus:outline-none focus:border-fuchsia-500 focus:ring-1 focus:ring-fuchsia-500 transition">
                        <button type="submit" class="absolute right-1 top-1 bottom-1 w-8 rounded-full bg-fuchsia-600 hover:bg-fuchsia-500 text-white flex items-center justify-center transition">
                            <i class="fa-solid fa-paper-plane text-xs"></i>
                        </button>
                    </form>
                </div>
            </div>
        </div>

    </main>

    <style> @keyframes scan { 0% { top: 0%; } 100% { top: 100%; } } </style>

    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        let points = 2450; let pFill = 45; let hFill = 85;

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === "detection") handleDetection(data.payload);
            else if (data.type === "n8n_log") addN8nLog(data.payload);
            else if (data.type === "chat_reply") addChatMessage('ai', data.payload.html);
        };

        function triggerSim(type) { ws.send(JSON.stringify({ action: "simulate", type: type })); }

        function handleDetection(item) {
            const bbox = document.getElementById("bbox");
            bbox.style.width = (30+Math.random()*20) + "%"; bbox.style.height = (40+Math.random()*30) + "%";
            bbox.style.top = (20+Math.random()*30) + "%"; bbox.style.left = (20+Math.random()*40) + "%";
            
            const color = item.danger ? "#f43f5e" : "#34d399";
            bbox.style.borderColor = color; bbox.style.backgroundColor = color + "33";
            const lbl = document.getElementById("bboxLabel");
            lbl.style.backgroundColor = color; lbl.textContent = `${item.class} (0.95)`;
            bbox.classList.remove("hidden");
            
            const html = `
                <div class="text-[10px] text-slate-500 mb-1">[${new Date().toLocaleTimeString()}] Async YOLO Detect</div>
                <div class="grid grid-cols-2 gap-x-2 gap-y-1">
                    <div><span class="text-slate-500">Class:</span> <span class="text-sky-300">${item.class}</span></div>
                    <div><span class="text-slate-500">ResNet:</span> <span class="text-fuchsia-300">${item.subType}</span></div>
                    <div><span class="text-slate-500">Grade:</span> <span class="${item.danger ? 'text-rose-400 font-bold' : 'text-emerald-400'}">${item.grade}</span></div>
                    <div><span class="text-slate-500">Points:</span> <span class="text-yellow-400">+${item.points}</span></div>
                </div>`;
            document.getElementById("detectionDetails").innerHTML = html;

            points += item.points; document.getElementById("totalPoints").innerText = points.toLocaleString();
            if (item.danger) {
                hFill = Math.min(100, hFill + 15);
                document.getElementById("hBinText").innerText = hFill + "%"; document.getElementById("hBinBar").style.width = hFill + "%";
            } else {
                pFill = Math.min(100, pFill + 5);
                document.getElementById("pBinText").innerText = pFill + "%"; document.getElementById("pBinBar").style.width = pFill + "%";
            }
            setTimeout(() => bbox.classList.add("hidden"), 2500);
        }

        function addN8nLog(log) {
            document.getElementById("n8nEmpty")?.remove();
            const el = document.createElement("div");
            const isDanger = log.action.includes('Telegram');
            el.className = `slide-in p-3 rounded-lg border text-xs ${isDanger ? 'border-rose-500 bg-rose-500/10' : 'border-indigo-500/50 bg-indigo-500/10'}`;
            el.innerHTML = `
                <div class="flex justify-between mb-1 font-bold text-${isDanger ? 'rose' : 'indigo'}-400">
                    <span>${log.action}</span> <span class="text-slate-400 text-[10px]">%time%</span>
                </div>
                <div class="text-slate-300 font-mono text-[10px] space-y-1 mt-2">
                    ${log.details.map(d => `<div class="truncate">✓ ${d}</div>`).join('')}
                </div>`.replace('%time%', new Date().toLocaleTimeString());
            document.getElementById("n8nLogs").prepend(el);
        }

        document.getElementById("chatForm").addEventListener("submit", function(e) {
            e.preventDefault();
            const msg = document.getElementById("chatInput").value.trim();
            if (!msg) return;
            addChatMessage('user', msg); ws.send(JSON.stringify({ action: "chat", query: msg }));
            document.getElementById("chatInput").value = "";
            addChatMessage('ai', '<span class="animate-pulse">Đang tìm trong Vector DB...</span>', 'loadingAi');
        });

        function addChatMessage(role, html, id=null) {
            if (role === 'ai' && document.getElementById('loadingAi')) document.getElementById('loadingAi').parentElement.parentElement.remove();
            const el = document.createElement("div"); el.className = `flex gap-3 slide-in ${role==='user'?'flex-row-reverse':''}`;
            el.innerHTML = role === 'user' 
                ? `<div class="w-8 h-8 rounded-full bg-slate-700 flex-shrink-0 border border-slate-600 flex items-center justify-center"><i class="fa-solid fa-user text-xs"></i></div><div class="bg-sky-600/80 rounded-2xl p-2 px-4 border border-sky-500">${html}</div>`
                : `<div class="w-8 h-8 rounded-full bg-fuchsia-500/20 flex-shrink-0 border border-fuchsia-500/50 flex items-center justify-center"><i class="fa-solid fa-robot text-fuchsia-400 text-xs"></i></div><div class="bg-slate-800/80 rounded-2xl p-2 px-4 border border-slate-700">${html}</div>`;
            if (id) el.id = id;
            document.getElementById("chatBox").appendChild(el);
            document.getElementById("chatBox").scrollTop = 9999;
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            req = json.loads(data)
            
            if req.get('action') == 'simulate':
                item = random.choice([w for w in WASTE_TYPES if w['danger'] == (req.get('type') == 'hazard')])
                await websocket.send_json({"type": "detection", "payload": item})
                
                await asyncio.sleep(0.8)
                await websocket.send_json({"type": "n8n_log", "payload": {
                    "action": "Kafka Event -> SpringBoot",
                    "details": ["Persisted WasteEvent(event_id, class, grade)", "Points awarded to user", "Updated Bin capacity"]
                }})

                if item['danger']:
                    await asyncio.sleep(1)
                    await websocket.send_json({"type": "n8n_log", "payload": {
                        "action": "Telegram Alert: HAZMAT DETECTED",
                        "details": ["Webhook -> n8n", "AI Agent (GPT-4) parsed hazmat risk", "🚨 Pushed alert to Environment Group!"]
                    }})

            elif req.get('action') == 'chat':
                q = req.get('query').lower()
                await asyncio.sleep(1.5)
                html = "Theo <b>TT 36/2015</b>, pin và ắc quy cũ là rác thải nguy hại. Vui lòng cho vào thùng rác chuyên dụng (mũi neo đen) nhé!<br><span class='text-[10px] text-fuchsia-400 mt-2 block'>📚 Source: TCVN 6706:2009 (Sim: 0.94)</span>" if "pin" in q or "thuỷ" in q else "Đây là Rác Tái Chế. Nhớ làm sạch trước khi cho vào thùng (Xanh) để nhận điểm thưởng bạn nhé!<br><span class='text-[10px] text-fuchsia-400 mt-2 block'>📚 Source: HD PL RT SH (Sim: 0.88)</span>"
                await websocket.send_json({"type": "chat_reply", "payload": {"html": html}})

    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
