#include "../include/object_detector_api.h"
#include <stdio.h>

// 初始化目标检测器
int object_detector_init(void)
{
    printf("object_detector_init: initializing object detector\n");
    return 0;
}

// 从视频流检测目标
int object_detector_detect_from_stream(void* stream)
{
    printf("object_detector_detect_from_stream: detecting objects from stream\n");

    // 调用预处理函数
    __preprocess_image(stream);

    // 调用推理函数
    __run_inference(stream);

    // 调用后处理函数
    __postprocess_results(stream);

    return 0;
}

// 预处理图像
static int __preprocess_image(void* stream)
{
    printf("__preprocess_image: preprocessing image\n");
    return 0;
}

// 运行推理
static int __run_inference(void* stream)
{
    printf("__run_inference: running inference\n");
    return 0;
}

// 后处理结果
static int __postprocess_results(void* stream)
{
    printf("__postprocess_results: postprocessing results\n");
    return 0;
}
