void task_dmv() {
	fixed *dest_ptr = dest->data;
	for(uint16_t i = 0; i < rows; i++) {
		fixed *filter_ptr = filter->data + i * cols;
		fixed *src_ptr = src->data;
		fixed w = 0;
		for(uint16_t j = 0; j < cols; j++) {
			w = F_ADD(w, F_MUL(*filter_ptr, *src_ptr));
			filter_ptr++;
			src_ptr++;
		}
		*dest_ptr++ = w;
	}
}