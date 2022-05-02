
#include "sconv_panic.h"

#ifdef UNROLL
#include "sconv1_panic.h"
#endif

void task_sconv() {
	
    uint16_t pos = 0;
	uint16_t len = 0;
	uint16_t fsize = frows * fcols;
	uint16_t idx = filter->sparse.offsets[pos];
	fixed *filter_ptr = filter->data;
	uint16_t scols = MAT_GET_DIM(src, 1);
	while(pos < total_elements) {
		uint16_t k = idx / fsize;
		uint16_t l = (idx % fsize) / fcols;
		uint16_t m = idx % fcols;
		fixed *dest_ptr = dest->data;
		fixed *src_ptr = MAT_PTR(src, k, l, m);

		for(uint16_t i = 0; i < rows; i++) {
			vcfg(cols, _kernel);
			vtfr(src_ptr, SCONV_PANIC_VTFR0);
			vtfr(*filter_ptr, SCONV_PANIC_VTFR1);
			vtfr(dest_ptr, SCONV_PANIC_VTFR2);
			vtfr(dest_ptr, SCONV_PANIC_VTFR3);
			vfence();
			src_ptr += scols;
			dest_ptr += cols;
		}

		pos++;
		idx += filter->sparse.offsets[pos];
		filter_ptr++;
	}
}
