"""
校验工具
"""
import os

from pathlib import Path
from django.conf import settings
from typing import Tuple,Optional
from qiniu import Auth, put_file


class ImageTool:
    """
    图片工具类
    """

    @staticmethod
    def is_allowed_image(filename: str)-> Tuple[bool, Optional[str]]:
        # 1.预处理图片后缀
        ext = Path(filename).suffix.lower()
        if not ext:
            return False, "无法识别文件扩展名"

        # 2.检查是否添加了图片格式的限制
        if not settings.ALLOWED_IMAGE_EXTENSIONS:
            return True, ext

        # 3.检查是否在图片格式限制内
        if ext in settings.ALLOWED_IMAGE_EXTENSIONS:
            return True, ext

        return False, "文件格式不允许"

    @staticmethod
    def upload_to_qiniu(local_file_path: str, filename: str) -> Tuple[bool, Optional[str]]:
        try:
            # 获取七牛云配置
            qiniu_config = settings.BUCKET_CONFIG.get('qiniu')
            if not qiniu_config:
                error_msg = "未配置七牛云存储（BUCKET_CONFIG.qiniu 缺失）"
                # logger.error(error_msg)
                return False, error_msg

            # 校验必要字段
            required_keys = ['access_key', 'secret_key', 'bucket_name', 'bucket_domain']
            for key in required_keys:
                if not qiniu_config.get(key):
                    error_msg = f"七牛云配置缺少必要字段: {key}"
                    # logger.error(error_msg)
                    return False, error_msg

            # 构造认证对象
            _auth = Auth(qiniu_config['access_key'], qiniu_config['secret_key'])

            # 生成上传 token
            token = _auth.upload_token(qiniu_config['bucket_name'])

            # 执行上传
            ret, info = put_file(token, filename, local_file_path)

            # 判断上传结果
            if info.status_code == 200 and ret:
                upload_url = f"https://{qiniu_config['bucket_domain']}/{ret['key']}"
                return True, upload_url
            else:
                error_detail = getattr(info, 'error', '未知错误')
                error_msg = f"七牛云上传失败: 状态码={info.status_code}, 错误={error_detail}"
                # logger.error(error_msg)
                return False, error_msg

        except FileNotFoundError:
            error_msg = f"本地文件不存在: {local_file_path}"
            # logger.error(error_msg)
            return False, error_msg

        except Exception as e:
            error_msg = f"上传过程中发生异常: {str(e)}"
            # logger.exception("七牛云上传异常堆栈")  # 记录完整 traceback
            return False, error_msg