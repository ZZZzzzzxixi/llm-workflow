# Test Component

这是一个测试用的C语言组件库，包含计算器和字符串工具函数。

## 目录结构

```
test_component/
├── include/        # 头文件目录
│   ├── calculator.h
│   └── string_utils.h
├── src/           # 源文件目录
│   ├── calculator.c
│   └── string_utils.c
└── lib/           # 库文件目录（预留）
```

## 功能说明

### 计算器模块 (calculator.h/c)
- add(): 加法运算
- subtract(): 减法运算
- multiply(): 乘法运算
- divide(): 除法运算

### 字符串工具模块 (string_utils.h/c)
- string_length(): 计算字符串长度
- string_copy(): 字符串拷贝
- string_concat(): 字符串拼接
- string_compare(): 字符串比较

## 使用示例

```c
#include "calculator.h"
#include "string_utils.h"

int main() {
    int result = add(5, 3);
    char str[50];
    string_copy(str, "Hello");
    string_concat(str, " World");
    return 0;
}
```
