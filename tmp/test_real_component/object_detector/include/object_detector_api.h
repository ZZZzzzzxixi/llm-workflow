#ifndef OBJECT_DETECTOR_API_H
#define OBJECT_DETECTOR_API_H

// 从视频流检测目标
int object_detector_detect_from_stream(void* stream);

// 初始化目标检测器
int object_detector_init(void);

#endif
