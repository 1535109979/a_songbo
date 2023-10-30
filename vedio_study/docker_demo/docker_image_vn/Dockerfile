##############################################
# 基于 opencloudos9.0_py3.10 构建 vn 运行环境
##############################################

#FROM os_linux_python310:base
FROM vnpy:req33

# 标签信息
LABEL group_name=BYT

## 复制依赖文件
COPY add_requirements.txt requirements.txt

# 安装 VN 以及相关依赖
RUN set -ex \
    && pip3 install --no-cache-dir -r requirements.txt
