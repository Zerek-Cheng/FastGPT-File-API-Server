# FastGPT 文件 API 服务器

这是一个符合 FastGPT API 文件库标准的服务端实现，用于提供本地文件系统中的文件和文件夹访问。

## 功能特点

- 提供符合 FastGPT API 文件库规范的接口
- 支持文件和文件夹的浏览
- 支持文件内容的获取
- 支持文件阅读链接的生成
- 支持基于 Bearer Token 的身份验证

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/fastgpt-file-api-server.git
cd fastgpt-file-api-server
```

2. 创建并激活虚拟环境：

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. 安装依赖：

```bash
pip install -r requirements.txt
```

## 配置

在 `main.py` 文件中，修改 `API_TOKEN` 变量为你自己的密钥：

```python
API_TOKEN = "your-secret-token"  # 修改为你自己的密钥
```

## 使用方法

1. 启动服务器：

```bash
python main.py
```

服务器将在 http://localhost:8000 上运行。

2. 在 FastGPT 中配置 API 文件库：

- baseURL: `http://localhost:8000`
- authorization: `your-secret-token`

## API 接口

### 1. 获取文件树

```
POST /v1/file/list
```

请求体：

```json
{
    "parentId": null,  // 可选，父目录ID
    "searchKey": ""    // 可选，搜索关键词
}
```

### 2. 获取文件内容

```
GET /v1/file/content?id=文件ID
```

### 3. 获取文件阅读链接

```
GET /v1/file/read?id=文件ID
```

## 注意事项

- 本服务仅用于演示和测试目的
- 在生产环境中使用时，请确保适当的安全措施
- 默认情况下，服务器会提供 `resources` 目录中的文件

## 许可证

MIT 