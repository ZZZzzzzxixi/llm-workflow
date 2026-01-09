#ifndef COMPONENT_H
#define COMPONENT_H

#include <stdint.h>

// 组件初始化
int component_init(void);

// 组件处理
int component_process(uint8_t* data, uint32_t length);

// 组件清理
int component_cleanup(void);

#endif // COMPONENT_H
