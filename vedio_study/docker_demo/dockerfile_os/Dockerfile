##############################################
# 基于 opencloudos9.0 构建 python3.11 运行环境
##############################################

FROM opencloudos/opencloudos:9.0

# 标签信息
LABEL group_name=BYT-OS

# 环境变量
ENV LANG=en_US.utf8 \
    LANGUAGE=zh_CN.UTF-8 \
    TZ=Asia/Shanghai \
    PYTHON_VERSION=3.11

# 复制 pip 配置
COPY pip.conf /etc/pip.conf

# 安装系统依赖
RUN set -ex \
    && dnf update -y \
    && dnf makecache \
    # 安装所需组件
    && dnf install -y libxkbcommon-devel libglvnd-devel libffi-devel zlib-devel bzip2-devel \
    && dnf install -y openssl-devel ncurses-devel readline-devel tk-devel \
    && dnf install -y make initscripts gcc gcc-c++ m4 gmp-devel.x86_64 \
    # 安装常用工具
    && dnf install -y wget tar xz vim less tree iproute dmidecode hostname telnet traceroute \
    && dnf install -y git sqlite* \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime \
    && ln -svf /usr/share/zoneinfo/${TZ} /etc/localtime \
    && touch ~/.bashrc && echo 'alias ll="ls -lsatrh"' >> ~/.bashrc && source ~/.bashrc \
    # 安装python相关依赖
    && dnf install -y python${PYTHON_VERSION}-pip python3-devel \
    && ln -svf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    && ln -svf /usr/bin/python${PYTHON_VERSION} /usr/bin/python \
    && python3 -m pip install --upgrade pip \
    && cd /usr/local/lib/python${PYTHON_VERSION}/site-packages \
    && ln -svf /usr/local/lib/python${PYTHON_VERSION}/site-packages /byt_pub \
    && dnf clean all

# 安装 TA-Lib (必须在 python install ta-lib 之前安装，
# 否则报错 :: talib/_ta_lib.c:747:10: fatal error: ta-lib/ta_defs.h: 没有那个文件或目录)
RUN set -ex \
    && cd /opt \
    && wget --progress bar:force http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib && ./configure --prefix=/usr/local \
    && make && make install && make clean \
    && rm -rf /opt/ta-lib-* \
    && pip3 list

# 设置系统字符集
ENV PATH=/usr/local/python3/bin:$PATH