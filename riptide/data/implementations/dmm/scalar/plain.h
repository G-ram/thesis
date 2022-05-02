void task_dmm() {
	int16_t *dest_ptr = dest->data;
	for(uint32_t i = 0; i < rows; i++) {
		uint32_t row = i * cols;
		for(uint32_t j = 0; j < dcols; j++) {
			int16_t w = 0;
			for(uint32_t k = 0; k < cols; k++) {
				w = F_ADD(w, F_MUL(filter->data[row + k], 
					src->data[k * dcols + j]));
			}
			*dest_ptr++ = w;
		}
	}
}