void task_sort();

#include "sort0_panic.h"
#include "sort1_panic.h"

void task_sort() {
	uint16_t count = MAT_GET_DIM(dest, 0);
	fixed *src_ptr = src->data;
	fixed *dest_ptr = dest->data;
	fixed *inter_ptr = inter->data;


	volatile uint16_t tmp;
	uint16_t *tmp_buffer = &tmp - count + 1;
	uint16_t width = 8 * sizeof(fixed);
	uint16_t offset = 0;

	// ===== WINDOW =====
	vcfg(count, _kernel0);
	vtfr(src_ptr, SORT0_PANIC_VTFR0);
	vtfr(tmp_buffer, SORT0_PANIC_VTFR1);
	vfence();
	// ===== WINDOW =====

	for(uint16_t i = 0; i < width; i++) {
		fixed *src_buffer = (i & 0x1) ? inter_ptr : src_ptr;
		fixed *dest_buffer = (i & 0x1) ? src_ptr : inter_ptr;
		if(i == width - 1) dest_buffer = dest_ptr;

		offset = count - tmp;
		if(offset != 0) offset -= 1;

		// ===== WINDOW =====
		vcfg(count, _kernel1);
		vtfr(src_buffer, SORT1_PANIC_VTFR0);
		vtfr(0x8000, SORT1_PANIC_VTFR1);
		vtfr((i + 1), SORT1_PANIC_VTFR2);
		vtfr(tmp_buffer, SORT1_PANIC_VTFR3);
		vtfr(i, SORT1_PANIC_VTFR4);
		vtfr(offset, SORT1_PANIC_VTFR5);
		vtfr(dest_buffer, SORT1_PANIC_VTFR6);
		vtfr((dest_buffer - 1), SORT1_PANIC_VTFR7);
		vfence();
		// ===== WINDOW =====
	}

}
