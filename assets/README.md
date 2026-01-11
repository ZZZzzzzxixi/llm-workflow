# Object Detector 模块

## 简介

这是一个基于 YOLO 的目标检测模块，提供简洁的 C API 接口，内部使用 C++ 实现。

## 目录结构

```
object_detector/
├── include/              # 公共 API 头文件
│   ├── object_detector_api.h       # 主 API 接口
│   └── object_detector_config.h    # 配置结构定义
├── src/                  # 实现文件
│   ├── object_detector_api.cpp     # C API 实现
│   ├── yolo_detector.cpp/h         # YOLO 检测器主类
│   ├── detector_types.cpp/h        # 数据类型定义
│   ├── detector_config.h           # 内部配置
│   ├── tkl_npu_engine.cpp          # NPU 推理引擎
│   ├── inference_engine.h          # 推理引擎接口
│   ├── yolov5_postprocessor.cpp    # YOLOv5 后处理
│   ├── postprocessor.h             # 后处理接口
│   ├── letterbox_preprocessor.cpp  # Letterbox 预处理
│   ├── preprocessor.h              # 预处理接口
│   ├── detector_utils.cpp/h        # 工具函数
│   └── ...
├── opencv/               # OpenCV 库
├── model/                # 模型文件
│   ├── yolov5.rknn                 # RKNN 模型
│   └── coco_80_labels_list.txt     # COCO 标签
└── input/                # 测试输入（可选）
```

## 快速开始

### 1. 基本使用

```c
#include "object_detector_api.h"

int main() {
    // 获取默认配置
    OBJECT_DETECTOR_CONFIG_T config = object_detector_get_default_config();
    config.conf_threshold = 0.3f;  // 可选：调整置信度阈值
    
    // 初始化检测器
    if (object_detector_init("/tuya/data/test.model", NULL, &config) != OPRT_OK) {
        printf("Init failed\n");
        return -1;
    }
    
    // 从视频流检测
    OBJECT_DETECTION_LIST_T results;
    OBJECT_DETECTOR_PERF_T perf;
    
    while (1) {
        if (object_detector_detect_from_stream(&results) == 0) {
            // 打印结果
            printf("Found %d objects\n", results.count);
            
            for (int i = 0; i < results.count; i++) {
                const char* name = object_detector_get_class_name(
                    results.results[i].class_id);
                printf("  %s: %.3f\n", name, results.results[i].confidence);
            }
            
            // 性能统计
            object_detector_get_performance(&perf);
            printf("FPS: %.2f\n\n", perf.fps);
        }
        
        usleep(100 * 1000);  // 100ms
    }
    
    // 清理资源
    object_detector_deinit();
    return 0;
}
```

### 2. 从图像数据检测

```c
// 假设你有 RGB 图像数据
unsigned char* image_data = ...;  // RGB 格式
int width = 1920;
int height = 1080;

OBJECT_DETECTION_LIST_T results;
if (object_detector_detect(image_data, width, height, &results) == 0) {
    // 处理检测结果
    for (int i = 0; i < results.count; i++) {
        printf("Object %d: class=%d, conf=%.3f, box=(%d,%d,%d,%d)\n",
            i,
            results.results[i].class_id,
            results.results[i].confidence,
            results.results[i].left,
            results.results[i].top,
            results.results[i].right,
            results.results[i].bottom);
    }
}
```

## API 参考

### 配置相关

#### `object_detector_get_default_config()`
获取默认配置参数。

**返回值：** 默认配置结构

**示例：**
```c
OBJECT_DETECTOR_CONFIG_T config = object_detector_get_default_config();
config.conf_threshold = 0.5f;  // 修改置信度阈值
```

### 初始化与清理

#### `object_detector_init()`
初始化检测器。

**参数：**
- `model_path`: 模型文件路径
- `label_path`: 标签文件路径（可选，传 NULL 使用默认）
- `config`: 配置参数（可选，传 NULL 使用默认）

**返回值：** `OPRT_OK` 成功，其他值表示失败

#### `object_detector_deinit()`
释放检测器资源。

**返回值：** 0 成功，负数表示失败

### 检测相关

#### `object_detector_detect()`
检测图像中的目标。

**参数：**
- `image_data`: RGB 图像数据指针
- `width`: 图像宽度
- `height`: 图像高度
- `results`: 输出检测结果

**返回值：** 0 成功，负数表示失败

#### `object_detector_detect_from_stream()`
从视频流自动获取图像并检测。

**参数：**
- `results`: 输出检测结果

**返回值：** 0 成功，负数表示失败

### 辅助功能

#### `object_detector_get_class_name()`
获取类别名称。

**参数：**
- `class_id`: 类别 ID

**返回值：** 类别名称字符串

#### `object_detector_get_performance()`
获取性能统计。

**参数：**
- `perf`: 输出性能统计数据

**返回值：** 0 成功，负数表示失败

#### `object_detector_update_config()`
运行时更新配置。

**参数：**
- `config`: 新的配置参数

**返回值：** 0 成功，负数表示失败

## 配置参数说明

```c
typedef struct {
    // 模型参数
    int model_width;              // 模型输入宽度（默认 640）
    int model_height;             // 模型输入高度（默认 640）
    
    // 检测参数
    float conf_threshold;         // 置信度阈值（默认 0.25，范围 0.0-1.0）
    float nms_threshold;          // NMS 阈值（默认 0.45，范围 0.0-1.0）
    int max_detections;           // 最大检测数量（默认 100）
    
    // 性能选项
    int enable_timing;            // 启用性能统计（1=启用，0=禁用）
    int save_debug_images;        // 保存调试图像（1=启用，0=禁用）
    int debug_image_interval;     // 调试图像保存间隔（帧数）
} OBJECT_DETECTOR_CONFIG_T;
```

## 注意事项

1. **初始化顺序**：必须先调用 `object_detector_init()` 才能使用其他 API
2. **线程安全**：当前实现使用全局单例，多线程调用需要外部加锁
3. **图像格式**：输入图像必须是 RGB 格式（3 通道）
4. **资源释放**：程序退出前应调用 `object_detector_deinit()` 释放资源
5. **性能优化**：建议关闭 `save_debug_images` 以提升性能

## 性能参考

- **预处理时间**：约 10-20ms
- **推理时间**：约 50-100ms（取决于硬件）
- **后处理时间**：约 5-10ms
- **总体 FPS**：约 8-15 帧/秒

## 故障排查

### 编译错误：找不到头文件

确保在 `local.mk` 中添加了正确的包含路径：
```makefile
LOCAL_TUYA_SDK_INC += $(LOCAL_PATH)/src/object_detector/include
```

### 运行时错误：初始化失败

1. 检查模型文件路径是否正确
2. 检查标签文件是否存在
3. 查看日志输出的具体错误信息

### 性能问题

1. 关闭调试图像保存：`config.save_debug_images = 0`
2. 降低检测频率：增加检测间隔
3. 调整模型输入尺寸：使用更小的 `model_width` 和 `model_height`


