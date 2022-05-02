#define min(a, b) (((a) < (b)) ? (a) : (b))

void task_dmm() {
	uint16_t len = 0;

	for(uint16_t i = 0; i < rows; i += BLOCK_SIZE) {
		for(uint16_t j = 0; j < dcols; j += BLOCK_SIZE) {
			for(uint16_t k = 0; k < cols; k += BLOCK_SIZE) {
				fixed *filter_ptr = filter->data + i * cols + k;
				for(uint16_t l = i; l < min(i + BLOCK_SIZE, rows); l++) {
					fixed *dest_ptr = dest->data + l * dcols + j;
					*dest_ptr = 0; // Breaks blocking
					uint16_t max_n = min(k + BLOCK_SIZE, cols);
					for(uint16_t m = j; m < min(j + BLOCK_SIZE, dcols); m++) {
						fixed w = 0;
						fixed *src_ptr = src->data + dcols * k + m;
						fixed *cur_filter_ptr = filter_ptr;
						for(uint16_t n = k; n < max_n; n += len) {
							vsetvl(len, max_n - n);
							vlh(v0, cur_filter_ptr);
							vlsh(v1, src_ptr, dcols);
							vmul(v2, v0.k, v1.k);
							vclipi(v1, v2.k, F_N);
							vredsum(v0, v1.k);
							vfence();
							uint16_t tlen;
							fixed tmp = 0;
							vsetvl(tlen, 1);
							vsh((&tmp), v0.k);
							vfence();
							w = F_ADD(w, tmp);
							src_ptr += dcols * len;
							cur_filter_ptr += len;
						}
						*dest_ptr++ += w;
						*dest_ptr = 0; // Breaks blocking
					}
					filter_ptr += cols;
				}
			}
		}
	}
}
