void task_smm();

#include "smm_panic.h"

void task_smm() {
#if 1
	for(uint16_t i = 0; i < rows; i++) {
		fixed *dest_ptr = MAT_PTR(dest, i, 0);
		uint16_t j = filter->sparse.sizes[i];
		for(; j < filter->sparse.sizes[i + 1]; j ++) {
			uint16_t row = filter->sparse.offsets[j];	
			uint16_t start = src->sparse.sizes[row];
			uint16_t end = src->sparse.sizes[row + 1];
			uint16_t len = end - start;
			fixed f = filter->data[j];
			vcfg(len, _kernel);
			vtfr(src->data + start, SMM_PANIC_VTFR0);
			vtfr(f, SMM_PANIC_VTFR1);
			vtfr(src->sparse.offsets + start, SMM_PANIC_VTFR2);
			vtfr(dest_ptr, SMM_PANIC_VTFR3);
			vtfr(dest_ptr, SMM_PANIC_VTFR4);
			vfence();
		}
	}
}
