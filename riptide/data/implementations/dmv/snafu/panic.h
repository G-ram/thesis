#define min(a, b) (((a) < (b)) ? (a) : (b))
fixed tmp = 0;
fixed *tmp_dest = &tmp;

void task_dmv() {

	uint16_t rblock = rows;
	uint16_t cblock = cols;

	for(uint16_t i = 0; i < rows; i += rblock) {
		for(uint16_t j = 0; j < cols; j += cblock) {
			fixed *dest_ptr = dest->data + i;
			fixed *src_ptr = src->data + j;
			fixed *filter_ptr = filter->data + i * cols + j;
			uint16_t max_l = min(j + cblock, cols);
			for(uint16_t k = i; k < min(i + rblock, rows); k++) {
					
				vcfg(max_l, _kernel);
				vtfr(filter_ptr, DMV_PANIC_VTFR0);
				vtfr(src_ptr, DMV_PANIC_VTFR1);
				vtfr(tmp_dest - max_l + 1, DMV_PANIC_VTFR2);
				vfence();

				filter_ptr += max_l;
				*dest_ptr++ += tmp;
			}
		}
	}
}
