#ifndef TY_ROBOT_MEDIA_H
#define TY_ROBOT_MEDIA_H

#include <stdint.h>

// 主入口函数
int ty_robot_media_init(void);

// 视觉模块初始化函数（重要，涉及线程初始化）
int robotics_svc_media_vision_init(void);

// 云端初始化函数
int media_stream_init(void);

// 音频初始化函数
int robotics_svc_media_audio_init(void);

#endif
