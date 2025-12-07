# PHÂN TÍCH HỆ THỐNG ỨNG DỤNG QUẢN LÝ RỦI RO THIÊN TAI

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Thông tin dự án
- **Tên dự án**: SVATTT (Hệ thống quản lý và cảnh báo rủi ro thiên tai)
- **Phiên bản**: 0.1.0
- **Giấy phép**: Apache License 2.0
- **Chủ sở hữu**: PKA-OpenLD

### 1.2 Mục đích
Ứng dụng web real-time để giám sát, dự báo và cảnh báo các rủi ro thiên tai (đặc biệt là lũ lụt và mất điện) thông qua:
- Hệ thống bản đồ tương tác
- Mạng lưới cảm biến IoT
- Cơ chế báo cáo của người dùng
- Tự động hóa tạo cảnh báo dựa trên quy tắc

### 1.3 Đối tượng sử dụng
- **Người dùng thông thường**: Xem bản đồ cảnh báo, báo cáo sự cố, xem thời tiết
- **Quản trị viên**: Quản lý cảm biến, tạo vùng cảnh báo, cấu hình quy tắc tự động

---

## 2. KIẾN TRÚC HỆ THỐNG

### 2.1 Stack công nghệ

#### Frontend
- **Framework**: Next.js 16.0.3 (React 19.2.0)
- **UI Framework**: TailwindCSS 4.x + PostCSS
- **Bản đồ**: VietMap GL JS 6.0.1
- **Biểu đồ luồng**: XYFlow/React 12.9.3
- **Icons**: FontAwesome 7.1.0
- **Ngôn ngữ**: TypeScript 5.x

#### Backend
- **Runtime**: Bun (JavaScript/TypeScript runtime)
- **API Framework**: Next.js App Router API Routes
- **Database**: MongoDB 7.0.0
- **WebSocket**: Native WebSocket (ws 8.18.3)
- **Real-time**: Custom WebSocket server với Bun

#### DevOps
- **Linting**: ESLint 9.x với Next.js config
- **Type Checking**: TypeScript
- **Package Manager**: Bun

### 2.2 Cấu trúc thư mục

```
app/
├── app/                          # Next.js App Router
│   ├── page.tsx                 # Trang chủ (bản đồ)
│   ├── admin/                   # Dashboard quản trị
│   │   └── page.tsx
│   ├── api/                     # REST API endpoints
│   │   ├── zones/               # Quản lý vùng cảnh báo
│   │   ├── sensors/             # Quản lý cảm biến
│   │   ├── sensor-data/         # Dữ liệu cảm biến
│   │   ├── sensor-rules/        # Quy tắc tự động
│   │   ├── predictions/         # Dự báo
│   │   ├── user-reports/        # Báo cáo người dùng
│   │   └── weather/             # API thời tiết
│   ├── globals.css             # Styles toàn cục
│   ├── layout.tsx              # Layout chính
│   └── favicon.ico
│
├── components/                  # React components
│   └── Maps/                   # Các component bản đồ
│       ├── Maps.tsx            # Component bản đồ chính
│       ├── AdminPanel.tsx      # Panel quản trị
│       ├── UserReportButton.tsx # Nút báo cáo người dùng
│       └── WeatherPanel.tsx    # Panel thời tiết
│
├── lib/                        # Business logic & utilities
│   ├── db/                     # Database operations
│   │   ├── zones.ts           # CRUD vùng cảnh báo
│   │   ├── sensors.ts         # CRUD cảm biến
│   │   ├── sensor-rules.ts    # CRUD quy tắc
│   │   ├── predictions.ts     # CRUD dự báo
│   │   ├── user-reports.ts    # CRUD báo cáo
│   │   ├── collections.ts     # MongoDB collections
│   │   └── schema.ts          # Schema definitions (deprecated)
│   ├── automation/             # Tự động hóa
│   │   └── rule-engine.ts     # Engine xử lý quy tắc
│   ├── types/                  # TypeScript type definitions
│   │   ├── sensor.ts          # Types cho sensor
│   │   └── global.d.ts        # Global types
│   ├── mongodb.ts             # MongoDB connection
│   └── websocket.ts           # WebSocket utilities
│
├── public/                     # Static assets
├── server.ts                   # Custom Bun server (WebSocket + Proxy)
├── next.config.ts             # Next.js configuration
├── tsconfig.json              # TypeScript configuration
├── eslint.config.mjs          # ESLint configuration
├── postcss.config.mjs         # PostCSS configuration
└── package.json               # Dependencies
```

