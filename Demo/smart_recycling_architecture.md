# 🏗️ Kiến Trúc Hệ Thống Quản Lý Tái Chế Rác Thải Thông Minh

## Tổng Quan Hệ Thống

Hệ thống được thiết kế theo kiến trúc **Microservices + Event-Driven**, tích hợp AI/ML Pipeline, RAG Agent, và automation workflow để tạo ra một hệ sinh thái quản lý tái chế khép kín từ nhận diện rác → phân loại → thưởng điểm → báo cáo.

---

## 1. Sơ Đồ Kiến Trúc Tổng Thể

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           SMART RECYCLING ECOSYSTEM                                  │
│                                                                                       │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │                          EDGE LAYER (IoT)                                     │   │
│  │                                                                               │   │
│  │   📷 Smart Bin Camera  ──►  Raspberry Pi / Edge Device  ──►  MQTT Broker     │   │
│  │   📡 Ultrasonic Sensor (fill level)                          (Mosquitto)     │   │
│  │   🌡️ Temperature Sensor                                                       │   │
│  └──────────────────────────────────────────────┬────────────────────────────────┘  │
│                                                  │ MQTT / HTTP                       │
│  ┌───────────────────────────────────────────────▼────────────────────────────────┐ │
│  │                        AI INFERENCE LAYER (FastAPI)                             │ │
│  │                                                                                 │ │
│  │  ┌─────────────────────┐    ┌────────────────────────┐    ┌──────────────────┐ │ │
│  │  │  /detect  (YOLOv8)  │    │ /classify (ResNet-50)  │    │  /chat (RAG      │ │ │
│  │  │  - Object Detection │    │ - Plastic sub-type     │    │  Agent / LLM)    │ │ │
│  │  │  - Bounding Boxes   │    │ - Confidence Score     │    │  - ChromaDB      │ │ │
│  │  │  - Class Labels     │    │ - Material Type        │    │  - LangChain     │ │ │
│  │  └─────────────────────┘    └────────────────────────┘    └──────────────────┘ │ │
│  └──────────────────────────────────────┬──────────────────────────────────────────┘ │
│                                         │ REST API                                   │
│  ┌──────────────────────────────────────▼──────────────────────────────────────────┐ │
│  │                    CORE BACKEND LAYER (Spring Boot)                              │ │
│  │                                                                                 │ │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐ │ │
│  │  │ Waste        │  │ User &        │  │ Point &      │  │ Report &           │ │ │
│  │  │ Detection    │  │ Auth Service  │  │ Reward       │  │ Analytics          │ │ │
│  │  │ Service      │  │ (JWT/OAuth2)  │  │ Service      │  │ Service            │ │ │
│  │  └──────────────┘  └───────────────┘  └──────────────┘  └────────────────────┘ │ │
│  │  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  ┌────────────────────┐ │ │
│  │  │ Bin          │  │ Notification  │  │ Vehicle      │  │ AI Proxy           │ │ │
│  │  │ Management   │  │ Service       │  │ Routing      │  │ Service            │ │ │
│  │  │ Service      │  │               │  │ Service      │  │                    │ │ │
│  │  └──────────────┘  └───────────────┘  └──────────────┘  └────────────────────┘ │ │
│  │                                                                                 │ │
│  │              Message Queue: Apache Kafka / RabbitMQ                            │ │
│  └──────────────────────────────────────┬──────────────────────────────────────────┘ │
│                          ┌──────────────┼──────────────┐                             │
│                          │              │              │                             │
│  ┌───────────────────────▼──┐  ┌────────▼────────┐  ┌─▼──────────────────────────┐ │
│  │   DATA LAYER              │  │  AUTOMATION     │  │   CLIENT LAYER              │ │
│  │                           │  │  LAYER (n8n)    │  │                             │ │
│  │  ┌─────────────────────┐  │  │                 │  │  ┌──────────────────────┐  │ │
│  │  │  PostgreSQL          │  │  │ Workflow 1:     │  │  │  Mobile App          │  │ │
│  │  │  - Users             │  │  │ Bin Full Alert  │  │  │  (React Native)      │  │ │
│  │  │  - WasteEvents       │  │  │                 │  │  │  - Scan QR           │  │ │
│  │  │  - Points            │  │  │ Workflow 2:     │  │  │  - View Points       │  │ │
│  │  │  - Bins              │  │  │ Vehicle Dispatch│  │  │  - Chat with AI      │  │ │
│  │  │  - Reports           │  │  │                 │  │  └──────────────────────┘  │ │
│  │  │  - Classifications   │  │  │ Workflow 3:     │  │  ┌──────────────────────┐  │ │
│  │  └─────────────────────┘  │  │ Monthly Reports │  │  │  Admin Dashboard     │  │ │
│  │  ┌─────────────────────┐  │  │                 │  │  │  (React/Angular)     │  │ │
│  │  │  ChromaDB (Vector)  │  │  │ Workflow 4:     │  │  │  - Analytics         │  │ │
│  │  │  - Recycling Regs   │  │  │ User Rewards    │  │  │  - Map View          │  │ │
│  │  │  - Policy Docs      │  │  │ Notification    │  │  │  - Reports           │  │ │
│  │  │  - FAQ Embeddings   │  │  │                 │  │  └──────────────────────┘  │ │
│  │  └─────────────────────┘  │  └─────────────────┘  └────────────────────────────┘ │
│  │  ┌─────────────────────┐  │                                                      │
│  │  │  Redis (Cache)      │  │                                                      │
│  │  │  - Session          │  │                                                      │
│  │  │  - Rate Limiting    │  │                                                      │
│  │  └─────────────────────┘  │                                                      │
│  └───────────────────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Sơ Đồ Luồng Dữ Liệu Chi Tiết (End-to-End)

