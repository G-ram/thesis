void task_smm();

void task_smm() {
	fixed *dest_ptr = dest->data;
	for(uint16_t i = 0; i < rows; i++) {
		for(uint16_t j = 0; j < cols; j++) {
			*dest_ptr++ = 0;
		}
	}

	for(uint16_t i = 0; i < rows; i++) {
		fixed *dest_ptr = MAT_PTR(dest, i, 0);
		uint16_t j = filter->sparse.sizes[i];
		for(; j < filter->sparse.sizes[i + 1]; j++) {
			uint16_t row = filter->sparse.offsets[j];	
			uint16_t k = src->sparse.sizes[row];
			fixed f = filter->data[j];
			for(; k < src->sparse.sizes[row + 1]; k++) {
				fixed w = F_MUL(f, src->data[k]);
				uint16_t col = src->sparse.offsets[k];
				fixed *d = dest_ptr + col;
				*d = F_ADD(w, *d);
			}
		}
	}
}
