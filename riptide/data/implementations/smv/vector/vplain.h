void task_smv() {

	for(uint16_t i = 0; i < rows; i++) {
		uint16_t start = filter->sparse.sizes[i];	
		uint16_t end = filter->sparse.sizes[i + 1];	
		fixed *filter_ptr = MAT_PTR(filter, start);
		uint16_t *offset = filter->sparse.offsets + start;
		uint16_t len = 0;
		fixed w = 0;
		for(uint16_t j = start; j < end; j += len) {
			vsetvl(len, end - j);
			vlh(v2, offset);
			vlxh(v0, src->data, v2);
			vlh(v1, filter_ptr);
			vmul(v2, v0, v1);
			vclipi(v1, v2, F_N);
			vredsum(v0, v1);
			uint16_t tlen, tremaining = 1;
			fixed tmp;
			vfence();
			vsetvl(tlen, tremaining);
			vsh((&tmp), v0);
			vfence();
			w = F_ADD(w, tmp);
			offset += len;
			filter_ptr += len;
		}
		MAT_SET(dest, w, i, 0);
	}
}
