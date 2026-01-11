#!/bin/bash

# 创建测试目录结构

echo "创建测试目录结构..."

# 创建根目录
mkdir -p /tmp/test_component_with_opencv/test_component

# 创建 README.md（不应该被识别为开源库）
echo "# Test Component" > /tmp/test_component_with_opencv/test_component/README.md

# 创建用户的代码文件夹
mkdir -p /tmp/test_component_with_opencv/test_component/include
cat > /tmp/test_component_with_opencv/test_component/include/my_api.h << 'EOF'
#ifndef MY_API_H
#define MY_API_H

void init_api(void);
int process_data(int input);

#endif
EOF

mkdir -p /tmp/test_component_with_opencv/test_component/src
cat > /tmp/test_component_with_opencv/test_component/src/my_api.c << 'EOF'
#include "my_api.h"
#include <stdio.h>

void init_api(void) {
    printf("API initialized\n");
}

int process_data(int input) {
    return input * 2;
}
EOF

# 创建第三方库文件夹（应该被识别并略过）
mkdir -p /tmp/test_component_with_opencv/test_component/opencv/include
mkdir -p /tmp/test_component_with_opencv/test_component/opencv/lib

# 创建 LICENSE 文件（应该被识别为开源库）
echo "MIT License" > /tmp/test_component_with_opencv/test_component/opencv/LICENSE

# 创建 opencv 头文件
cat > /tmp/test_component_with_opencv/test_component/opencv/include/opencv_core.h << 'EOF'
// OpenCV Core Header
#ifndef OPENCV_CORE_H
#define OPENCV_CORE_H
// OpenCV definitions
#endif
EOF

# 创建另一个第三方库文件夹 vendor
mkdir -p /tmp/test_component_with_opencv/test_component/vendor/tensorflow
cat > /tmp/test_component_with_opencv/test_component/vendor/tensorflow/LICENSE << 'EOF'
Apache License 2.0
EOF

# 打包成 zip
cd /tmp/test_component_with_opencv
zip -r test_component_with_opencv.zip test_component > /dev/null
mv test_component_with_opencv.zip /workspace/projects/assets/

echo "✅ 测试文件创建完成：assets/test_component_with_opencv.zip"
echo ""
echo "目录结构："
echo "test_component/"
echo "├── README.md"
echo "├── include/"
echo "│   └── my_api.h"
echo "├── src/"
echo "│   └── my_api.c"
echo "├── opencv/         # 应该被识别为第三方库"
echo "│   ├── LICENSE"
echo "│   ├── include/"
echo "│   └── lib/"
echo "└── vendor/         # 应该被识别为第三方库"
echo "    └── tensorflow/"
echo "        └── LICENSE"
