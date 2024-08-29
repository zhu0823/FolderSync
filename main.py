import logging
import os
import shutil
from datetime import datetime
from pytz import timezone
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def is_running_in_docker():
    """判断当前程序是否在 Docker 容器中运行"""
    # 检查是否存在 .dockerenv 文件
    if os.path.exists('/.dockerenv'):
        return True
    # 检查 /proc/1/cgroup 文件内容
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read()
    except FileNotFoundError:
        return False


# 根据运行环境设置目录
if is_running_in_docker():
    UPLOAD_DIR = Path("/data")
    LOG_DIR = Path("/logs")
else:
    UPLOAD_DIR = Path("./data")
    LOG_DIR = Path("./logs")

# 东8区的时区
tz = timezone('Asia/Shanghai')


class CustomFormatter(logging.Formatter):
    """自定义日志格式化器，将时间转换为东8区"""

    def formatTime(self, record, formatter=None):
        # 获取记录的时间戳并转换为东8区时间
        dt = datetime.fromtimestamp(record.created, tz)
        if formatter:
            return dt.strftime(formatter)
        else:
            return dt.isoformat()


# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志记录
LOG_FILE = LOG_DIR / "upload.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# 创建日志处理器，并应用自定义格式化器
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(CustomFormatter("%(asctime)s - %(message)s"))
logging.getLogger().handlers = [handler]


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 确保目录存在
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # 定义文件路径
        file_path = UPLOAD_DIR / file.filename
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 记录日志
        logging.info(f"上传成功: {file.filename}")

        return JSONResponse(content={"code": 200, "data": file.filename, "msg": "upload success!"})
    except Exception as e:
        logging.error(f"上传失败: {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18000)