### 2.3 Kiến trúc phân tầng

```
┌─────────────────────────────────────────┐
│        PRESENTATION LAYER               │
│  (Next.js Pages + React Components)     │
│  - Maps UI                              │
│  - Admin Dashboard                      │
│  - Weather Panel                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         API LAYER                       │
│  (Next.js API Routes)                   │
│  - REST endpoints                       │
│  - Request validation                   │
│  - Error handling                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      BUSINESS LOGIC LAYER               │
│  (lib/)                                 │
│  - Rule Engine                          │
│  - Data processing                      │
│  - Validation                           │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       DATA ACCESS LAYER                 │
│  (lib/db/)                              │
│  - MongoDB operations                   │
│  - CRUD functions                       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         DATABASE                        │
│         MongoDB                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      REAL-TIME LAYER                    │
│  (WebSocket Server)                     │
│  - Bun WebSocket                        │
│  - Broadcast updates                    │
│  - Sensor data streaming                │
└─────────────────────────────────────────┘
```

---

## 3. CHỨC NĂNG CHI TIẾT

### 3.1 Hệ thống bản đồ

#### 3.1.1 Tính năng cốt lõi
- **Bản đồ tương tác**: Sử dụng VietMap GL JS
  - Zoom, pan, rotate
  - Geolocation tracking
  - Navigation controls
  - Tâm mặc định: Hà Nội (105.748684, 20.962594)

