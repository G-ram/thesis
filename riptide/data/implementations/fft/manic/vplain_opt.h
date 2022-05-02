void task_fft1d();

#if VL == 16
#include "permute_small.h"
#include "twiddle_small.h"
uint16_t len = 16;
#elif VL == 32
#include "permute_medium.h"
#include "twiddle_medium.h"
uint16_t len = 32;
#elif VL == 64
#include "permute_large.h"
#include "twiddle_large.h"
uint16_t len = 64;
#else
#include "permute_huge.h"
#include "twiddle_huge.h"
uint16_t len = 128;
#endif

void task_fft1d() {
	fixed *src_real_ptr_base = MAT_PTR(src_real, row_idx, col_idx);
	fixed *src_imag_ptr_base = MAT_PTR(src_imag, row_idx, col_idx);
	fixed *dest_real_ptr_base = MAT_PTR(dest_real, row_idx, col_idx);
	fixed *dest_imag_ptr_base = MAT_PTR(dest_imag, row_idx, col_idx);

	vsetvl(len, len);

	fixed *src_real_ptr = src_real_ptr_base;
	fixed *src_imag_ptr = src_imag_ptr_base;
	fixed *dest_real_ptr = dest_real_ptr_base;
	fixed *dest_imag_ptr = dest_imag_ptr_base;
	
	uint16_t strided_step = len * stride;
	uint16_t new_stride = stride * (num_elements / len);
	if(new_stride == 0) new_stride = stride;

	for(uint16_t i = 0; i < num_elements; i += len) {
		vlsh(v0, src_real_ptr, new_stride);
		vlsh(v1, src_imag_ptr, new_stride);
		
		uint16_t k = 0;
		for(uint16_t j = 1; j < len; j <<= 1, k++) {
			vaddi(v5, v1, 0); // Make a copy of imag // 3
			vlh(v4, permute[k]); // 2
			vaddi(v6, v0, 0); // Make a copy of real // 1
			vpermute(v3, v5.k, v4); // permute imag // 5
			vpermute(v2, v6.k, v4.k); // permute real // 4
			
			vlh(v4, sign_twiddle[k]); // 6
			vmul(v0, v0.k, v4); // Apply sign twiddle to real // 7
			vmul(v1, v1.k, v4.k); // Apply sign twiddle to imag // 8

			vadd(v2, v0.k, v2.k); // Real sum (a) // 9
			vadd(v3, v1.k, v3.k); // Imag sum (b) // 10

			vlh(v4, real_twiddle[k]); // Twiddle real (alpha) // 11

			vmul(v6, v4, v3); // alpha * b // 15
			
			vlh(v5, imag_twiddle[k]); // Twiddle imag (beta) // 12

			vmul(v7, v5, v2); // beta * a // 16

			vclipi(v7, v7.k, F_N); // 20
			vclipi(v6, v6.k, F_N); // 19

			vsub(v1, v6.k, v7.k); // alpha * b - beta * a // 22

			vmul(v7, v5.k, v3.k); // beta * b // 14
			vclipi(v7, v7.k, F_N); // 18
			vmul(v6, v2.k, v4.k); // alpha * a // 13
			vclipi(v6, v6.k, F_N); // 17

			vadd(v0, v6.k, v7.k); // alpha * a + beta * b // 21
		}

		vlh(v2, permute[k]);
		vpermute(v3, v0, v2);
		vpermute(v4, v1, v2);
		vssh(dest_real_ptr, v3, stride);
		vssh(dest_imag_ptr, v4, stride);
		vfence();

		if(len < num_elements) {
			src_real_ptr += stride;
			src_imag_ptr += stride;
			dest_real_ptr += stride;
			dest_imag_ptr += stride;
		}
	}
}

