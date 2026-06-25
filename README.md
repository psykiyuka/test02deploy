# 电商平台系统 - 部署包

## 快速启动

### 前提条件
- 已安装 Docker 和 Docker Compose
- 已安装 Node.js 18+（前端开发模式需要）

### 1. 启动后端服务（PostgreSQL + Redis + FastAPI + Nginx）

```bash
docker compose up -d --build
```

等待所有容器启动完成（首次启动需要构建镜像和初始化数据库）。

### 2. 启动前端开发服务器

```bash
cd shop-frontend
npm install
npm run dev
```

### 3. 访问系统

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8004/api/shop/ |
| API 文档 | http://localhost:8004/docs |
| Nginx 代理 | http://localhost:83 |

### 4. 测试账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 管理员 | admin@shop.local | 12345678 |
| 买家 | test@test.com | 12345678 |
| 商家 | testmerchant2@shop.com | 12345678 |

## 目录结构

```
test01-deploy/
├── .env                  # 环境变量配置
├── docker-compose.yml    # Docker 编排文件
├── init.sql              # 数据库初始化脚本
├── nginx/
│   └── nginx.conf        # Nginx 配置
├── shop-service/         # 后端 FastAPI 服务
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── apps/             # API 路由
│   ├── domain/           # 业务逻辑
│   ├── infrastructure/   # 基础设施
│   ├── middleware/       # 中间件
│   └── migrations/       # 数据库迁移脚本
├── shop-frontend/        # 前端 Vue 3 应用
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/              # 源代码
└── docs/
    └── system-usage-report.html  # 系统使用报告
```

## 技术栈

- **前端**: Vue 3 + TypeScript + Pinia + Tailwind CSS v4 + Vite
- **后端**: FastAPI + PostgreSQL + Redis
- **部署**: Docker Compose

## 常用命令

```bash
# 查看容器状态
docker compose ps

# 查看后端日志
docker compose logs -f shop-service

# 重启后端
docker compose restart shop-service

# 停止所有服务
docker compose down

# 停止并清除数据（慎用）
docker compose down -v
```

## 版本

当前版本: test01-v1.7