### Giai Đoạn 1: Camera → AI Detection

```
[📷 Smart Bin Camera]
       │
       │ Chụp ảnh khi cảm biến PIR phát hiện chuyển động
       ▼
[Edge Device (Raspberry Pi)]
       │
       │ 1. Compress image (JPEG 80%)
       │ 2. Attach metadata: bin_id, timestamp, gps_location
       │ 3. POST /api/detect (multipart/form-data)
       ▼
[FastAPI - YOLO Service :8001]
       │
       │ 4. Load YOLOv8 model (cached in memory)
       │ 5. Inference → [{class: "plastic_bottle", confidence: 0.94,
       │                   bbox: [x,y,w,h]}, ...]
       │
       │ [Nếu class = plastic/*]
       │       └──► POST /api/classify (ResNet Service :8002)
       │              │
       │              │ 6. Crop ROI từ bounding box
       │              │ 7. ResNet inference → {sub_type: "PET", 
       │              │                        recycle_grade: "A",
       │              │                        confidence: 0.89}
       │              └──► Return classification result
       │
       │ 8. Aggregate results: detection + classification
       │ 9. Return JSON response
       ▼
[Spring Boot - AI Proxy Service]
       │
       │ 10. Validate & enrich response
       │ 11. Map waste_type → point_value (lookup table)
       │ 12. Publish event to Kafka: "waste.detected"
       ▼
```

### Giai Đoạn 2: Spring Boot Xử Lý Nghiệp Vụ

```
[Kafka Topic: waste.detected]
       │
       ├──► [Waste Detection Service]
       │         │
       │         │ 13. Persist WasteEvent to PostgreSQL:
       │         │     {event_id, bin_id, user_id, 
       │         │      waste_type, sub_type, recycle_grade,
       │         │      confidence, image_url, timestamp}
       │         │
       │         │ 14. Update Bin status:
       │         │     bins SET fill_level = fill_level + weight_estimate
       │         │                       WHERE bin_id = ?
       │         ▼
       │    [Bin Management Service]
       │         │
       │         │ 15. Check fill_level threshold (> 80%?)
       │         │         YES → Publish "bin.full" event to Kafka
       │         │         NO  → Continue
       │
       └──► [Point & Reward Service]
                 │
                 │ 16. Calculate points:
                 │     base_points = waste_type_config[waste_type]
                 │     multiplier = recycle_grade_multiplier[grade]
                 │     final_points = base_points × multiplier × confidence_factor
                 │
                 │ 17. Update user points in PostgreSQL:
                 │     user_points SET total = total + final_points,
                 │                     history = history + [new_record]
                 │
                 │ 18. Check achievement milestones
                 │     → Publish "points.awarded" event
                 ▼
```

