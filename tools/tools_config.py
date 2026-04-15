##定义agent能使用的工具
from .model_tools import (
    confirm_dangerous_action,
    request_mfa_code,
    clean_container_disk_cache,
    collect_host_disk_info,
)
TOOLS=[
     {
        "type": "function",
        "name": "confirm_dangerous_action",
        "description": "在执行可能影响系统的操作前进行确认。大模型应该在执行以下操作前调用此工具：1) 需要登录宿主机执行的操作 2) 会修改系统状态的操作（删除、清理等） 3) 需要特殊权限的操作。获得用户确认后，再调用实际的工具。",
        "func": confirm_dangerous_action,
        "parameters": {
            "type": "object",
            "properties": {
                "action_description": {
                    "type": "string",
                    "description": "操作的简短描述，如'清理Docker缓存'、'通知业务方'"
                },
                "details": {
                    "type": "string",
                    "description": "详细信息，如要操作的主机名、预期影响等。可选。"
                }
            },
            "required": ["action_description"]
        }
    },
    {
        "type": "function",
        "func": request_mfa_code,
        "name": "request_mfa_code",
        "description": "Request user MFA code (valid for 60s)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
        
    },
    {
        "type": "function",
        "func": clean_container_disk_cache,
        "name": "clean_container_disk_cache",                    # ✅ 必须：字母数字和下划线，最多64字符
        "description": "该方法需要获取MFA码。清理容器内部缓存目录",
        "parameters": {
            "type": "object",
            "properties": {
                "host_name": {
                    "type": "string",
                    "description": "容器ID"
                }
            },
            "required": ["host_name"]
        }
        
    },
    {
        "type": "function",
        "func": collect_host_disk_info,
        "name": "collect_host_disk_info",
        "description": "该方法需要获取MFA码。采集宿主机磁盘使用相关信息，包括整体磁盘使用情况以及磁盘的overlay2被业务容器占用的情况。pod overlay2仅采集磁盘占用量在10G以上且排名前5的容器。",
        "parameters": {
            "type": "object",
            "properties": {
                "host_name": {
                    "type": "string",
                    "description": "宿主机名称"
                }
            },
            "required": ["host_name"]
        }
    
    },
]