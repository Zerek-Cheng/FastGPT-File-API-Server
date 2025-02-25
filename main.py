from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
import os
import json
from datetime import datetime
import uvicorn

app = FastAPI(title="FastGPT文件API服务")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全验证
security = HTTPBearer()
API_TOKEN = "your-secret-token"  # 在实际应用中，应该从环境变量或配置文件中读取


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# 数据模型
class FileListItem(BaseModel):
    id: str
    parentId: Optional[str] = None
    name: str
    type: str  # "file" 或 "folder"
    updateTime: datetime
    createTime: datetime


class FileListRequest(BaseModel):
    parentId: Optional[str] = None
    searchKey: Optional[str] = ""


class FileContentResponse(BaseModel):
    content: Optional[str] = None
    previewUrl: Optional[str] = None


class FileReadResponse(BaseModel):
    url: str


class ResponseModel(BaseModel):
    code: int = 200
    success: bool = True
    message: str = ""
    data: Any


# 文件系统操作
def get_absolute_path(file_id: str) -> str:
    """将文件ID转换为绝对路径"""
    # 在这个简单实现中，我们直接使用文件路径作为ID
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    return os.path.join(base_dir, file_id)


def get_file_info(
    path: str, file_id: str, parent_id: Optional[str] = None
) -> FileListItem:
    """获取文件或文件夹的信息"""
    name = os.path.basename(path)
    is_dir = os.path.isdir(path)
    stats = os.stat(path)

    # 转换时间戳为datetime对象
    create_time = datetime.fromtimestamp(stats.st_ctime)
    update_time = datetime.fromtimestamp(stats.st_mtime)

    return FileListItem(
        id=file_id,
        parentId=parent_id,
        name=name,
        type="folder" if is_dir else "file",
        createTime=create_time,
        updateTime=update_time,
    )


def list_directory(
    directory: str, parent_id: Optional[str] = None, search_key: str = ""
) -> List[FileListItem]:
    """列出目录中的所有文件和文件夹"""
    result = []

    try:
        for item in os.listdir(directory):
            # 跳过隐藏文件
            if item.startswith("."):
                continue

            full_path = os.path.join(directory, item)
            relative_path = os.path.relpath(
                full_path,
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources"),
            )

            # 如果有搜索关键词，则过滤
            if search_key and search_key.lower() not in item.lower():
                continue

            # 获取文件信息
            file_info = get_file_info(full_path, relative_path, parent_id)
            result.append(file_info)
    except Exception as e:
        print(f"Error listing directory {directory}: {e}")

    return result


# API路由
@app.post("/v1/file/list", response_model=ResponseModel)
async def file_list(request: FileListRequest, token: str = Depends(verify_token)):
    """获取文件树"""
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

    # 如果指定了父目录ID，则使用该目录
    if request.parentId:
        directory = get_absolute_path(request.parentId)
        if not os.path.isdir(directory):
            return ResponseModel(
                code=404, success=False, message="指定的目录不存在", data=[]
            )
    else:
        directory = base_dir

    # 列出目录内容
    files = list_directory(directory, request.parentId, request.searchKey or "")

    return ResponseModel(data=files)


@app.get("/v1/file/content", response_model=ResponseModel)
async def file_content(id: str, token: str = Depends(verify_token)):
    """获取单个文件内容"""
    file_path = get_absolute_path(id)

    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return ResponseModel(
            code=404, success=False, message="文件不存在或是一个目录", data={}
        )

    try:
        # 读取文件内容
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return ResponseModel(data=FileContentResponse(content=content))
    except Exception as e:
        return ResponseModel(
            code=500, success=False, message=f"读取文件失败: {str(e)}", data={}
        )


@app.get("/v1/file/read", response_model=ResponseModel)
async def file_read(id: str, token: str = Depends(verify_token)):
    """获取文件阅读链接"""
    file_path = get_absolute_path(id)

    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return ResponseModel(
            code=404, success=False, message="文件不存在或是一个目录", data={}
        )

    # 在实际应用中，这里应该返回一个可以访问文件的URL
    # 这里我们简单地返回一个假URL，实际应用中可能需要生成一个临时URL或使用文件服务器
    mock_url = f"http://localhost:8000/files/{id}"

    return ResponseModel(data=FileReadResponse(url=mock_url))


@app.get("/")
async def root():
    return {"message": "FastGPT文件API服务已启动"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
