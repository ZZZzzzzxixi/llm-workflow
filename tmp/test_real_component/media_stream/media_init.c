#include "../include/ty_robot_media.h"
#include "../object_detector/include/object_detector_api.h"
#include <stdio.h>

// 全局控制句柄
static void* g_pro_hdl = NULL;

// 入口函数
int ty_robot_media_init(void)
{
    printf("ty_robot_media_init: initializing media module\n");

    // 调用云端初始化
    media_stream_init();

    // 调用视觉初始化（重要，涉及线程初始化）
    robotics_svc_media_vision_init();

    printf("ty_robot_media_init: media module initialized\n");
    return 0;
}

// 云端初始化函数
int media_stream_init(void)
{
    printf("media_stream_init: initializing media stream\n");
    // 初始化云端连接
    g_pro_hdl = (void*)0x12345678;
    return 0;
}

// 视觉模块初始化函数（重要，涉及线程初始化）
int robotics_svc_media_vision_init(void)
{
    printf("robotics_svc_media_vision_init: initializing vision module\n");

    // 调用硬件初始化
    __camera_hw_init();

    // 调用音频初始化
    robotics_svc_media_audio_init();

    // 创建采样线程
    printf("robotics_svc_media_vision_init: creating sample thread\n");

    // 创建检测线程
    printf("robotics_svc_media_vision_init: creating detect thread\n");

    return 0;
}

// 硬件初始化函数
static int __camera_hw_init(void)
{
    printf("__camera_hw_init: initializing camera hardware\n");
    return 0;
}

// 音频初始化函数
int robotics_svc_media_audio_init(void)
{
    printf("robotics_svc_media_audio_init: initializing audio\n");
    return 0;
}

// 采样线程函数
static void* __sample_proc_task(void* arg)
{
    printf("__sample_proc_task: sample thread started\n");

    while (1) {
        printf("__sample_proc_task: reading video frame\n");
        // 读取视频帧
        // 处理视频帧
        // 写入环形缓冲区
    }

    return NULL;
}

// 检测线程函数
static void* __detect_proc_task(void* arg)
{
    printf("__detect_proc_task: detect thread started\n");

    while (1) {
        printf("__detect_proc_task: waiting for detect signal\n");

        // 调用object_detector接口进行目标检测
        object_detector_detect_from_stream(NULL);

        printf("__detect_proc_task: detection completed\n");
    }

    return NULL;
}
