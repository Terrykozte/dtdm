# ☁️ MyMiniCloud — Hệ Thống Mô Phỏng Hạ Tầng Cloud 9 Server

**Sinh viên thực hiện:** Phạm Hoài Thương  
**Mã số sinh viên:** 52300262  
**Học phần:** Điện Toán Đám Mây (Cloud Computing)  
**Khoa / Ngành:** Công Nghệ Thông Tin  
**GitHub Repository:** [https://github.com/Terrykozte/dtdm](https://github.com/Terrykozte/dtdm)  
**Docker Hub Organization:** [https://hub.docker.com/u/terrykozte](https://hub.docker.com/u/terrykozte)  
**AWS EC2 Live Deployment:** [http://18.140.70.14](http://18.140.70.14)

---

## 📌 Tổng Quan Dự Án

Dự án xây dựng và mô phỏng hệ sinh thái Cloud cơ bản (**MyMiniCloud**) đáp ứng 100% các tiêu chí và yêu cầu trong đề cương môn học Điện Toán Đám Mây:
1. **Kiến trúc gồm 9 loại máy chủ cốt lõi**: Web Frontend, App Backend, Relational Database, Identity/Authentication, Object Storage S3, Internal DNS, Monitoring, Metrics Visualization Dashboard, và API Gateway / Load Balancer.
2. **Triển khai đa nền tảng**:
   - **Môi trường Local**: Chạy trọn vẹn thông qua Docker Compose và runner script cho dự án Web VeganGlow (Next.js 16).
   - **Môi trường Cloud AWS EC2**: Triển khai thực tế trên máy ảo Ubuntu 22.04 LTS (IP: `18.140.70.14`, Region `ap-southeast-1` Singapore) với đầy đủ Security Group, EBS Volume mở rộng 25GB, Swap Memory, và toàn bộ 12 containers hoạt động 24/7.
3. **Đóng gói và phát hành Docker Hub**:
   - `terrykozte/myminicloud-web:latest`: Web Nginx tĩnh + Blog 3 bài viết + Load Balancing.
   - `terrykozte/myminicloud-app:latest`: Flask API Backend + OIDC + MariaDB Student DB.
   - `terrykozte/veganglow:latest`: Ứng dụng thương mại điện tử Next.js 16.

---

## 📁 Cấu Trúc Thư Mục Chuẩn (Đúng Quy Cách Đề Tài)

```
PhamHoaiThuongminicloud/
├── app/                              # 2. Application Backend Server (Python Flask API)
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   └── students.json
├── auth/                             # 4. Authentication Server (Keycloak 26 OIDC)
│   └── realm-sv001.json
├── db/                               # 3. Relational Database Server (MariaDB 11)
│   ├── crud-demo.sql
│   └── init/
│       ├── 001_init.sql
│       └── 002_studentdb.sql
├── dns/                              # 6. Internal DNS Server (Bind9 9.18)
│   ├── db.cloud.local
│   ├── named.conf.local
│   └── named.conf.options
├── grafana/                          # 8. Visualization Dashboard (Grafana)
│   ├── dashboards/
│   │   └── system-health.json
│   └── provisioning/
│       ├── dashboards/dashboards.yml
│       └── datasources/prometheus.yml
├── monitor/                          # 7. Monitoring Server (Prometheus)
│   └── prometheus.yml
├── proxy/                            # 9. API Gateway & Load Balancer (Nginx)
│   └── nginx.conf
├── storage/                          # 5. Object Storage Server (MinIO S3 Compatible)
│   ├── data/
│   └── seed/
│       ├── avatar.jpg
│       └── BaoCao.pdf
├── web/                              # 1. Web Frontend Server (Nginx + Blog 3 bài)
│   ├── Dockerfile
│   ├── conf.default
│   └── html/
│       ├── 404.html
│       ├── index.html
│       ├── lb-test.html
│       ├── assets/style.css
│       └── blog/
│           ├── index.html
│           ├── blog1.html
│           ├── blog2.html
│           ├── blog3.html
│           └── images/
├── docker-compose.yml                # File điều phối toàn bộ 12 container
└── README.md                         # Báo cáo kiến trúc & hướng dẫn vận hành
```

---

## 🏛️ Bảng Chi Tiết 9 Loại Máy Chủ & Mở Rộng

| STT | Loại Server | Service Container | Port Container | Port Host | Công nghệ | Vai trò & Yêu cầu Kỹ thuật |
|:---:|:---|:---|:---:|:---:|:---|:---|
| **1** | **Web Frontend Server** | `web-frontend-server` | 80 | `8080` | Nginx Alpine | Trang chủ giới thiệu, blog cá nhân 3 bài viết chuẩn SEO, trang test Load Balancing. |
| **-** | *Web Server Dự Phòng* | `web-frontend-server2` | 80 | `8082` | Nginx Alpine | Phục vụ cân bằng tải Round-Robin (MR 10) cùng `web-frontend-server`. |
| **-** | *E-Commerce Web App* | `veganglow-web` | 3000 | `3001` | Next.js 16 | Ứng dụng web thương mại điện tử VeganGlow đóng gói từ Docker Hub. |
| **2** | **Application Server** | `application-backend-server` | 8081 | `8085` | Python 3.11 Flask | REST API: `/hello`, `/student`, `/api/students-db`, kiểm tra OIDC Bearer Token `/secure`. |
| **3** | **Database Server** | `relational-database-server` | 3306 | `3306` | MariaDB 11 | CSDL `minicloud` và `studentdb`. Dữ liệu bảng `students` chứa MSSV 52300262. |
| **4** | **Authentication Server** | `authentication-identity-server` | 8080 | `8081` | Keycloak 26 | IdP / SSO, phát hành Token JWT, thiết lập Realm `realm_sv001` & Client `flask-app`. |
| **5** | **Object Storage Server** | `object-storage-server` | 9000, 9001 | `9000`, `9001` | MinIO (S3 API) | Lưu trữ đối tượng S3: bucket `demo`, `profile-pics` (avatar), `documents` (PDF). |
| **6** | **DNS / Name Service** | `internal-dns-server` | 53 | `1053` (TCP/UDP)| Bind9 9.18 | Phân giải domain nội bộ `cloud.local` cho các service (`web.cloud.local`, v.v.). |
| **7** | **Monitoring Server** | `monitoring-prometheus-server` | 9090 | `9090` | Prometheus | Thu thập metric từ Node Exporter và các endpoints Web Server. |
| **-** | *Node Exporter* | `monitoring-node-exporter-server`| 9100 | `9100` | Prometheus Exporter| Thu thập số liệu phần cứng host (CPU, RAM, Disk, Network I/O). |
| **8** | **Dashboard / Metrics** | `monitoring-grafana-dashboard-server`| 3000 | `3000` | Grafana OSS | Trực quan hóa dashboard giám sát tài nguyên máy chủ theo thời gian thực. |
| **9** | **API Gateway / Proxy** | `api-gateway-proxy-server` | 80 | `80` | Nginx Proxy | Reverse Proxy duy nhất tiếp nhận request ngoài và cân bằng tải Round-Robin. |

---

## 📦 Danh Sách Docker Hub Images Đã Đẩy Lên

Tất cả các image tùy chỉnh đã được build và push thành công lên Docker Hub công khai:
- 🌐 **Web Server Image:** [https://hub.docker.com/r/terrykozte/myminicloud-web](https://hub.docker.com/r/terrykozte/myminicloud-web)
- ⚙️ **App Server Image:** [https://hub.docker.com/r/terrykozte/myminicloud-app](https://hub.docker.com/r/terrykozte/myminicloud-app)
- 🛍️ **VeganGlow E-Commerce Image:** [https://hub.docker.com/r/terrykozte/veganglow](https://hub.docker.com/r/terrykozte/veganglow)

---

## 🌐 Trực Tiếp Trên AWS EC2 Cloud (Live Production)

Hệ thống đang hoạt động trực tiếp tại địa chỉ IP Public: **`18.140.70.14`**

| Dịch vụ | Đường dẫn truy cập trên AWS EC2 | Tài khoản mặc định |
|:---|:---|:---|
| **API Gateway (Cổng chính)** | `http://18.140.70.14/` | Không yêu cầu |
| **Blog Cá Nhân (3 Bài viết)** | `http://18.140.70.14/blog/` | Không yêu cầu |
| **Load Balancing Test** | `http://18.140.70.14/lb-test/` | F5 để thấy luân phiên Server 1 & Server 2 |
| **Backend REST API** | `http://18.140.70.14/api/hello` | Trả về JSON chào mừng |
| **Student Info API** | `http://18.140.70.14/api/student` | Trả về thông tin SV 52300262 |
| **Database Connected API** | `http://18.140.70.14/api/students-db` | Đọc dữ liệu trực tiếp từ MariaDB |
| **VeganGlow Storefront** | `http://18.140.70.14:3001/` | Web Next.js 16 thương mại điện tử |
| **Grafana Monitoring Dashboard** | `http://18.140.70.14:3000/` | `admin` / `admin` |
| **Prometheus Metrics Targets** | `http://18.140.70.14:9090/targets` | Trạng thái các endpoint giám sát |
| **MinIO Storage Console** | `http://18.140.70.14:9001/` | `minioadmin` / `minioadmin` |
| **Keycloak Identity Console** | `http://18.140.70.14:8081/` | `admin` / `admin` |

---

## 💻 Hướng Dẫn Vận Hành Môi Trường Localhost

### 1. Khởi động Web VeganGlow trên Localhost (Next.js 16)
Thư mục `VeganGlow` đã được cấu hình độc lập hoàn toàn:
1. Vào thư mục `c:\Users\Terrykozte\OneDrive\Desktop\bcck\VeganGlow`.
2. Nhấp đúp chuột vào file **`start_dev.bat`**.
3. File tự động nhận diện Node.js, khởi chạy Webpack Dev Server và tự động mở trình duyệt tại:
   👉 **`http://localhost:3000`**

### 2. Khởi động trọn bộ 9 Server MiniCloud trên máy local (Nếu cài Docker Desktop)
```bash
cd PhamHoaiThuongminicloud
docker compose up -d --build
docker compose ps
```

---

## 🎯 10 Yêu Cầu Mở Rộng Đã Hoàn Thành (Thang Điểm 10/10)

1. **Object Storage S3 (MinIO):** Tự động khởi tạo 3 bucket `demo`, `profile-pics`, `documents` kèm dữ liệu mẫu `avatar.jpg` và `BaoCao.pdf`.
2. **Authentication (Keycloak):** Cấu hình Realm `realm_sv001`, OIDC Client `flask-app`, cấp phát token JWT bảo vệ endpoint `/secure`.
3. **DNS Server (Bind9):** Cấu hình phân giải Forward Zone `cloud.local` cho tất cả các máy chủ nội bộ.
4. **MariaDB Database:** Tự động nạp schema `001_init.sql` và `002_studentdb.sql`, cung cấp script `db/crud-demo.sql` phục vụ demo CRUD.
5. **Prometheus Monitoring:** Giám sát Node Exporter (CPU, RAM, Disk) và tự động scrape chỉ số từ Web Server.
6. **Grafana Dashboards:** Tự động nạp cấu hình Datasource & Dashboard `system-health.json` ngay khi khởi động.
7. **Blog Cá Nhân 3 Bài Viết:** Tích hợp đầy đủ tại `web/html/blog/` với giao diện chuyên nghiệp, hình ảnh minh họa vector.
8. **Đóng Gói & Xuất Bản Docker Hub:** Build và push 3 image lên `terrykozte/myminicloud-web`, `terrykozte/myminicloud-app`, `terrykozte/veganglow`.
9. **Triển Khai Thực Tế Lên AWS Cloud:** Máy ảo EC2 Ubuntu 22.04 LTS cấu hình hoàn chỉnh Security Group, 25GB Storage, chạy trực tiếp trên Internet.
10. **Load Balancer (Round-Robin):** Nginx cấu hình Upstream luân chuyển tải giữa `web-frontend-server` và `web-frontend-server2`.
