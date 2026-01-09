#include "component.h"
#include <stdio.h>
#include <stdlib.h>

static int is_initialized = 0;

int component_init(void) {
    if (is_initialized) {
        return -1;
    }

    printf("Component initialized\n");
    is_initialized = 1;
    return 0;
}

static int validate_data(uint8_t* data, uint32_t length) {
    if (!data || length == 0) {
        return -1;
    }
    return 0;
}

static int process_data(uint8_t* data, uint32_t length) {
    for (uint32_t i = 0; i < length; i++) {
        data[i] = data[i] + 1;
    }
    return 0;
}

int component_process(uint8_t* data, uint32_t length) {
    if (!is_initialized) {
        return -2;
    }

    if (validate_data(data, length) != 0) {
        return -1;
    }

    if (process_data(data, length) != 0) {
        return -1;
    }

    return 0;
}

int component_cleanup(void) {
    if (!is_initialized) {
        return -1;
    }

    printf("Component cleaned up\n");
    is_initialized = 0;
    return 0;
}
