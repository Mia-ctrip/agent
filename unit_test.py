from gpu_agent import run_agent
from test_gpu_agent import base_chat
import os


## 重要须知 经验教训：
## 执行agent的机器 在通过expect登录跳板机前必须先手动通过ssh指令登陆一次来鉴权
# The authenticity of host 'jumpserver.ops.ctripcorp.com (10.62.135.7)' can't be established.
# RSA key fingerprint is SHA256:3PdsEwHwI+e52V340dEYOklirAnGNOHYfuGSy/JV4uQ.
# This key is not known by any other names
# Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
# Warning: Permanently added 'jumpserver.ops.ctripcorp.com' (RSA) to the list of known hosts.
# run_agent(
#     "VMSALI01774663"
# )
messages = [
     {"role": "system", "content": "你是一个精通GPU 操作系统和k8s docker的运维专家，尤其精通操作系统下存储相关的分析。查看宿主机上存储使用情况时需要先获取MFA令牌才能登录宿主机。"},
     {"role": "user", "content": '''请帮忙查看VMSALI01326242这台机器上的磁盘使用（docker/overlay）情况，根据du指令返回的结果分析出磁盘占用超过了5G的前5的overylay的container ID(如果超过5G的overlay不满5个仅返回大于5G的即可，如果超过了5个仅返回5个即可), 并返回给我这些container ID及对应的使用磁盘大小。
     返回的结果以这样的样式给我:
     [
        {
            "overlay_id":"xxxxxxxxx",
            "disk_usage:"20G"
        },
        {
            "overlay_id":"xxxxxxxx",
            "disk_usage:"11G"
        }
     ]
     这是执行的结果:已连接到目标主机

 切换root用户执行
----------------------------------------
sudo -i
-bash: PROMPT_COMMAND: readonly variable
[root@VMSALI01326242 ~]# 

 执行: 查看宿主机磁盘占用情况(只读操作)
----------------------------------------
cd /var/lib/docker/overlay2 && du -shc * | egrep -E '(G|T)' 
3.6G    066206be70f2d00466fe4833213b2ef1c1ca31022b5e7776b91bdc269be395ee
6.4G    07e3a996f5348ed6c5bb0d004f36b6dc5dfdcb4d4bd174c341022d4b6a61cf6a
4.4G    095c312eb389fa5909fa34b4339a16be493a1b74a2b8faaef50641d32a399298
5.6G    0ba12af51f79437533f1ca813a1e85cc8f0fe554b9dc48bce08e3ca54c5a9211
1.3G    0d1d18593a1b1be2e04e31d04ccba64e2e05862f83cb4b9de006b712e47e1125
7.8G    1091d50b2a62add083d61a1c0b7c11e6aacf4b0bfb6ff0a75fb5b7ebdf634b1d
4.1G    13c4c51de596c100642569fe654bca986380416dd6d97ef16452296ee738d0d8
6.3G    142017fc792ab4f1196582963a6b285cc70b7822973847ea87d666a0588436c3
1.1G    146c3fcea120d118a7fc0728ce1a24aa9d49441ebc9a02d3a324055fe8e66e20
1.8G    196f35c14aa99baa131c94efee9f47a478e73551f9e70e479c019a6f5c597cf1
4.6G    1d6363ef4c871c283332044be21637aa93878c284c0395636aadf6f658d49a75
5.2G    289c5b66de17443e65cf05c6f012af0438c60e489b61dc015bed1ae353bfe8be
2.4G    2aab1624bceb63135b9bad079d93a2a2d2a1b2e0a612113cdd9ae5f7c68d3776
2.1G    2b700829e0e2975aacd8baa3010e8c6696aa88a6f44c4c544f85718f994ca810
35G     2bca0239f3a96e9f9119775dd9fc98c62f582aba73cd751430738f69a96f3257
4.6G    2cce7a9d713689f753a7afcdcda5618eece1235884713eef5cd4c9ec4691b11b
1.5G    2eb02c160f1e33a6e5079acd23c101795bf40ca0a47d1b60eecffe4001912dac
36G     2f7397bafa000bb4017dbf314541693a769762861c1070eb4c00fac7cc95dbad
6.4G    32541068e525eaef43d908f3808486a7ca85ac21a9aea3846e50ea55a5ffb0be
6.1G    468991e433bcb3aab2cbb3a455ae43ca7e24bb68100747959d907254c1b42e27
1.5G    51d1e66147e17915f25cf25f08ddce8753b8836d28781b7f1661ca900c57ec88
1.5G    587e3d9b907e13dea66ed83ce72c7be2156439e16f22011173aca64cd18ed558
2.0G    653583c592922b200337b82d356622ad4397b1446243ca6ef06445ad1a47c909
4.3G    68c031e37645abbef520da968d7b43501f3eeaa997315096bd0ab9c766a5564e
4.9G    6b30ff2c5eb5aad4ddd483eca7d6a0ac6698d225366fca4b7147ccea06b6cc1f
1.5G    7d6327e1b5c6e145635b10987a2bba1abe7b8676c87074a0e090555e6fc6e460
4.4G    82629490a8b8734a74638011431951d4f77756b61dd136d5fbe8d52df4b974a2
2.5G    8cb5b64e218095a7b5f9a7f6ed1694b8f0eb7154facc5e8a0aaa7e3ee8786838
2.4G    908f5ebb8b0881630a4261a1c619a9590b50f2f54b7f4bcafa63a1386f17b048
1.8G    96cbec9d072b2808ff41f11dfb41ccb2b1aedc1bb4d3690c03fc2fb98363cf2c
4.4G    9934ed436e3bf83cfd433dae9e689cc948f025811255b9e72ba0ce8a8fdf996c
1.6G    9f10610d954e33377cc1cb5886e756f31ef52e9a360162569773e35773a9d847
3.1G    ac5b296a6c53dfa02bc511eebf373ad50c0df320d809d8419750738a9138a7c6
1.7G    b2b891fff2dac84623a3e1bec216d080fe8a543a9daa107d42c027366eea75d4
4.3G    c73a1e8ab197697ee05359027fe60f594ad86741d85ccf0a4eed4973c5c7b21b
6.2G    cf0bb6679d94cfa99e0b5a571f7cff1c076f5e7407f2450163963c83b4e98717
1.1G    cff176ab8a1d89f404b6cae75fa46b8082b5b260a9ebbc47c55cb439e41536d8
4.9G    e84585cd70cc24b6050512c95a282e682098b64ab10399c6bef0f5f737e58e6b
1.2G    ee0a9ef3859751cefe3a87fe2439f5d21f4ed83a307c8e1e1ed17ed58cb996ae
7.0G    f20902568071f12aeccaa806f706e70bc551c6df9f874b330bcb9ed51ca541dc
253G    tota'''}
]
#print(base_chat(messages))

