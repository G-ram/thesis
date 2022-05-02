#include "smv_panic.h"

void task_smv() {
	fixed tmp = 0;
	fixed *tmp_dest = &tmp;
	fixed *dest_ptr = dest->data;

	for(uint16_t i = 0; i < rows; i++) {
		uint16_t start = filter->sparse.sizes[i];
		uint16_t end = filter->sparse.sizes[i + 1];
		uint16_t len = end - start;

		uint16_t *offset_ptr = filter->sparse.offsets + start;
		uint16_t *filter_ptr = filter->data + start;

		vcfg(len, _kernel);
		vtfr(offset_ptr, SMV_PANIC_VTFR0);
		vtfr(src->data, SMV_PANIC_VTFR1);
		vtfr(filter_ptr, SMV_PANIC_VTFR2);
		vtfr(tmp_dest - len + 1, SMV_PANIC_VTFR3);
		vfence();
		*dest_ptr++ = *tmp_dest;
	}
}