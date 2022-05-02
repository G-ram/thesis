void task_sconv() {
	uint16_t fsize = frows * fcols;

	uint16_t pos = 0;
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
			for(uint16_t j = 0; j < cols; j++) {
				fixed w = F_MUL(*src_ptr, *filter_ptr);
				if(pos == 0) *dest_ptr = 0;
				*dest_ptr = F_ADD(*dest_ptr, w);
				dest_ptr++;
				src_ptr++;
			}
			src_ptr += scols - cols;
		}
		pos++;
		idx += filter->sparse.offsets[pos];
		filter_ptr++;
	}
}