messages_disk = [
     {"role": "system", "content": '''
     你是一个精通GPU 操作系统和k8s docker的运维专家，尤其精通操作系统下存储相关的分析。查看宿主机上存储使用情况时需要先获取MFA令牌才能登录宿主机。
     关键知识：1. Kubernetes 自动生成的容器命名规则是k8s_{容器名}_{Pod名}_{命名空间}_{Pod UID}_{重启次数},如果你想获取pod名，取第三个字段；
     2. overlay所处目录是/var/lib/docker/overlay2/，某个overlay的全路径是/var/lib/docker/overlay2/xxxxxx
     3. 并不是所有overlay2都可以匹配到对应的pod的，因为pod可能消亡了并不存在了，但是写到磁盘的数据还在，如果找不到对应的pod，用null填充也可以。
     '''},
     {"role": "user", "content": '''
        我会给你两份数据，一份是宿主机上使用磁盘大于5G的overlay列表，一份运行了指令<docker ps -q | xargs docker inspect --format '{{.Name}} {{.GraphDriver.Data.MergedDir}}'>之后获得的宿主机上运行的所有docker容器和对应的容器名。
        我要求你先帮我提取运行docker ps之后得到的结果中docker的pod名和overlay的对应关系，再帮我从所有overlay中筛选出我给你的磁盘大于5G的overlay列表中的那些overlay，最后输出筛选过后的overlay和pod名的对应关系，返回的结果以这样的样式给我:
     [
        {
            "overlay_id":"xxxxxxxxx",
            "disk_usage:"20G",
            "pod_name":"xxx"
        },
        {
            "overlay_id":"xxxxxxxx",
            "disk_usage:"11G",
            "pod_name":"xxx"
        },
        ....
     ]
     所以最终我给你的overlay列表元素有多少个，你给的结果也有多少元素，输出的结果是在overlay列表的基础上参考运行脚本返回，添加上pod_name而已，就这么简单。
        overlay列表：
[
    {
        "overlay_id": "2f7397bafa000bb4017dbf314541693a769762861c1070eb4c00fac7cc95dbad",
        "disk_usage": "36G"
    },
    {
        "overlay_id": "2bca0239f3a96e9f9119775dd9fc98c62f582aba73cd751430738f69a96f3257",
        "disk_usage": "35G"
    },
    {
        "overlay_id": "1091d50b2a62add083d61a1c0b7c11e6aacf4b0bfb6ff0a75fb5b7ebdf634b1d",
        "disk_usage": "7.8G"
    },
    {
        "overlay_id": "f20902568071f12aeccaa806f706e70bc551c6df9f874b330bcb9ed51ca541dc",
        "disk_usage": "7.0G"
    },
    {
        "overlay_id": "07e3a996f5348ed6c5bb0d004f36b6dc5dfdcb4d4bd174c341022d4b6a61cf6a",
        "disk_usage": "6.4G"
    }
]

        运行脚本返回：==========================================
 开始登录跳板机获取容器映射信息
==========================================
 目标主机: VMSALI01326242
 跳板机: yumeifeng@jumpserver.ops.ctripcorp.com

 正在连接堡垒机...

 已登录堡垒机
 正在连接目标主机: VMSALI01326242
Opt> VMSALI01326242
  ID    | 名称                                          | 用户名                                          
+-------+-----------------------------------------------+------------------------------------------------+
  1     | normalop                                      | normalop                                        
  2     | powerop                                       | powerop                                         

ID> 
 选择登录用户: 2 (powerop)
2
正在通过 koko 连接到 powerop@10.24.31.129 0.2

Welcome to Alibaba Cloud Elastic Compute Service !

Updates Information Summary: available
    117 Security notice(s)
         46 Important Security notice(s)
         66 Moderate Security notice(s)
          5 Low Security notice(s)
Run "dnf upgrade-minimal --security" to apply all updates.More details please refer to:
https://help.aliyun.com/document_detail/416274.html
Last login: Fri Mar 20 19:53:30 2026 from 10.62.240.143
-bash: PROMPT_COMMAND: readonly variable
[powerop@VMSALI01326242 ~]$ 
 已连接到目标主机

 切换root用户执行
----------------------------------------
sudo -i
-bash: PROMPT_COMMAND: readonly variable
[root@VMSALI01326242 ~]# 

 执行: 查询 Docker Overlay 容器映射
----------------------------------------
dDir}}'ps -q | xargs docker inspect --format '{{.Name}} {{.GraphDriver.Data.Merged
/k8s_aitraining_ocp282pronvlzafwy-tr021538-0_pro-gps_7c41531b-d746-4c96-bb9a-e8aabe1b939a_0 /var/lib/docker/overlay2/2bca0239f3a96e9f9119775dd9fc98c62f582aba73cd751430738f69a96f3257/merged
/k8s_POD_ocp282pronvlzafwy-tr021538-0_pro-gps_7c41531b-d746-4c96-bb9a-e8aabe1b939a_0 /var/lib/docker/overlay2/b02ec7a6b47dee99abb2bfd9f41a7c966927faa4247f62a919c57e1ce33c2eda/merged
/k8s_peta-exporter_peta-exporter-lwcp5_a2i-system_71cc8cde-a914-4dd0-9627-51e026b110e4_0 /var/lib/docker/overlay2/1515a8511a5261dddd6ba5358c5b7e21655031e96bd6dff5b53b12fd6c94032c/merged
/k8s_POD_peta-exporter-lwcp5_a2i-system_71cc8cde-a914-4dd0-9627-51e026b110e4_0 /var/lib/docker/overlay2/050d6cdc75508e9d0ad138b810e38eb014f41369bb4b8c30de8e2cb83c73e563/merged
/cilium-sidecar /var/lib/docker/overlay2/445de9375126eb5176e013b9b183be1dd736adbaa31f6f6510437be5ab9df210/merged
/cilium-agent /var/lib/docker/overlay2/1c01dd288051958175d1883f43599067054178f5f3033763bdfcb7df8d9ef165/merged
/k8s_nvidia-device-plugin-ctr_nvidia-device-plugin-daemonset-1.12-66vrp_a2i-system_7b33a37b-953c-4da1-af93-5f398fc8d450_0 /var/lib/docker/overlay2/34999e92f2b60d86675cd1e63f14d0846268fbfe15b7e21e56023594d87c9bb8/merged
/k8s_POD_nvidia-device-plugin-daemonset-1.12-66vrp_a2i-system_7b33a37b-953c-4da1-af93-5f398fc8d450_0 /var/lib/docker/overlay2/3989260cd404f1c7b077317b428e0fc308c21c9e04e7b0897565db9094a494d7/merged
/k8s_dcgm-exporter_dcgm-exporter-5w4jf_a2i-system_8637d011-1a40-4844-b500-c204917feafe_0 /var/lib/docker/overlay2/3da486a4036c8e722dccadfb3e0aa7d0de4a29ae3508f33c8929e018c0293d19/merged
/k8s_POD_dcgm-exporter-5w4jf_a2i-system_8637d011-1a40-4844-b500-c204917feafe_0 /var/lib/docker/overlay2/63ca523a3c22da35906a95126b222552e1cb7e2e7f6a18f338ccdcf4fb4831f0/merged
/k8s_sidecar-textfile_node-exporter-m74b4_node-exporter_6c683ac7-73da-453c-b74b-f6debac2f69c_0 /var/lib/docker/overlay2/dd2d0fe5536ba64f96e744e0f4371bcbfa2b8b6a052e43cb40a80a78ccd90826/merged
/k8s_main_node-exporter-m74b4_node-exporter_6c683ac7-73da-453c-b74b-f6debac2f69c_0 /var/lib/docker/overlay2/59b78b868fd641e858508b1c611bd74d39cae88cc168a5dce542e72ab0023106/merged
/k8s_POD_node-exporter-m74b4_node-exporter_6c683ac7-73da-453c-b74b-f6debac2f69c_0 /var/lib/docker/overlay2/ce43d9ea13b1673f5525464a4ea5341bc2f1ac484a0cef758017f5097270b50b/merged
/k8s_chaosblade-tool_chaosblade-tool-q7bvd_chaosblade_79164b57-5c7c-42ec-a162-1e733b7948df_0 /var/lib/docker/overlay2/4d555f4a005da91dc25c47b39cbaffa17205528f52f3443bfcaf7d09fb036647/merged
/k8s_POD_chaosblade-tool-q7bvd_chaosblade_79164b57-5c7c-42ec-a162-1e733b7948df_0 /var/lib/docker/overlay2/af837aaf8042348ad2eea2bbf8d153e70c249c1d97f6481ff1bb2cc4e0ca45cd/merged
/k8s_liveness-probe_juicefs-csi-node-h5m25_juicefs-system_08863d89-b797-410c-9b8a-e8c2ea2b016e_0 /var/lib/docker/overlay2/913878f3ad3e8acb1b8a8d10a4c0a58bad6c7a814500f460243c848bdae79dcb/merged
/k8s_node-driver-registrar_juicefs-csi-node-h5m25_juicefs-system_08863d89-b797-410c-9b8a-e8c2ea2b016e_0 /var/lib/docker/overlay2/a188e15472da92c0da987681e84b38474edc739048c18775b026f40f997bae32/merged
/k8s_juicefs-plugin_juicefs-csi-node-h5m25_juicefs-system_08863d89-b797-410c-9b8a-e8c2ea2b016e_0 /var/lib/docker/overlay2/87cbe059992d8e4d266a84308962ae10e2a0240398950e41abb87244860536e8/merged
/k8s_POD_juicefs-csi-node-h5m25_juicefs-system_08863d89-b797-410c-9b8a-e8c2ea2b016e_0 /var/lib/docker/overlay2/8f9e2afc54e2755d48da44aae26e0051463ec93944b2c753f6e4373c94846471/merged
/k8s_filebeat-daemonset_filebeat-daemonset-9jvzx_klog_d704e6dc-74c7-4c62-aef5-7177b8bb5fb3_0 /var/lib/docker/overlay2/5bee1879ff0f695c36e5fd423f412eb192f6c26de3366ff3125daae664e8edc2/merged
/k8s_POD_filebeat-daemonset-9jvzx_klog_d704e6dc-74c7-4c62-aef5-7177b8bb5fb3_0 /var/lib/docker/overlay2/14e998114e3648be40e720078a8361b37b0bc4d38d1451515acee2e495b6f50b/merged
/k8s_nas-driver-registrar_csi-plugin-jqz2x_kube-system_1d27608b-4040-4f07-bcbf-5c5c486d1317_0 /var/lib/docker/overlay2/d80a41ac80891fb7286ac977d823ba2670d44d2b4be8c61a01759e82807d0121/merged
/k8s_disk-driver-registrar_csi-plugin-jqz2x_kube-system_1d27608b-4040-4f07-bcbf-5c5c486d1317_0 /var/lib/docker/overlay2/bb15e5dce0bbbe804eb09e09806519d2fe90b0856afc3ddb388347ba238ed793/merged
/k8s_csi-plugin_csi-plugin-jqz2x_kube-system_1d27608b-4040-4f07-bcbf-5c5c486d1317_0 /var/lib/docker/overlay2/44a2ae475685d3c589f0ec28226bf106fabdca4478e8e410c12d1e743f110225/merged
/k8s_POD_csi-plugin-jqz2x_kube-system_1d27608b-4040-4f07-bcbf-5c5c486d1317_0 /var/lib/docker/overlay2/05de3bc5ef93d27c661767cfa692467366dfc5327e10e5de2114e9cfe8ddd070/merged
/k8s_aitraining_ocpproatpaejii-tr049596-0_pro-gps_b59f2a2e-98a2-4248-a519-808f09d7ebb9_0 /var/lib/docker/overlay2/2f7397bafa000bb4017dbf314541693a769762861c1070eb4c00fac7cc95dbad/merged
/k8s_POD_ocpproatpaejii-tr049596-0_pro-gps_b59f2a2e-98a2-4248-a519-808f09d7ebb9_0 /var/lib/docker/overlay2/f62eef231ad4873124cfa8483c9080e74e737f671b7d4bbfc8ff57c598dfe208/merged
/k8s_jfs-mount_juicefs-vmsali01326242-vacation-ai-pv-rlibhx_juicefs-system_b5644374-d9bf-475c-b693-844dbb66fc37_0 /var/lib/docker/overlay2/09f9331da6d0650cefdf07933bf294639018a8b6b375fd963707979346d657c9/merged
/k8s_POD_juicefs-vmsali01326242-vacation-ai-pv-rlibhx_juicefs-system_b5644374-d9bf-475c-b693-844dbb66fc37_0 /var/lib/docker/overlay2/bccf8c98869ac32d84073a7dfce74d75b2fce00b761dfceb78703662d332a35f/merged
/k8s_beacon_beacon-wdtnr_observability_86f5da3e-b84a-4cda-ac5e-ff65e1cc971f_0 /var/lib/docker/overlay2/e5ef6e9668adc4d4976c591234b630b5564d10f3e44716cb6b2c14a9cbe4f4e2/merged
/k8s_POD_beacon-wdtnr_observability_86f5da3e-b84a-4cda-ac5e-ff65e1cc971f_0 /var/lib/docker/overlay2/eb9d1bd62b33efa0cf8839a86c785901c6510b7d51f7950c4338209c328a2bef/merged
/k8s_kruise-daemon_kruise-daemon-vc7t2_kruise-system_ea925fb8-ea0a-4c55-bb44-3efa2279ce37_0 /var/lib/docker/overlay2/de77aae0645cb7ecfcc9370c07e0de4bba943cdca2576c8c1a4be94f84cf79b3/merged
/k8s_POD_kruise-daemon-vc7t2_kruise-system_ea925fb8-ea0a-4c55-bb44-3efa2279ce37_0 /var/lib/docker/overlay2/45a245b47dac4a3c3b91bd28020d831dcb188dd0961b6bf1071952243cabc28e/merged
/k8s_node-problem-detector_node-problem-detector-n4njd_kube-system_4a73c446-5ff2-4295-9c4f-2106a95016fa_2 /var/lib/docker/overlay2/1942504cb5fc6d511bb6e7f144c10f34ea7b9d627b0f9caad015d8e47e84ccda/merged
/k8s_POD_node-problem-detector-n4njd_kube-system_4a73c446-5ff2-4295-9c4f-2106a95016fa_0 /var/lib/docker/overlay2/cd58940263c9a22f5b4a6c00a390d9a2e3ad1965ed4ea99d04766eead7f8ccdb/merged
/k8s_main_ip-device-plugin-daemonset-hjb4m_kube-system_b840dd13-528c-406e-8c23-cd5da0e4d26b_0 /var/lib/docker/overlay2/aea2ae5781cb8f3ca9be93b404ffaa5a01494ddc3442a89525a91a2578754558/merged
/k8s_POD_ip-device-plugin-daemonset-hjb4m_kube-system_b840dd13-528c-406e-8c23-cd5da0e4d26b_0 /var/lib/docker/overlay2/268deb208ef9bdb5afe71f74569958c03bbd3fb2381a7f4e9b652362ac8ff76f/merged
[root@VMSALI01326242 ~]# 
 查询完成

 退出...
exit
logout
     '''}
]

