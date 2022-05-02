void task_sort();

uint16_t len = VL;

void radix(fixed *src, fixed *dest) {
	vlh(v1, src);
	vxorx(v1, v1.k, 0x8000);
	uint16_t bit = 0x1;
	for(uint16_t i = 0; i < 16; i++) {
		vandx(v0, v1, bit);
		vsrlx(v0, v0.k, i);
		vredsum(v2, v0);
		vfence();
		uint16_t tlen;
		fixed tmp;
		vsetvl(tlen, 1);
		vsh((&tmp), v2.k);
		vfence();	
		uint16_t offset = len - tmp - 1;
		if(len - tmp == 0) offset = 0;
		vsetvl(len, len);
		vpresum(v2, v0);
		vaddx(v3, v2.k, offset);
		vpermute(v4.m, v1, v3.k);

		vxori(v0, v0.k, 1);
		vpresum(v2, v0);
		vsubi(v2, v2.k, 1);
		vpermute(v4.m, v1.k, v2.k);
		vaddi(v1, v4.k, 0);

		bit <<= 0x1;
	}

	vxorx(v1, v1.k, 0x8000);
	
	if(dest != NULL) {
		vsh(dest, v1.k);
		vfence();
	}
}

void merge(fixed *src1, fixed *src2, fixed *dest, uint16_t len) {
	uint16_t idx1 = 0;
	uint16_t idx2 = 0;
	// I am sorry for this craziness, I just like stuff on one line
	for(uint16_t i = 0; i < 2 * len; i++) {
		if(idx1 < len && idx2 < len)
			if(*src1 < *src2) *dest++ = *src1++, idx1++;
			else *dest++ = *src2++, idx2++;
		else if(idx1 < len) *dest++ = *src1++, idx1++;
		else *dest++ = *src2++, idx2++;
	}
}

void task_sort() {
	uint16_t count = MAT_GET_DIM(dest, 0);
	fixed *src_ptr = src->data;
	fixed *dest_ptr = dest->data;
	fixed *inter_ptr = inter->data;
	for(uint16_t i = 0; i < count; i += len) {
		vsetvl(len, len);
		radix(src_ptr, dest_ptr);
		src_ptr += len;
		dest_ptr += len;
	}

	dest_ptr = dest->data;
	uint8_t swap = 1;
	uint16_t idx = len;
	while(idx < count) {
		fixed *tmp = inter_ptr;
		inter_ptr = dest_ptr;
		dest_ptr = tmp;
		for(uint16_t i = 0; i < count; i += 2 * idx)
			merge(inter_ptr + i, inter_ptr + i + idx, dest_ptr + i, idx);
		idx <<= 1;
		swap = swap ^ 0x01;
	}

	if(!swap) {
		for(uint16_t i = 0; i < count; i += len) {
			vsetvl(len, count - i);
			vlh(v0, dest_ptr + i);
			vsh(inter_ptr + i, v0.k);
			vfence();
		}
	}

}
