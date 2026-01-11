#include "calculator.h"
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int dividend, int divisor) {
    if (divisor == 0) {
        printf("Error: Division by zero\n");
        return 0;
    }
    return dividend / divisor;
}