### Giai Đoạn 3: n8n Automation Workflows

```
[Kafka → n8n Webhook Triggers]

┌─────────────────────────────────────────────────────────┐
│  WORKFLOW 1: Bin Full Alert                             │
│  Trigger: "bin.full" event                              │
│                                                         │
│  1. Receive bin_id, location, fill_level               │
│  2. Query PostgreSQL → nearest available vehicles       │
│  3. Calculate optimal route (Google Maps API)           │
│  4. Send push notification to Driver App               │
│  5. Send email alert to Operations Manager             │
│  6. Update bin status: "scheduled_for_pickup"          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  WORKFLOW 2: Points Awarded Notification                │
│  Trigger: "points.awarded" event                        │
│                                                         │
│  1. Receive user_id, points_earned, total_points        │
│  2. Query user preferences (notification channel)       │
│  3. Format personalized message:                        │
│     "Bạn vừa nhận +50 điểm! Tổng: 1,250 điểm 🌟"      │
│  4. Send via: FCM (Mobile) / Email / SMS               │
│  5. Check if milestone reached → trigger badge award   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  WORKFLOW 3: Monthly Report Generation (Cron: 1st/month)│
│                                                         │
│  1. Query PostgreSQL aggregate stats:                   │
│     - Total waste collected by type                     │
│     - Top performing users/districts                    │
│     - Bin utilization rates                             │
│     - CO2 offset estimates                              │
│  2. Generate PDF report (Jasper/iText)                  │
│  3. Upload to S3/MinIO storage                          │
│  4. Email to all stakeholders                           │
│  5. Post summary to Slack/Teams channel                 │
└─────────────────────────────────────────────────────────┘
```

### Giai Đoạn 4: RAG Agent - Hỏi Đáp Quy Định

```
[User Mobile App]
       │
       │ User hỏi: "Hộp sữa có thể tái chế không?"
       ▼
[FastAPI - RAG Service :8003]
       │
       │ 1. Embed câu hỏi → vector (OpenAI/local embedding model)
       │
       │ 2. ChromaDB similarity search:
       │    → Retrieve top-5 relevant chunks từ:
       │       - Nghị định 08/2022/NĐ-CP về tái chế
       │       - TCVN về phân loại rác thải
       │       - Hướng dẫn của Bộ TN&MT
       │       - Internal recycling guidelines
       │
       │ 3. Build augmented prompt:
       │    SYSTEM: "Bạn là chuyên gia tái chế..."
       │    CONTEXT: [retrieved chunks]
       │    USER: [original question]
       │
       │ 4. LLM generates answer (GPT-4o / Gemini / local Ollama)
       │
       │ 5. Log conversation to PostgreSQL (chat_history table)
       │ 6. Return structured response:
       │    {answer, sources, confidence, related_questions}
       ▼
[User receives detailed, regulation-backed answer]
```

---

## 3. Database Schema (PostgreSQL)

