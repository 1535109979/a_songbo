##############################################
# 基于 opencloudos9.0 构建 python3.10.5 运行环境
##############################################

FROM opencloudos/opencloudos:9.0

# 标签信息
LABEL group_name=BYT-OS

# 环境变量
ENV LANG=en_US.utf8 \
    LANGUAGE=zh_CN.UTF-8 \
    TZ=Asia/Shanghai \
    PYTHON_VERSION=3.10.5

# 复制 pip 配置
COPY pip.conf /etc/pip.conf

# 安装系统依赖
RUN set -ex \
    # 安装所需组件
    && dnf install -y libxkbcommon-devel libglvnd-devel libffi-devel zlib-devel bzip2-devel openssl-devel ncurses-devel readline-devel tk-devel \
    && dnf install -y make initscripts gcc gcc-c++ m4 gmp-devel.x86_64 \
    # 安装常用工具
    && dnf install -y wget tar vim less tree iproute dmidecode hostname htop telnet traceroute \
    # 安装python相关依赖
    && dnf install -y sqlite* python3-pip deltarpm python3-devel \
    # 修改系统时区为东八区
    && rm -rf /etc/localtime && ln -s /usr/share/zoneinfo/${TZ} /etc/localtime \
    && touch ~/.bashrc && echo 'alias ll="ls -lsatrh"' >> ~/.bashrc && source ~/.bashrc \
    && dnf clean all

# 安装 TA-Lib (必须在 python install ta-lib 之前安装，
# 否则报错 :: talib/_ta_lib.c:747:10: fatal error_old: ta-lib/ta_defs.h: 没有那个文件或目录)
RUN set -ex \
    && cd /opt \
    && wget --progress bar:force http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib && ./configure --prefix=/usr/local \
    && make && make install && make clean \
    && rm -rf /opt/ta-lib*.gz

# 设置系统字符集
ENV PATH=/usr/local/python3/bin:$PATH
