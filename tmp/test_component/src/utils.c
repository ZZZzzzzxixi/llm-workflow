#include <stdio.h>
#include <string.h>

/**
 * 辅助函数：计算数据校验和
 */
int calculate_checksum(const unsigned char *data, int len) {
    int checksum = 0;
    for (int i = 0; i < len; i++) {
        checksum += data[i];
    }
    return checksum;
}

/**
 * 辅助函数：格式化数据
 */
void format_data(const unsigned char *data, int len, char *buffer) {
    for (int i = 0; i < len && i < 64; i++) {
        sprintf(buffer + i * 3, "%02X ", data[i]);
    }
}