#### 3.1.2 Hiển thị vùng cảnh báo (Zones)
- **Loại vùng**:
  - 🌊 Flood (Lũ lụt) - Màu xanh (#3b82f6)
  - ⚡ Outage (Mất điện/Tắc đường) - Màu đỏ (#ef4444)

- **Hình dạng**:
  - **Circle**: Vùng nguy hiểm hình tròn (có tâm và bán kính)
  - **Line**: Tuyến đường/lộ trình nguy hiểm

- **Thuộc tính vùng**:
  ```typescript
  interface Zone {
    id: string
    type: 'flood' | 'outage'
    shape: 'circle' | 'line'
    center?: [lng, lat]        // Cho circle
    radius?: number             // Bán kính (meters)
    coordinates?: number[][]    // Cho line
    riskLevel?: number          // 0-100
    title?: string
    description?: string
    createdAt?: number
    automatedFrom?: string      // Nếu được tạo tự động
    triggeredBy?: string        // ID cảm biến kích hoạt
  }
  ```

#### 3.1.3 Tương tác người dùng
- **Hover vùng**: Hiển thị popup với thông tin chi tiết
- **Click báo cáo**: Xem chi tiết báo cáo người dùng
- **Admin mode**:
  - Vẽ vùng mới (circle/line)
  - Xóa vùng
  - Quản lý cảm biến

### 3.2 Hệ thống cảm biến (Sensors)

#### 3.2.1 Loại cảm biến
- **water_level**: Mực nước
- **temperature**: Nhiệt độ
- **humidity**: Độ ẩm

#### 3.2.2 Cấu trúc dữ liệu
```typescript
interface Sensor {
  id: string
  name: string
  location: [lng, lat]
  type: 'water_level' | 'temperature' | 'humidity'
  threshold: number          // Ngưỡng cảnh báo
  actionType: 'flood' | 'outage'
  actionTarget?: string      // Zone/route ID
  createdAt?: number
}
```

#### 3.2.3 Hiển thị trên bản đồ
- Icon hình tròn màu xanh lá (#10b981)
- Label hiển thị tên cảm biến
- Chỉ hiển thị cho admin

### 3.3 Báo cáo người dùng (User Reports)

#### 3.3.1 Chức năng
- Người dùng có thể báo cáo sự cố trực tiếp trên bản đồ
- Click vào vị trí → Điền form → Gửi báo cáo

#### 3.3.2 Cấu trúc báo cáo
```typescript
interface UserReport {
  id: string
  type: 'flood' | 'outage' | 'other'
  location: [lng, lat]
  description: string
  severity: 'low' | 'medium' | 'high'
  reporterName?: string
  status: 'new' | 'investigating' | 'resolved'
  createdAt: number
}
```

#### 3.3.3 Hiển thị
- Marker với kích thước phụ thuộc mức độ nghiêm trọng
- Màu sắc theo loại sự cố
- Animation pulse cho báo cáo nghiêm trọng
- Popup chi tiết khi click

### 3.4 Hệ thống quy tắc tự động (Rule Engine)

#### 3.4.1 Mục đích
Tự động tạo vùng cảnh báo khi cảm biến vượt ngưỡng

#### 3.4.2 Loại quy tắc
- **1-sensor**: Kích hoạt dựa trên 1 cảm biến
  - Điều kiện: `active` (vượt ngưỡng) hoặc `inactive` (dưới ngưỡng)
  
- **2-sensor**: Kích hoạt dựa trên 2 cảm biến
  - Toán tử: `AND` (cả 2 vượt ngưỡng) hoặc `OR` (1 trong 2 vượt ngưỡng)

#### 3.4.3 Cấu trúc quy tắc
```typescript
interface SensorRule {
  id: string
  name: string
  type: '1-sensor' | '2-sensor'
  sensors: string[]           // IDs cảm biến
  operator?: 'AND' | 'OR'     // Cho 2-sensor
  actionType: 'flood' | 'outage'
  actionShape: 'circle' | 'line'
  actionCoordinates?: number[][]
  actionRadius?: number
  enabled: boolean
  metadata?: {
    condition?: 'active' | 'inactive'
    points?: number[][]       // Cho line
  }
  createdAt?: number
}
```

#### 3.4.4 Quy trình thực thi
```
1. Nhận dữ liệu từ cảm biến
   ↓
2. Cập nhật reading vào memory
   ↓
3. Lấy tất cả quy tắc enabled
   ↓
4. Duyệt từng quy tắc:
   - Kiểm tra điều kiện kích hoạt
   - Nếu đạt → Tạo zone tự động
   ↓
5. Broadcast qua WebSocket
   ↓
6. Hiển thị trên bản đồ
```

#### 3.4.5 Tối ưu hóa
- Kiểm tra zone trùng lặp (trong 5 phút)
- Tự động dọn dẹp zone cũ (sau 1 giờ)
- Lưu trữ reading trong memory để xử lý nhanh

### 3.5 Hệ thống thời tiết

#### 3.5.1 Chức năng
- Hiển thị thông tin thời tiết theo vị trí
- Panel riêng cho người dùng (không phải admin)
- Chuyển đổi giữa chế độ "Bản đồ" và "Thời tiết"

#### 3.5.2 Component
- `WeatherPanel.tsx`: Hiển thị dữ liệu thời tiết
- Tích hợp với vị trí hiện tại trên bản đồ

### 3.6 Dashboard quản trị

#### 3.6.1 Chức năng
- Quản lý cảm biến (CRUD)
- Quản lý quy tắc (CRUD)
- Vẽ vùng cảnh báo thủ công
- Xem lịch sử dữ liệu
- Xóa tất cả vùng cảnh báo

#### 3.6.2 Quyền truy cập
- Route: `/admin`
- Cần xác thực (có thể mở rộng thêm authentication)

---

## 4. LUỒNG DỮ LIỆU

### 4.1 Luồng tạo vùng cảnh báo thủ công

```
User (Admin)
    ↓
Click "Draw Zone" button
    ↓
Select type (flood/outage) & shape (circle/line)
    ↓
Draw on map:
  - Circle: Click center → Move mouse → Click to finish
  - Line: Click multiple points → Double-click/Enter to finish
    ↓
Enter title & description in dialog
    ↓
POST /api/zones
    ↓
Save to MongoDB (zones collection)
    ↓
Broadcast via WebSocket
    ↓
All clients update map in real-time
```

### 4.2 Luồng dữ liệu cảm biến

```
IoT Sensor Device
    ↓
POST /api/sensor-data
{
  sensorId: "sensor-123",
  value: 15.5,
  timestamp: 1733432800000
}
    ↓
Rule Engine: checkAndExecuteRules()
    ↓
Check enabled rules:
  - 1-sensor rules: Compare with threshold
  - 2-sensor rules: Check both sensors with AND/OR
    ↓
If triggered → createAutomatedZone()
    ↓
Save zone to MongoDB
    ↓
Broadcast via WebSocket
{
  type: 'zone_created',
  zone: { ... }
}
    ↓
All clients update map
```

### 4.3 Luồng báo cáo người dùng

```
User (End-user)
    ↓
Click "Report" button
    ↓
Click location on map
    ↓
Fill form:
  - Type (flood/outage/other)
  - Description
  - Severity (low/medium/high)
  - Reporter name (optional)
    ↓
POST /api/user-reports
    ↓
Save to MongoDB (userReports collection)
    ↓
Broadcast via WebSocket
{
  type: 'user_report_created',
  report: { ... }
}
    ↓
All clients show new marker on map
```

### 4.4 Luồng WebSocket real-time

```
Client connects
    ↓
WebSocket: ws://localhost:3000/ws
    ↓
Server stores client in Set<WebSocket>
    ↓
When data changes (zone/sensor/report):
    ↓
Broadcast message to all clients
    ↓
Clients receive & update UI instantly
```

---

## 5. CƠ SỞ DỮ LIỆU

### 5.1 MongoDB Collections

#### 5.1.1 zones
```javascript
{
  _id: ObjectId,
  id: String,              // Unique ID
  type: String,            // 'flood' | 'outage'
  shape: String,           // 'circle' | 'line'
  center: [Number],        // [lng, lat] - for circle
  radius: Number,          // meters - for circle
  coordinates: [[Number]], // [[lng,lat],...] - for line
  riskLevel: Number,       // 0-100
  title: String,
  description: String,
  createdAt: Number,       // timestamp
  automatedFrom: String,   // rule ID (if automated)
  triggeredBy: String      // sensor ID (if automated)
}
```

#### 5.1.2 sensors
```javascript
{
  _id: ObjectId,
  id: String,
  name: String,
  location: [Number],      // [lng, lat]
  type: String,            // 'water_level' | 'temperature' | 'humidity'
  threshold: Number,
  actionType: String,      // 'flood' | 'outage'
  actionTarget: String,
  createdAt: Number
}
```

#### 5.1.3 sensorRules
```javascript
{
  _id: ObjectId,
  id: String,
  name: String,
  type: String,            // '1-sensor' | '2-sensor'
  sensors: [String],       // sensor IDs
  operator: String,        // 'AND' | 'OR'
  actionType: String,      // 'flood' | 'outage'
  actionShape: String,     // 'circle' | 'line'
  actionCoordinates: [[Number]],
  actionRadius: Number,
  enabled: Boolean,
  metadata: Object,
  createdAt: Number
}
```

#### 5.1.4 sensorData
```javascript
{
  _id: ObjectId,
  sensorId: String,
  value: Number,
  timestamp: Number,
  metadata: Object
}
```

#### 5.1.5 userReports
```javascript
{
  _id: ObjectId,
  id: String,
  type: String,            // 'flood' | 'outage' | 'other'
  location: [Number],      // [lng, lat]
  description: String,
  severity: String,        // 'low' | 'medium' | 'high'
  reporterName: String,
  status: String,          // 'new' | 'investigating' | 'resolved'
  createdAt: Number
}
```

#### 5.1.6 predictions
```javascript
{
  _id: ObjectId,
  id: String,
  zoneId: String,
  predictedRiskLevel: Number,
  confidence: Number,      // 0-1
  timestamp: Number,
  factors: Object,         // Các yếu tố ảnh hưởng
  createdAt: Number
}
```

### 5.2 Indexes

```javascript
// zones
db.zones.createIndex({ id: 1 }, { unique: true })
db.zones.createIndex({ type: 1 })
db.zones.createIndex({ createdAt: -1 })
db.zones.createIndex({ automatedFrom: 1 })

// sensors
db.sensors.createIndex({ id: 1 }, { unique: true })
db.sensors.createIndex({ type: 1 })

// sensorRules
db.sensorRules.createIndex({ id: 1 }, { unique: true })
db.sensorRules.createIndex({ enabled: 1 })

// sensorData
db.sensorData.createIndex({ sensorId: 1, timestamp: -1 })
db.sensorData.createIndex({ timestamp: -1 })

// userReports
db.userReports.createIndex({ id: 1 }, { unique: true })
db.userReports.createIndex({ status: 1 })
db.userReports.createIndex({ createdAt: -1 })
```

---

## 6. API ENDPOINTS

### 6.1 Zones API

#### GET /api/zones
Lấy tất cả vùng cảnh báo
```
Response: {
  zones: Zone[]
}
```

#### POST /api/zones
Tạo vùng cảnh báo mới
```
Request Body: Zone
Response: {
  zone: Zone
}
```

#### DELETE /api/zones
Xóa tất cả vùng cảnh báo
```
Response: {
  message: string
}
```

#### DELETE /api/zones/:id
Xóa vùng cảnh báo theo ID
```
Response: {
  message: string
}
```

### 6.2 Sensors API

#### GET /api/sensors
Lấy tất cả cảm biến
```
Response: {
  sensors: Sensor[]
}
```

#### POST /api/sensors
Tạo cảm biến mới
```
Request Body: Sensor
Response: {
  sensor: Sensor
}
```

#### DELETE /api/sensors?id=xxx
Xóa cảm biến
```
Response: {
  message: string
}
```

### 6.3 Sensor Data API

#### POST /api/sensor-data
Gửi dữ liệu từ cảm biến
```
Request Body: {
  sensorId: string,
  value: number,
  timestamp: number
}
Response: {
  success: boolean,
  execution?: ExecutionResult
}
```

#### GET /api/sensor-data?sensorId=xxx&limit=100
Lấy lịch sử dữ liệu cảm biến
```
Response: {
  data: SensorData[]
}
```

### 6.4 Sensor Rules API

#### GET /api/sensor-rules
Lấy tất cả quy tắc
```
Response: {
  rules: SensorRule[]
}
```

#### POST /api/sensor-rules
Tạo quy tắc mới
```
Request Body: SensorRule
Response: {
  rule: SensorRule
}
```

#### PUT /api/sensor-rules/:id
Cập nhật quy tắc
```
Request Body: Partial<SensorRule>
Response: {
  rule: SensorRule
}
```

#### DELETE /api/sensor-rules/:id
Xóa quy tắc
```
Response: {
  message: string
}
```

### 6.5 User Reports API

#### GET /api/user-reports
Lấy tất cả báo cáo
```
Response: {
  reports: UserReport[]
}
```

#### POST /api/user-reports
Tạo báo cáo mới
```
Request Body: UserReport
Response: {
  report: UserReport
}
```

#### PATCH /api/user-reports/:id
Cập nhật trạng thái báo cáo
```
Request Body: {
  status: 'new' | 'investigating' | 'resolved'
}
Response: {
  report: UserReport
}
```

### 6.6 Predictions API

#### GET /api/predictions?zoneId=xxx
Lấy dự báo cho vùng
```
Response: {
  predictions: Prediction[]
}
```

#### POST /api/predictions
Tạo dự báo mới
```
Request Body: Prediction
Response: {
  prediction: Prediction
}
```

### 6.7 Weather API

#### GET /api/weather?lat=xxx&lng=xxx
Lấy thông tin thời tiết
```
Response: {
  weather: WeatherData
}
```

---

## 7. WEBSOCKET PROTOCOL

### 7.1 Connection
```
WebSocket URL: ws://localhost:3000/ws
Protocol: Native WebSocket
```

### 7.2 Message Types

#### zone_created
```json
{
  "type": "zone_created",
  "zone": {
    "id": "zone-123",
    "type": "flood",
    ...
  }
}
```

#### zone_updated
```json
{
  "type": "zone_updated",
  "zone": { ... }
}
```

#### zone_deleted
```json
{
  "type": "zone_deleted",
  "zoneId": "zone-123"
}
```

#### zones_cleared
```json
{
  "type": "zones_cleared"
}
```

#### sensor_created
```json
{
  "type": "sensor_created",
  "sensor": { ... }
}
```

#### sensor_deleted
```json
{
  "type": "sensor_deleted",
  "sensorId": "sensor-123"
}
```

#### sensor_data
```json
{
  "type": "sensor_data",
  "data": {
    "sensorId": "sensor-123",
    "value": 15.5,
    "timestamp": 1733432800000
  }
}
```

#### user_report_created
```json
{
  "type": "user_report_created",
  "report": { ... }
}
```

#### prediction
```json
{
  "type": "prediction",
  "prediction": { ... }
}
```

---

## 8. BẢO MẬT VÀ HIỆU NĂNG

### 8.1 Bảo mật

#### 8.1.1 Hiện tại
- CORS cơ bản
- Validation input đơn giản
- MongoDB connection string qua ENV

#### 8.1.2 Cần cải thiện
- [ ] Authentication & Authorization
- [ ] API rate limiting
- [ ] Input sanitization
- [ ] SQL/NoSQL injection prevention
- [ ] XSS protection
- [ ] HTTPS enforcement
- [ ] JWT tokens
- [ ] Role-based access control

### 8.2 Hiệu năng

#### 8.2.1 Tối ưu hóa hiện tại
- WebSocket cho real-time updates (tránh polling)
- In-memory cache cho sensor readings
- MongoDB indexes
- Next.js automatic code splitting
- Bun runtime (nhanh hơn Node.js)

#### 8.2.2 Có thể cải thiện
- [ ] Redis cache cho dữ liệu thường xuyên truy vấn
- [ ] CDN cho static assets
- [ ] Database query optimization
- [ ] Lazy loading components
- [ ] Image optimization
- [ ] Service Worker cho offline support
- [ ] Debouncing/throttling cho map events

### 8.3 Khả năng mở rộng

#### 8.3.1 Horizontal scaling
- Tách WebSocket server riêng
- Load balancer cho API
- MongoDB replica set
- Redis pub/sub cho WebSocket clustering

#### 8.3.2 Vertical scaling
- Tăng RAM cho MongoDB
- Optimize queries & indexes
- Connection pooling

---

## 9. DEPLOYMENT

### 9.1 Yêu cầu hệ thống

#### Production
- **Server**: Linux/Ubuntu 20.04+
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 20GB SSD
- **Network**: Port 3000 exposed

#### Dependencies
- Bun 1.x
- MongoDB 7.0+
- Node.js 20+ (fallback)

### 9.2 Biến môi trường

```bash
# .env.local
MONGODB_URI=mongodb://localhost:27017/svattt
NEXT_PUBLIC_VIETMAP_API_KEY=your_vietmap_key
PORT=3000
NODE_ENV=production
```

### 9.3 Build & Deploy

#### Development
```bash
# Install dependencies
bun install

# Start Next.js dev server
bun run dev:next

# Start Bun WebSocket server (in another terminal)
bun run dev
```

#### Production
```bash
# Build
bun run build

# Start production server
bun run start
```

### 9.4 Docker (Optional)

```dockerfile
FROM oven/bun:1

WORKDIR /app

COPY package.json bun.lock ./
RUN bun install --production

COPY . .
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "start"]
```

---

## 10. TESTING

### 10.1 Unit Testing
- [ ] Utils functions
- [ ] Database operations
- [ ] Rule engine logic

### 10.2 Integration Testing
- [ ] API endpoints
- [ ] WebSocket connections
- [ ] Database transactions

### 10.3 E2E Testing
- [ ] User flows
- [ ] Admin flows
- [ ] Real-time updates

### 10.4 Tools (Đề xuất)
- Jest/Vitest
- React Testing Library
- Playwright/Cypress
- MongoDB Memory Server

---

## 11. MONITORING & LOGGING

### 11.1 Logging

#### Hiện tại
- Console.log cho development
- Bun native logging

#### Cần bổ sung
- [ ] Winston/Pino logger
- [ ] Log levels (error, warn, info, debug)
- [ ] Log rotation
- [ ] Centralized logging (ELK stack)

### 11.2 Monitoring

#### Cần bổ sung
- [ ] Application metrics (Prometheus)
- [ ] Database metrics
- [ ] WebSocket connection stats
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Uptime monitoring

---

## 12. ROADMAP & CẢI TIẾN

### 12.1 Tính năng mới

#### Phase 1 (Ngắn hạn)
- [ ] Authentication & user management
- [ ] Email/SMS notifications
- [ ] Historical data visualization
- [ ] Mobile responsive improvements
- [ ] Export reports (PDF/CSV)

#### Phase 2 (Trung hạn)
- [ ] Machine Learning predictions
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Integration với các API thời tiết khác
- [ ] Advanced analytics dashboard

#### Phase 3 (Dài hạn)
- [ ] AI-powered risk assessment
- [ ] Drone integration
- [ ] Satellite imagery
- [ ] Social media integration
- [ ] Public API

### 12.2 Cải tiến kỹ thuật

- [ ] Microservices architecture
- [ ] GraphQL API
- [ ] Event-driven architecture
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Automated testing
- [ ] Performance optimization
- [ ] Security hardening

---

## 13. TÀI LIỆU THAM KHẢO

### 13.1 External APIs
- [VietMap API Documentation](https://vietmap.vn/docs)
- [MapLibre GL JS](https://maplibre.org/)

### 13.2 Frameworks & Libraries
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Bun Documentation](https://bun.sh/docs)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)

### 13.3 Best Practices
- [Next.js App Router Best Practices](https://nextjs.org/docs/app/building-your-application)
- [MongoDB Schema Design](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)
- [WebSocket Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API/Writing_WebSocket_servers)

---

## 14. LIÊN HỆ & HỖ TRỢ

### 14.1 Team
- **Organization**: PKA-OpenLD
- **License**: Apache License 2.0

### 14.2 Repository
- Mã nguồn: [Link to repository]
- Issues: [Link to issues]
- Documentation: [Link to docs]

---

## PHỤ LỤC

### A. Glossary (Từ điển thuật ngữ)

- **Zone**: Vùng cảnh báo
- **Sensor**: Cảm biến IoT
- **Rule**: Quy tắc tự động
- **User Report**: Báo cáo từ người dùng
- **Prediction**: Dự báo rủi ro
- **Threshold**: Ngưỡng cảnh báo
- **WebSocket**: Giao thức real-time
- **MongoDB**: Cơ sở dữ liệu NoSQL

### B. Common Issues & Solutions

#### Issue: WebSocket không kết nối được
**Solution**: Kiểm tra server.ts đang chạy, check port 3000

#### Issue: Bản đồ không load
**Solution**: Kiểm tra NEXT_PUBLIC_VIETMAP_API_KEY trong .env.local

#### Issue: MongoDB connection failed
**Solution**: Kiểm tra MONGODB_URI và MongoDB service đang chạy

#### Issue: Sensors không hiển thị
**Solution**: Đảm bảo đăng nhập với quyền admin (isAdmin=true)

### C. Development Tips

1. **Hot Reload**: Sử dụng `bun run dev:next` để Next.js tự động reload
2. **Debug WebSocket**: Sử dụng browser DevTools → Network → WS
3. **MongoDB GUI**: Sử dụng MongoDB Compass để xem dữ liệu
4. **API Testing**: Sử dụng Postman/Thunder Client
5. **TypeScript Errors**: Chạy `npx tsc --noEmit` để kiểm tra

---

**Ngày tạo**: 2025-12-05  
**Phiên bản tài liệu**: 1.0  
**Tác giả**: PKA-OpenLD Team
