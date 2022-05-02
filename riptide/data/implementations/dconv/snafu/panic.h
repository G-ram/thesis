#include "dconv_panic.h"

#ifdef UNROLL
#include "dconv1_panic.h"
#endif


void task_dconv() {
	uint16_t scols = MAT_GET_DIM(src, 1);
	fixed *src_row_ptr = src->data;
	fixed *filter_ptr = filter->data;
	for(uint16_t i = 0; i < frows; i++) {
		for(uint16_t j = 0; j < fcols; j++) {
			fixed *dest_ptr = dest->data;
			fixed *src_ptr = src_row_ptr + j;
			for(uint16_t k = 0; k < rows; k++) {
				vcfg(cols, _kernel);
				vtfr(src_ptr, DCONV_PANIC_VTFR0);
				vtfr(*filter_ptr, DCONV_PANIC_VTFR1);
				vtfr(dest_ptr, DCONV_PANIC_VTFR2);
				vtfr(dest_ptr, DCONV_PANIC_VTFR3);
				vfence();
				src_ptr += scols;
				dest_ptr += cols;
			}
			filter_ptr++;
		}
		src_row_ptr += scols;
	}
}
