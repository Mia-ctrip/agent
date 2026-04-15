#!/bin/bash
# ============================================
# Docker Overlay 容器映射查询脚本 - Linux 版本
# ============================================
# 用法: bash disk-overlay-mapping-linux.sh <hostname|IP>
# 示例: bash disk-overlay-mapping-linux.sh VMSALI01788572
#
# 功能: 查询宿主机上所有运行中容器的 overlayId 与 Pod 名称的映射关系
#
# 首次使用前，请设置环境变量（添加到 ~/.bashrc 或 ~/.zshrc）:
#   export JUMP_PWD="你的固定密码"
# 然后执行: source ~/.bashrc
# ============================================

JUMPSERVER="yumeifeng@jumpserver.ops.ctripcorp.com"

# 检查参数
if [[ $# -lt 1 ]]; then
    echo "ERROR: 缺少目标主机参数"
    echo "用法: bash disk-overlay-mapping-linux.sh <hostname|IP>"
    echo "示例: bash disk-overlay-mapping-linux.sh VMSALI01788572"
    exit 1
fi

TARGET_HOST=$1

# 检查 expect 是否安装
if ! command -v expect &> /dev/null; then
    echo "ERROR: expect not installed"
    exit 1
fi

# 检查密码环境变量
if [[ -z "$JUMP_PWD" ]]; then
    echo "ERROR: JUMP_PWD not set"
    exit 1
fi

echo "=========================================="
echo " 开始登录跳板机获取容器映射信息"
echo "=========================================="
echo " 目标主机: $TARGET_HOST"
echo " 跳板机: $JUMPSERVER"
echo ""

# 拼接完整密码: 固定密码 + 空格 + 验证码
FULL_PWD="${JUMP_PWD} ${MFA_CODE}"

# 使用 expect 处理交互
expect -c "
set timeout 120
set full_password \"$FULL_PWD\"
log_user 0

puts \" 正在连接堡垒机...\"
spawn ssh -t $JUMPSERVER

expect {
    \"password:\" {
        send \"\$full_password\r\"
        exp_continue
    }
    \"Opt>\" {
        log_user 1
        puts \"\n 已登录堡垒机\"
        puts \" 正在连接目标主机: $TARGET_HOST\"
        sleep 1
        send \"$TARGET_HOST\r\"
    }
    timeout {
        puts \"\n 连接堡垒机超时\"
        exit 1
    }
}

# 等待主机列表显示和 ID> 提示符
expect {
    \"ID>\" {
        puts \"\n 选择登录用户: 2 (powerop)\"
        send \"2\r\"
    }
    -re {\\\$\\s*\$|#\\s*\$} {
        puts \"\n 已连接到目标主机\"
    }
    timeout {
        puts \"\n 等待响应超时\"
        exit 1
    }
}

# 等待连接到目标主机 shell
expect {
    -re {\\\$\\s*\$|#\\s*\$} {
        puts \"\n 已连接到目标主机\"
    }
    timeout {
        puts \"\n 连接目标主机超时\"
        exit 1
    }
}

puts \"\n 切换root用户执行\"
puts \"----------------------------------------\"
send \"sudo -i\r\"
expect {
    -re {\\\$\\s*\$|#\\s*\$} {}
    timeout { puts \" df 命令超时\" }
}


puts \"\"
puts \"\n 执行: 查询 Docker Overlay 容器映射\"
puts \"----------------------------------------\"
send \"docker ps -q | xargs docker inspect --format '{{.Name}} {{.GraphDriver.Data.MergedDir}}'\r\"

expect {
    -re {#\\s*\$} {
        puts \"\n 查询完成\"
    }
    timeout { puts \"\n 查询超时\" }
}

puts \"\n 退出...\"
send \"exit\r\"

expect {
    \"Opt>\" { send \"q\r\" }
    eof {}
    timeout {}
}

expect eof
"

exit_code=$?

if [[ $exit_code -eq 0 ]]; then
    echo ""
    echo "✅ 成功获取容器映射信息"
else
    echo ""
    echo "❌ 查询失败，错误代码: $exit_code"
fi

exit $exit_code
