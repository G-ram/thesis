void task_dconv() {
	uint16_t scols = MAT_GET_DIM(src, 1);
	for(uint16_t i = 0; i < flayers; i++) {
		fixed *dest_ptr = dest->data;
		for(uint16_t j = 0; j < rows; j++) {
			for(uint16_t k = 0; k < cols; k++) {
				fixed w = 0;
				fixed *filter_ptr = MAT_PTR(filter, i, 0, 0);
				fixed *src_ptr = MAT_PTR(src, i, j, k);
				for(uint16_t l = 0; l < frows; l++) {
					for(uint16_t m = 0; m < fcols; m++) {
						w = F_ADD(w, F_MUL(*src_ptr, *filter_ptr));
						filter_ptr++;
						src_ptr++;
					}
					src_ptr += scols - fcols;
				}
				*dest_ptr++ = w; 
			}
		}
	}
}
