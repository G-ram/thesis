#define min(a, b) (((a) < (b)) ? (a) : (b))

fixed tmp = 0;
fixed *tmp_dest = &tmp;

void task_dmm() {

	for(uint16_t i = 0; i < rows; i += BLOCK_SIZE) {
		for(uint16_t j = 0; j < dcols; j += BLOCK_SIZE) {
			for(uint16_t k = 0; k < cols; k += BLOCK_SIZE) {
				fixed *filter_ptr = filter->data + i * cols + k;
				for(uint16_t l = i; l < min(i + BLOCK_SIZE, rows); l++) {
					fixed *dest_ptr = dest->data + l * dcols + j;
					fixed *src_ptr = src->data + dcols * k + j;
					uint16_t max_n = min(k + BLOCK_SIZE, cols);
					fixed *tmp_dest_ptr = tmp_dest - max_n + 1;
					
					for(uint16_t m = j; m < min(j + BLOCK_SIZE, dcols); m++) {

						vcfg(max_n, _kernel);
						vtfr(filter_ptr, DMM_PANIC_VTFR0);
						vtfrx(src_ptr, dcols, DMM_PANIC_VTFR1);
						vtfr(tmp_dest_ptr, DMM_PANIC_VTFR2);
						vfence();

						*dest_ptr++ += tmp;
						src_ptr++;
					}
					filter_ptr += cols;
				}
			}
		}
	}
}
