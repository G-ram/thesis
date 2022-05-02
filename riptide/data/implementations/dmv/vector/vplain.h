#define min(a, b) (((a) < (b)) ? (a) : (b))

void task_dmv() {
	uint16_t len = 0;

	for(uint16_t i = 0; i < rows; i += BLOCK_SIZE) {
		for(uint16_t j = 0; j < cols; j += BLOCK_SIZE) {
			fixed *dest_ptr = dest->data + i;
			*dest_ptr = 0; // Breaks blocking
			for(uint16_t k = i; k < min(i + BLOCK_SIZE, rows); k++) {
				fixed *filter_ptr = filter->data + k * cols + j;
				fixed *src_ptr = src->data + j;
				fixed w = 0;
				uint16_t max_l = min(j + BLOCK_SIZE, cols);
				for(uint16_t l = j; l < max_l; l += len) {
					vsetvl(len, max_l - l);
					vlh(v0, filter_ptr);
					vlh(v1, src_ptr);
					vmul(v2, v0, v1);
					vclipi(v1, v2, F_N);
					vredsum(v0, v1);
					vfence();
					fixed tmp;
					uint16_t tlen;
					vsetvl(tlen, 1);
					vsh((&tmp), v0);
					vfence();
					w = F_ADD(w, tmp);
					filter_ptr += len;
					src_ptr += len;
				}
				*dest_ptr++ += w;
				*dest_ptr = 0; // Breaks blocking
			}
		}
	}
}