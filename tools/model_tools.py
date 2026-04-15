# -*- coding: utf-8 -*-
import subprocess
import os
import re
import json
from typing import List, Dict

# -*- coding: utf-8 -*-
import pexpect
import os
import sys

# Set UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

#模型调用工具的实现
def request_mfa_code() -> Dict[str, str]:
    """请求用户输入MFA验证码（60秒有效期）
    
    Returns:
        包含MFA码和过期时间提示的字典
    """
    print("\n⚠️  需要MFA验证码（有效期60秒）")
    mfa_code = input("请输入MFA验证码: ").strip()
    os.environ['MFA_CODE'] = mfa_code
    print("\获取MFA验证码结束")
    if not mfa_code:
        return {
            "success": False,
            "mfa_code": "",
            "message": "未输入MFA码"
        }
    
    return {
        "success": True,
        "mfa_code": mfa_code,
        "message": f"已获取MFA码，请在60秒内执行清理操作"
    }

##
def confirm_dangerous_action(action_description: str, details: str = "") -> Dict[str, any]:
    """在执行有实际影响的操作前进行确认

    这个函数用于：
    - 需要登录宿主机执行的操作
    - 会修改系统状态的操作（删除、清理等）
    - 需要特殊权限的操作

    Args:
        action_description: 操作的简短描述（如"清理Docker缓存"）
        details: 详细信息（如要操作的主机名、预期影响等）

    Returns:
        包含用户确认结果的字典
    """
    print("\n" + "="*60)
    print("⚠️  即将执行可能影响系统的操作")
    print("="*60)
    print(f"操作类型: {action_description}")
    if details:
        print(f"操作详情:\n{details}")
    print("-"*60)

    # 获取用户确认
    user_input = input("是否继续? (yes/no): ").strip().lower()

    if user_input in ['yes', 'y']:
        return {
            "confirmed": True,
            "action": action_description,
            "message": "用户已确认，操作继续执行"
        }
    else:
        return {
            "confirmed": False,
            "action": action_description,
            "message": "用户已取消操作"
        }
  

def clean_container_disk_cache(host_name: str) -> str:
    """清理容器内部缓存目录
    
    Args:
        host_name: 宿主机名称
    
    Returns:
        清理结果及docker prune的输出分析
    """
    script_path = "/home/octopus/work/mcp-test/scripts/disk-cleanup-linux.sh"
    
    os.environ['JUMP_PWD'] = "Mars19980729wu!"
    
    result = subprocess.run(
        ["bash", script_path, host_name],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ
    )
    
    script_output = result.stdout or ""
    script_error = result.stderr or ""
    full_output = script_output + ("\n" + script_error if script_error else "")

    if result.returncode == 0:
       return f" 清理成功\n{full_output}"
    else:
       return f" 清理失败\n{full_output if full_output else f'返回码: {result.returncode}'}"


def collect_host_disk_info(host_name: str) -> str:
    """Run disk-list-usage-linux.sh and return raw output for LLM analysis."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "scripts", "disk-list-usage-linux.sh")
    )

    os.environ['JUMP_PWD'] = "Mars19980729wu!"

    result = subprocess.Popen(
        ["bash", script_path, host_name],
        text=True,
        stderr=subprocess.STDOUT,  # 合并stderr到stdout
        env=os.environ
    )

    stdout = result.stdout or ""
    stderr = result.stderr or ""
    full_output = stdout + ("\n" + stderr if stderr else "")

    if result.returncode == 0:
        return full_output
    return json.dumps({"success": False, "error": full_output}, ensure_ascii=False)




# ============================================================
# 测试使用
# ============================================================

    
if __name__ == "__main__":
    #测试 传参作为host
    host = "VMSALI01866068"
    #confirm_dangerous_action("是否同意执行docker system prune -f -a这个清理宿主机缓存的指令？")
    #print(f"开始清理宿主机 {host} 上的容器磁盘缓存...")
    print(f"开始查询宿主机的磁盘使用情况")
    mfa_code = request_mfa_code()
    #output = collect_host_disk_info(host)
    output = clean_container_disk_cache(host)
    print(output)
    #print("清理结果:")
    #print(output)    

    #result = get_overlay2_usage("VMSALI01788572")
    #print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 输出示例：
    # {
    #   "success": true,
    #   "data": [
    #     {"size": "50G", "path": "abc123def456..."},
    #     {"size": "20G", "path": "def456ghi789..."},
    #     {"size": "15G", "path": "ghi789jkl012..."}
    #   ],
    #   "message": "✅ 成功获取 3 个大于等于 10G 的缓存"
    # } 

