#ifndef CALCULATOR_H
#define CALCULATOR_H

/**
 * @file calculator.h
 * @brief 简易计算器头文件
 */

/**
 * @brief 加法运算
 * @param a 第一个操作数
 * @param b 第二个操作数
 * @return 两数之和
 */
int add(int a, int b);

/**
 * @brief 减法运算
 * @param a 被减数
 * @param b 减数
 * @return 两数之差
 */
int subtract(int a, int b);

/**
 * @brief 乘法运算
 * @param a 第一个因数
 * @param b 第二个因数
 * @return 两数之积
 */
int multiply(int a, int b);

/**
 * @brief 除法运算
 * @param dividend 被除数
 * @param divisor 除数
 * @return 两数之商
 * @note 除数不能为零
 */
int divide(int dividend, int divisor);

#endif // CALCULATOR_H
