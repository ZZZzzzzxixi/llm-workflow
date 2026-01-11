#ifndef STRING_UTILS_H
#define STRING_UTILS_H

/**
 * @file string_utils.h
 * @brief 字符串工具函数头文件
 */

/**
 * @brief 计算字符串长度
 * @param str 输入字符串
 * @return 字符串长度（不包括结束符'\0'）
 */
size_t string_length(const char *str);

/**
 * @brief 字符串拷贝
 * @param dest 目标缓冲区
 * @param src 源字符串
 * @return 目标字符串指针
 */
char *string_copy(char *dest, const char *src);

/**
 * @brief 字符串拼接
 * @param dest 目标字符串
 * @param src 源字符串
 * @return 目标字符串指针
 */
char *string_concat(char *dest, const char *src);

/**
 * @brief 字符串比较
 * @param str1 第一个字符串
 * @param str2 第二个字符串
 * @return 0表示相等，负数表示str1<str2，正数表示str1>str2
 */
int string_compare(const char *str1, const char *str2);

#endif // STRING_UTILS_H
