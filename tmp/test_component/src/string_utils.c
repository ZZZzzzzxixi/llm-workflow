#include "string_utils.h"
#include <stdio.h>

size_t string_length(const char *str) {
    if (str == NULL) {
        return 0;
    }
    
    size_t len = 0;
    while (str[len] != '\0') {
        len++;
    }
    return len;
}

char *string_copy(char *dest, const char *src) {
    if (dest == NULL || src == NULL) {
        return NULL;
    }
    
    char *dest_ptr = dest;
    while ((*dest_ptr++ = *src++) != '\0') {
        // Copy character by character
    }
    return dest;
}

char *string_concat(char *dest, const char *src) {
    if (dest == NULL || src == NULL) {
        return NULL;
    }
    
    // Move dest pointer to the end of the string
    while (*dest != '\0') {
        dest++;
    }
    
    // Copy src to the end of dest
    while ((*dest++ = *src++) != '\0') {
        // Copy character by character
    }
    
    return dest - string_length(src) - 1;
}

int string_compare(const char *str1, const char *str2) {
    if (str1 == NULL || str2 == NULL) {
        if (str1 == str2) {
            return 0;
        }
        return (str1 == NULL) ? -1 : 1;
    }
    
    while (*str1 != '\0' && *str2 != '\0') {
        if (*str1 != *str2) {
            return *str1 - *str2;
        }
        str1++;
        str2++;
    }
    
    return *str1 - *str2;
}
