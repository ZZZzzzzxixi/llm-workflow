#!/bin/bash

# API测试脚本

# 配置
API_URL="https://rfvfy978y6.coze.site/run"
TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6IjI1NDgzMTMwLWQxYzAtNGZlNS05ZjJlLWRmNjU3OTFkMDJlNSJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImsxM09jVEVCT01FVnhmRTJKQzgyaFAyS1hhYzdEWkxxIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzY3OTQ0MzY5LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NTkzMjQzMTg1MTI0NDc0OTMwIiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NTkzMjYzMjQ5OTQ1MDAyMDI2In0.LZf4wiYUEX4di5dUNVyyGLUb_3B39ceqp3dlgH_qKp86t-eCzG5bQKpMH4AIt49ZFNzoMtaC5W9pvjY14TXIS9-KyJdZDCjhl85XQSNWP3M8SueitKf3c_D2o0f4z_UwNDyOJdTxLDWUeFAdLw4d3jhjii3TnkVQPlpt3lPG6F39iHbZsV51rrBZSvrKRXQeELO_4WsVMfWy6UtmBipPtRHRiKFwwQBb9o79c5ciUOLTmWBhVpKiIfIdVl-DOBVry_JGg_RsWzK7LaMEh09-onvcffusTrUKC8iAKIhz0ABdoZkRV-HItknm8arQnevk7ZpWt26bxV5UqICKne1hmA"
COMPONENT_URL="https://raw.githubusercontent.com/ZZZzzzzxixi/llm-workflow/tmp/source/robotics_svc_media.zip"

echo "========== 方法1：直接单行curl命令 =========="
echo "执行命令："
echo 'curl --location '"${API_URL}"' --header "Authorization: Bearer '"${TOKEN}"'" --header "Content-Type: application/json" --data '"'"'{\"component_path\":\"'${COMPONENT_URL}'\"}'"'"
echo ""

curl --location "${API_URL}" \
  --header "Authorization: Bearer ${TOKEN}" \
  --header "Content-Type: application/json" \
  --data "{\"component_path\":\"${COMPONENT_URL}\"}"

echo ""
echo ""
echo "========== 方法2：使用JSON文件 =========="

# 创建JSON文件
cat > /tmp/test_request.json << EOF
{"component_path":"${COMPONENT_URL}"}
EOF

echo "请求内容："
cat /tmp/test_request.json
echo ""

echo "执行curl命令..."
curl --location "${API_URL}" \
  --header "Authorization: Bearer ${TOKEN}" \
  --header "Content-Type: application/json" \
  --data @/tmp/test_request.json

echo ""
echo ""
echo "========== 方法3：使用echo和pipe =========="

echo '{"component_path":"'${COMPONENT_URL}'"}' | \
curl --location "${API_URL}" \
  --header "Authorization: Bearer ${TOKEN}" \
  --header "Content-Type: application/json" \
  --data @-

echo ""
echo "========== 测试完成 =========="
