#!/bin/bash
# ============================================
# 磁盘容器占用情况分析脚本 - Linux 版本
# ============================================
# 用法: bash disk-list-usage-linux.sh <hostname|IP>
# 示例: bash disk-list-usage-linux.sh VMSALI01788572
#
# 首次使用前，请设置环境变量（添加到 ~/.bashrc 或 ~/.zshrc）:
#   export JUMP_PWD="你的固定密码"
# 然后执行: source ~/.bashrc
# ============================================

JUMPSERVER="yumeifeng@jumpserver.ops.ctripcorp.com"

# 检查参数
if [[ $# -lt 1 ]]; then
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

echo " 开始登录跳板机 "
echo " 目标主机: $TARGET_HOST"
echo " 跳板机: $JUMPSERVER"


# 拼接完整密码: 固定密码 + 空格 + 验证码
FULL_PWD="${JUMP_PWD} ${MFA_CODE}"
# echo $FULL_PWD

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
puts \"\n 执行: 查看宿主机磁盘占用情况(只读操作)\"
puts \"----------------------------------------\"
send \"cd /var/lib/docker/overlay2 && du -shc * | egrep -E '(G|T)' \\r\"

expect {
    -re {\\$\s*\$|#\s*\$} {}
    timeout { puts \"命令超时\" }
}




puts \"\n 退出root...\"
send \"exit\r\"

puts \"\n 退出...\"
send \"exit\r\"

expect {
    \"Opt>\" { send \"q\r\" }
    eof {}
    timeout {}
}

expect eof
"


exit 0
