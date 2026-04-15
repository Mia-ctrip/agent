#!/bin/bash
# 查询 Docker Overlay 容器映射脚本

docker ps -q | xargs docker inspect --format '{{.Name}} {{.GraphDriver.Data.MergedDir}}' | while read name merged; do
    pod=$(echo "$name" | cut -d'_' -f3)
    overlay=$(echo "$merged" | sed 's|/var/lib/docker/overlay2/||;s|/merged||')
    echo "$overlay $pod"
done
