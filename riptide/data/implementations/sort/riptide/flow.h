#include "sort_flow.h"
#include "sort_setup_flow.h"

void task_sort() {
        uint32_t size = MAT_GET_DIM(dest, 0);
        int16_t *src_ptr = src->data;
        int16_t *dest_ptr = dest->data;
        uint32_t count = 0;

        sort_setup(src_ptr, src_ptr, &count, size);
        cwait();

        sort(src_ptr, dest_ptr, size, count);
        cwait();

        sort_setup(src_ptr, dest_ptr, &count, size);
        cwait();

}
