void task_dconv() {
	uint16_t len = 0;
	uint16_t scols = MAT_GET_DIM(src, 1);

	fixed *filter_ptr = filter->data;
	for(uint16_t k = 0; k < flayers; k++) {
		for(uint16_t l = 0; l < frows; l++) {
			for(uint16_t m = 0; m < fcols; m++) {
				fixed *dest_ptr = dest->data;
				fixed *src_ptr = MAT_PTR(src, k, l, m);
				for(uint16_t i = 0; i < rows; i++) {
					for(uint16_t j = 0; j < cols; j += len) {
						vsetvl(len, cols - j);
						vlh(v0, src_ptr);
						vmulx(v1, v0.k, *filter_ptr);
						vclipi(v2, v1.k, F_N);
						vlh(v3, dest_ptr);
						vadd(v4, v2.k, v3.k);
						vsh(dest_ptr, v4.k);
						vfence();	
						dest_ptr += len;
						src_ptr += len;
					}
					src_ptr += scols - cols;
				}
				filter_ptr++;
			}
		}
	}
}
