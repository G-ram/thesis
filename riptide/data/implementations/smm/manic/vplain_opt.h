void task_smm();

void task_smm() {
	uint16_t len = 0;

	// Setup
	fixed *dest_ptr = dest->data;
	uint16_t count = rows * cols;
	vsetvl(len, count);
	vandi(v0, v0, 0); // Quick way to zero
	for(uint16_t i = 0; i < count; i += len) {
		vsetvl(len, count - i);
		vsh(dest_ptr, v0);
		vfence();
		dest_ptr += len;
	}

	// Computation
	for(uint16_t i = 0; i < rows; i++) {
		dest_ptr = MAT_PTR(dest, i, 0);
		uint16_t j = filter->sparse.sizes[i];
		for(; j < filter->sparse.sizes[i + 1]; j ++) {
			uint16_t row = filter->sparse.offsets[j];	
			uint16_t k = src->sparse.sizes[row];
			fixed f = filter->data[j];
			for(; k < src->sparse.sizes[row + 1]; k += len) {
				vsetvl(len, src->sparse.sizes[row + 1] - k);
				vlh(v1, src->data + k);
				vmulx(v2, v1.k, f);
				vclipi(v3, v2.k, F_N);
				vlh(v1, src->sparse.offsets + k); // Columns
				vlxh(v2, dest_ptr, v1);
				vadd(v4, v2.k, v3.k);
				vsxh(dest_ptr, v4.k, v1.k);
				vfence();
			}
		}
	}
}
