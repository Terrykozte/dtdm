# ☁️ MyMiniCloud — Hệ Thống Mô Phỏng Hạ Tầng Cloud 9 Server

**Sinh viên thực hiện:** Phạm Hoài Thương  
**Mã số sinh viên:** 52300262  
**Học phần:** Điện Toán Đám Mây (Cloud Computing)

Dự án xây dựng và mô phỏng hệ thống Cloud thu nhỏ (MyMiniCloud) gồm 9 loại máy chủ cơ bản trên nền tảng Docker & Docker Compose, sẵn sàng triển khai trên môi trường Local và AWS EC2 (Ubuntu).

---

## 📁 Cấu Trúc Dự Án (Theo Yêu Cầu Đề Tài)

```
PhamHoaiThuongminicloud/
├── app/                  # Application Backend Server (Flask API)
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── students.json
├── auth/                 # Authentication Server (Keycloak OIDC)
│   └── realm-sv001.json
├── db/                   # Relational Database Server (MariaDB)
│   ├── crud-demo.sql
│   └── init/
│       ├── 001_init.sql
│       └── 002_studentdb.sql
├── dns/                  # Internal DNS Server (Bind9)
│   ├── db.cloud.local
│   ├── named.conf.local
│   └── named.conf.options
├── grafana/              # Logging & Visualization (Grafana)
│   ├── dashboards/
│   └── provisioning/
├── monitor/              # Monitoring Server (Prometheus)
│   └── prometheus.yml
├── proxy/                # API Gateway / Reverse Proxy & Load Balancer (Nginx)
│   └── nginx.conf
├── storage/              # Object Storage (MinIO - S3 Compatible)
│   ├── data/
│   └── seed/
├── web/                  # Web Frontend Server (Nginx HTML + Blog)
│   ├── Dockerfile
│   ├── conf.default
│   └── html/
│       ├── 404.html
│       ├── index.html
│       ├── lb-test.html
│       ├── assets/
│       └── blog/
│           ├── index.html
│           ├── blog1.html
│           ├── blog2.html
│           ├── blog3.html
│           └── images/
├── docker-compose.yml    # File điều phối toàn bộ 9 container
└── README.md
```

---

## 🏛️ Danh Sách 9 Loại Server

| STT | Loại Server | Service Name | Port | Công nghệ | Vai trò & Yêu cầu |
|:---:|:---|:---|:---:|:---|:---|
| **1** | **Web Server** | `web-frontend-server` | `8080:80`, `8082:80` | Nginx Alpine | Phục vụ trang tĩnh, blog cá nhân 3 bài viết, hỗ trợ Round-Robin Load Balancing |
| **2** | **Application Server** | `application-backend-server` | `8085:8081` | Python Flask API | REST API `/hello`, `/student` (JSON), kết nối DB `/api/students-db`, xác thực OIDC `/secure` |
| **3** | **Database Server** | `relational-database-server` | `3306:3306` | MariaDB 11 | CSDL quan hệ `minicloud` và `studentdb` (bảng `students` gồm thông tin sinh viên) |
| **4** | **Authentication Server** | `authentication-identity-server` | `8081:8080` | Keycloak 26 | Quản lý định danh (IdP/SSO), phát hành JWT token, cấu hình OIDC realm `realm_sv001` |
| **5** | **File / Object Storage** | `object-storage-server` | `9000:9000`, `9001:9001` | MinIO | Lưu trữ đối tượng S3: bucket `demo`, `profile-pics` (avatar), `documents` (PDF) |
| **6** | **DNS / Name Service** | `internal-dns-server` | `1053:53/udp` | Bind9 9.18 | Quản lý phân giải tên miền nội bộ `cloud.local` cho các service trong mạng |
| **7** | **Monitoring Server** | `monitoring-prometheus-server` | `9090:9090` | Prometheus + Node Exporter | Thu thập chỉ số hệ thống (CPU, RAM, Disk, Network) và giám sát trạng thái Web Server |
| **8** | **Logging / Dashboard** | `monitoring-grafana-dashboard-server` | `3000:3000` | Grafana | Trực quan hóa dashboard giám sát tài nguyên (CPU Usage, Memory, Network Traffic) |
| **9** | **Reverse Proxy / Gateway** | `api-gateway-proxy-server` | `80:80` | Nginx | Cổng vào duy nhất (API Gateway), điều phối request và cân bằng tải Round Robin |

---

## 🚀 Hướng Dẫn Khởi Động & Kiểm Thử

### 1. Khởi động hệ thống
```bash
docker compose build --no-cache
docker compose up -d
docker compose ps
```

### 2. Kiểm thử từng Server

#### 1) Web Frontend Server
```bash
curl -I http://localhost:8080/
curl -I http://localhost:8080/blog/
```

#### 2) Application Backend Server
```bash
curl http://localhost:8085/hello
curl http://localhost:8085/student
curl http://localhost:8085/api/students-db
```

#### 3) Database Server (MariaDB)
```bash
docker exec -it relational-database-server mariadb -uroot -proot -e "USE studentdb; SELECT * FROM students;"
```

#### 4) Authentication Server (Keycloak)
- Mở trình duyệt: `http://localhost:8081` (Tài khoản: `admin` / `admin`)

#### 5) Object Storage Server (MinIO)
- Console: `http://localhost:9001` (Tài khoản: `minioadmin` / `minioadmin`)

#### 6) Internal DNS Server (Bind9)
```bash
dig @127.0.0.1 -p 1053 web-frontend-server.cloud.local +short
dig @127.0.0.1 -p 1053 app-backend.cloud.local +short
```

#### 7) Monitoring Server (Prometheus)
- Mở trình duyệt: `http://localhost:9090/targets` (Node Exporter & Web targets đều ở trạng thái `UP`)

#### 8) Grafana Dashboard
- Mở trình duyệt: `http://localhost:3000` (Tài khoản: `admin` / `admin`)

#### 9) API Gateway & Load Balancing
```bash
curl -I http://localhost/             # Route đến Web Frontend
curl -s http://localhost/api/hello     # Route đến Backend API
curl -s http://localhost/student/      # Route đến danh sách sinh viên
curl -I http://localhost/auth/         # Redirect đến Keycloak
```

---

## 🌐 Triển Khai Trên AWS EC2 (Ubuntu 22.04 LTS)

1. Tạo máy ảo **AWS EC2** (Ubuntu 22.04 LTS).
2. Cấu hình Inbound Rules cho Security Group:
   - `Port 22`: SSH
   - `Port 80`: HTTP (API Gateway)
   - `Port 3000`: Grafana
   - `Port 8081`: Keycloak
   - `Port 9001`: MinIO Console
3. SSH vào EC2 và triển khai:
   ```bash
   git clone <REPO_URL>
   cd PhamHoaiThuongminicloud
   docker compose up -d --build
   ```
4. Kiểm tra dịch vụ qua IP Public: `http://<EC2_PUBLIC_IP>/`.