```sql
-- Users & Authentication
CREATE TABLE users (
    user_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phone        VARCHAR(20) UNIQUE NOT NULL,
    email        VARCHAR(255),
    full_name    VARCHAR(255),
    qr_code      VARCHAR(100) UNIQUE,  -- for bin scanning
    total_points INTEGER DEFAULT 0,
    level        VARCHAR(20) DEFAULT 'BRONZE', -- BRONZE/SILVER/GOLD/PLATINUM
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Smart Bins
CREATE TABLE bins (
    bin_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location     VARCHAR(500),
    latitude     DECIMAL(10, 8),
    longitude    DECIMAL(11, 8),
    capacity_kg  DECIMAL(10,2),
    fill_level   DECIMAL(5,2) DEFAULT 0, -- percentage 0-100
    status       VARCHAR(50) DEFAULT 'ACTIVE', -- ACTIVE/FULL/MAINTENANCE
    waste_type   VARCHAR(50), -- GENERAL/PLASTIC/ORGANIC/PAPER/METAL
    last_emptied TIMESTAMP WITH TIME ZONE,
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Waste Detection Events
CREATE TABLE waste_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bin_id          UUID REFERENCES bins(bin_id),
    user_id         UUID REFERENCES users(user_id),
    image_url       VARCHAR(500),
    waste_type      VARCHAR(50),     -- plastic, paper, metal, organic
    sub_type        VARCHAR(100),    -- PET, HDPE, PVC (for plastics)
    recycle_grade   VARCHAR(5),      -- A, B, C, D
    yolo_confidence DECIMAL(4,3),
    resnet_confidence DECIMAL(4,3),
    weight_estimate DECIMAL(10,3),   -- kg (estimated from bounding box)
    points_awarded  INTEGER,
    detected_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed       BOOLEAN DEFAULT FALSE
);

-- Points Ledger
CREATE TABLE points_transactions (
    tx_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID REFERENCES users(user_id),
    event_id     UUID REFERENCES waste_events(event_id),
    tx_type      VARCHAR(50),  -- EARN / REDEEM / BONUS / EXPIRE
    points       INTEGER,
    balance      INTEGER,
    description  VARCHAR(255),
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vehicle Fleet
CREATE TABLE vehicles (
    vehicle_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plate_number VARCHAR(20) UNIQUE,
    driver_name  VARCHAR(255),
    driver_phone VARCHAR(20),
    capacity_kg  DECIMAL(10,2),
    status       VARCHAR(50), -- AVAILABLE/ON_ROUTE/MAINTENANCE
    current_lat  DECIMAL(10,8),
    current_lng  DECIMAL(11,8),
    updated_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Collection Routes
CREATE TABLE collection_routes (
    route_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id   UUID REFERENCES vehicles(vehicle_id),
    bin_ids      UUID[],  -- ordered array
    status       VARCHAR(50) DEFAULT 'PENDING',
    started_at   TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat History (for RAG)
CREATE TABLE chat_history (
    chat_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID REFERENCES users(user_id),
    question     TEXT,
    answer       TEXT,
    sources      JSONB,   -- retrieved document chunks
    feedback     INTEGER, -- 1 = helpful, -1 = not helpful
    created_at   TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_waste_events_user    ON waste_events(user_id, detected_at);
CREATE INDEX idx_waste_events_bin     ON waste_events(bin_id, detected_at);
CREATE INDEX idx_bins_status          ON bins(status, fill_level);
CREATE INDEX idx_points_tx_user       ON points_transactions(user_id, created_at);
```

---

## 4. API Contract (Spring Boot ↔ FastAPI)

### Spring Boot → FastAPI YOLO Service
```yaml
POST http://ai-service:8001/detect
Content-Type: multipart/form-data

Request:
  - image: <binary>
  - bin_id: "uuid"
  - timestamp: "ISO-8601"

Response 200:
  {
    "detections": [
      {
        "class": "plastic_bottle",
        "confidence": 0.94,
        "bbox": {"x": 120, "y": 80, "width": 200, "height": 350},
        "track_id": 1
      }
    ],
    "inference_time_ms": 45,
    "model_version": "yolov8n-waste-v2.1"
  }
```

### Spring Boot → FastAPI ResNet Service
```yaml
POST http://ai-service:8002/classify
Content-Type: multipart/form-data

Request:
  - image: <cropped ROI binary>
  - waste_class: "plastic_bottle"

Response 200:
  {
    "sub_type": "PET",
    "material_code": "1",
    "recycle_grade": "A",
    "recyclable": true,
    "confidence": 0.89,
    "processing_note": "Rinse before recycling",
    "point_multiplier": 1.5
  }
```

