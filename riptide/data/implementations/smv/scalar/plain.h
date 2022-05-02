void task_smv() {
	fixed *dest_ptr = dest->data;
	for(uint16_t i = 0; i < rows; i++) {
		fixed w = 0;
		uint16_t j = filter->sparse.sizes[i];
		for(; j < filter->sparse.sizes[i + 1]; j++) {
			fixed *src_ptr = src->data + filter->sparse.offsets[j];
			w = F_ADD(w, F_MUL(filter->data[j], *src_ptr));
		}
		*dest_ptr++ = w;
	}
}