#print(base_chat(messages_disk))

messages_prune = [
     {"role": "system", "content":'''你是一个精通GPU 操作系统和k8s docker的运维专家，尤其精通操作系统下存储相关的分析。
        关键知识：宿主机磁盘是否已用满主要判断依据是/var/lib/docker的使用率，如果df -h没显示/var/lib/docker目录则根据根目录/下的使用情况判断。
        例如执行df -h之后这个宿主机的磁盘使用情况如下：
        Filesystem                        Size  Used Avail Use% Mounted on
devtmpfs                           46G     0   46G   0% /dev
tmpfs                              46G  8.0K   46G   1% /dev/shm
tmpfs                              46G   11M   46G   1% /run
tmpfs                              46G     0   46G   0% /sys/fs/cgroup
/dev/vda1                          79G   17G   59G  22% /
/dev/mapper/VolDocker-dockerbase  240G  228G   13G  95% /var/lib/docker
/dev/mapper/VolDocker-dockerdata  240G   12G  229G   5% /var/lib/k8s
JuiceFS:infosafe-gps-share        1.0P  767G  1.0P   1% /var/lib/juicefs/volume/pv-juicefs-pro-gps-infosafe-gps-share-jcofan
可以认为这个宿主机的磁盘使用率在95%了，disk接近用满，需要及时清理。
     '''},
     {"role": "user", "content": '''
        我会给你一份执行了清理宿主机磁盘的日志，该日志会输出在宿主机上执行了缓存清理指令docker system prune -f -a的输出，以及清理完后执行df -h的输出。我希望你从日志中提取两个重要信息：
        1. 磁盘清理这个指令清理出来了多少磁盘空间；
        2. 执行清理缓存之后现在宿主机上磁盘还有多少可用空间？使用率是多少？
        3. 判断磁盘清理指令清理后磁盘的使用率是否仍大于50%
        返回输出的样式：
        {
            "pruned_disk": "600MB",
            "disk_usage": "236G",
            "disk_use_percent":"95%",
            "need_inform_user":true
        }
        日志输出如下：
        已连接到目标主机


 执行: sudo docker system prune -f -a
----------------------------------------
sudo docker system prune -f -a
Deleted Containers:
9b3f5bea12de5907d30f2c1210fe7c26fd471a0565a497636059c962b233f5c8
4edec85b6c6554a70639853ed2472dda7f0fc32e553247b546b692f16f873720
cee2efc731e68842244deb999140460a05234df132bb5748b4c196030021d96e

Deleted Images:
untagged: alibaba-cloud-csi-driver/csi-plugin:v1.31.4-init-multi
untagged: alibaba-cloud-csi-driver/csi-plugin@sha256:a0e62132e131439e8357725af759215af8899860298df2c2b314e489d7469c7b
deleted: sha256:bea43f1eb291f407bbdb3bf9a55b250dedb280d8803740700cbb7c0663154660
deleted: sha256:1e5a65f62caa6703cc308967fbc36235442e44e3fc0e34a525247ad6f9d6b3cd
deleted: sha256:98812195d93177c05e4252382da3240e3300b4b1fea0fd97605a9815547e292a
deleted: sha256:615880fae6fbccbf094116fe7910770e65b75e87b1cf121e4c4c2f1f75e16199
deleted: sha256:59a32798f793e00d0f3fe6bc4e8d36b7a05d28fbdc016094745bedd02863fdbc

Total reclaimed space: 61.78MB
[powerop@VMSALI02296558 ~]$ 
 Docker 清理完成

 执行: df -h (只读操作)
----------------------------------------
df -h
Filesystem                        Size  Used Avail Use% Mounted on
devtmpfs                           62G     0   62G   0% /dev
tmpfs                              62G  8.0K   62G   1% /dev/shm
tmpfs                              62G   33M   62G   1% /run
tmpfs                              62G     0   62G   0% /sys/fs/cgroup
/dev/vda1                         197G  171G   18G  91% /
/dev/mapper/VolDocker-dockerdata   60G   49M   60G   1% /var/lib/k8s
JuiceFS:transform                 1.0P   20T 1005T   2% /var/lib/juicefs/volume/pv-juicefs-transform-qeexvt
tmpfs                              13G     0   13G   0% /run/user/1724
     '''}]

print(base_chat(messages_prune))