### Spring Boot → FastAPI RAG Service
```yaml
POST http://ai-service:8003/chat
Content-Type: application/json

Request:
  {
    "user_id": "uuid",
    "question": "Hộp sữa có thể tái chế không?",
    "conversation_id": "uuid",
    "language": "vi"
  }

Response 200:
  {
    "answer": "Hộp sữa giấy (Tetra Pak) thuộc loại rác CÓ THỂ tái chế...",
    "sources": [
      {
        "document": "Thông tư 02/2022/TT-BTNMT",
        "chunk": "Mục 3.2: Phân loại rác thải sinh hoạt...",
        "similarity": 0.92
      }
    ],
    "related_questions": [
      "Cách rửa hộp sữa trước khi tái chế?",
      "Điểm thu gom hộp sữa gần tôi ở đâu?"
    ],
    "confidence": 0.91
  }
```

---

## 5. Kafka Event Schema

```json
// Topic: waste.detected
{
  "eventId": "uuid",
  "eventType": "WASTE_DETECTED",
  "timestamp": "2024-01-15T10:30:00Z",
  "payload": {
    "binId": "uuid",
    "userId": "uuid",
    "detection": { "class": "plastic_bottle", "confidence": 0.94 },
    "classification": { "subType": "PET", "grade": "A", "recyclable": true },
    "pointsAwarded": 75,
    "imageUrl": "s3://bucket/event-uuid.jpg"
  }
}

// Topic: bin.status.changed  
{
  "eventId": "uuid",
  "eventType": "BIN_FULL",
  "timestamp": "2024-01-15T14:20:00Z",
  "payload": {
    "binId": "uuid",
    "location": "123 Nguyễn Huệ, Q1, HCM",
    "coordinates": {"lat": 10.7769, "lng": 106.7009},
    "fillLevel": 87.5,
    "wasteType": "PLASTIC",
    "lastEmptied": "2024-01-14T08:00:00Z"
  }
}

// Topic: points.awarded
{
  "eventId": "uuid",
  "eventType": "POINTS_AWARDED",
  "timestamp": "2024-01-15T10:30:05Z",
  "payload": {
    "userId": "uuid",
    "pointsEarned": 75,
    "totalPoints": 1250,
    "newLevel": "SILVER",
    "levelUp": true,
    "achievementUnlocked": "first_plastic_100"
  }
}
```

---

## 6. Point Calculation Engine

```
WASTE TYPE BASE POINTS:
┌──────────────────┬──────────────┬────────────────────────────────┐
│ Waste Type       │ Base Points  │ Notes                          │
├──────────────────┼──────────────┼────────────────────────────────┤
│ Plastic (PET/1)  │ 50 pts/item  │ Highest value recyclable       │
│ Plastic (HDPE/2) │ 45 pts/item  │                                │
│ Plastic (other)  │ 20 pts/item  │                                │
│ Aluminum can     │ 60 pts/item  │ Premium recyclable             │
│ Glass bottle     │ 40 pts/item  │                                │
│ Paper/Cardboard  │ 15 pts/item  │                                │
│ E-waste          │ 100 pts/item │ Special handling required      │
│ Organic          │ 10 pts/item  │ Composting eligible            │
└──────────────────┴──────────────┴────────────────────────────────┘

GRADE MULTIPLIERS:
  Grade A (confidence > 0.90): × 1.5
  Grade B (confidence 0.75-0.90): × 1.0
  Grade C (confidence 0.60-0.75): × 0.75
  Grade D (confidence < 0.60): × 0.5

FORMULA:
  final_points = base_points × grade_multiplier × streak_bonus
  streak_bonus = 1.0 + (min(consecutive_days, 30) × 0.01)
```

---

## 7. Deployment Architecture (Docker Compose / Kubernetes)

