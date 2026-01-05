# 项目说明

## 版本信息
```shell
Python 3.12.10
Django 5.0.7
```

## 项目运行
```shell
# 创建虚拟环境
uv venv --python 3.12 <虚拟环境名称或路径>
# 激活虚拟环境
<虚拟环境名称或路径>\Scripts\Activate.ps1
# 安装环境依赖
pip install -r requirements.txt
# 生成迁移文件
python manage.py migrate
# 创建索引字段
python manage.py rebuild_index
```