```yaml
# docker-compose.yml (Development)
version: '3.9'
services:

  # Core Backend
  spring-boot-app:
    build: ./backend
    ports: ["8080:8080"]
    environment:
      - DB_URL=jdbc:postgresql://postgres:5432/recycledb
      - KAFKA_BOOTSTRAP=kafka:9092
      - REDIS_HOST=redis
      - AI_SERVICE_URL=http://fastapi-ai:8001

  # AI Services
  fastapi-ai:
    build: ./ai-services
    ports: ["8001:8001", "8002:8002", "8003:8003"]
    volumes:
      - ./models:/app/models   # Pre-trained YOLO + ResNet weights
    deploy:
      resources:
        reservations:
          devices: [{capabilities: [gpu]}]  # GPU acceleration

  # Databases
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: recycledb
      POSTGRES_USER: recycle_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  chromadb:
    image: chromadb/chroma:latest
    ports: ["8000:8000"]
    volumes: ["chroma_data:/chroma/chroma"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  # Message Queue
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092

  # Automation
  n8n:
    image: n8nio/n8n:latest
    ports: ["5678:5678"]
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
    volumes: ["n8n_data:/home/node/.n8n"]

  # Monitoring
  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]

  prometheus:
    image: prom/prometheus:latest
    volumes: ["./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml"]
```

---

## 8. Security Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                            │
│                                                               │
│  Kong API Gateway (Rate Limiting, mTLS, JWT Validation)      │
│          ↓                                                    │
│  Spring Security (OAuth2 / Keycloak)                         │
│  - JWT Access Token (15 min expiry)                          │
│  - Refresh Token (7 days, stored in HttpOnly Cookie)         │
│  - Role-Based: USER / DRIVER / ADMIN / SUPER_ADMIN           │
│          ↓                                                    │
│  Service-to-Service (Internal):                              │
│  - mTLS between Spring Boot ↔ FastAPI                        │
│  - API Key authentication for edge devices                   │
│          ↓                                                    │
│  Data Security:                                              │
│  - Encryption at rest: PostgreSQL (pgcrypto)                 │
│  - Encryption in transit: TLS 1.3                            │
│  - Image data: Anonymized before storage (face blur)         │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Monitoring & Observability

| Layer       | Tool           | Metrics                                   |
|-------------|----------------|-------------------------------------------|
| Application | Micrometer + Prometheus | Request rate, error rate, latency   |
| AI Services | MLflow         | Model accuracy drift, inference time      |
| Database    | pgAdmin + Grafana | Query time, connection pool, disk usage|
| Kafka       | Kafka UI       | Consumer lag, throughput                  |
| n8n         | Built-in logs  | Workflow execution success/failure        |
| Edge Devices| Grafana        | Camera uptime, sensor readings            |

**Alerting Rules (PagerDuty):**
- AI Service latency > 2s → Alert DevOps
- Kafka consumer lag > 1000 messages → Scale consumers
- PostgreSQL disk > 85% → Alert DBA
- n8n workflow failure → Alert Operations team

---

## 10. Scalability Roadmap

```
Phase 1 (MVP - Month 1-3):
  - Single Docker Compose deployment
  - 10 smart bins, 1 city district
  - Basic YOLO detection + point system

Phase 2 (Scale - Month 4-6):
  - Migrate to Kubernetes (k8s)
  - Horizontal scaling: 3 FastAPI replicas with load balancer
  - Add: Real-time analytics dashboard
  - 100 bins, 5 districts

Phase 3 (City-wide - Month 7-12):
  - Multi-tenant architecture (per city/district)
  - Federated Learning: Improve AI models from field data
  - Integration: City ERP systems, Government APIs
  - 1000+ bins, full city coverage
```

---

## 11. Tóm Tắt Luồng Hoàn Chỉnh (Sequence)

```
Camera → Edge Pi → [HTTPS] → FastAPI YOLO → FastAPI ResNet
                                                    ↓
                               Spring Boot (AI Proxy Service)
                                        ↓ (validates, maps)
                               Kafka: "waste.detected"
                                   ↙           ↘
                  Waste Detection Svc      Point & Reward Svc
                  (save to PostgreSQL)     (calculate & credit)
                          ↓                       ↓
                  Bin Management Svc      Kafka: "points.awarded"
                  (update fill level)             ↓
                          ↓                   n8n Workflow 2
                  if fill > 80%:            (push notification
                  Kafka: "bin.full"          to user mobile)
                          ↓
                      n8n Workflow 1
                  (dispatch vehicle,
                   notify driver,
                   update route)
                          ↓
                  Collection completed
                          ↓
                     n8n Workflow 3 (Cron)
                  (aggregate monthly data
                   → generate PDF report
                   → email stakeholders)
```
