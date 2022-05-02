void task_fft1d();

#include "fft0_panic.h"
#include "fft1_panic.h"
#include "fft2_panic.h"
#include "fft3_panic.h"

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

// Alternative implementation
// k = VL
// p = int(math.log(VL, 2))
// while k > 1:
// 	mask = ~(k - 1) & 0xFFFFFFFF
// 	imask = k - 1
// 	shuffle = [((i + (k >> 1)) & imask) + (i & mask) for i in range(VL)]
// 	twiddle = [(v & (k >> 1)) >> (p - 1) for v in shuffle]
// 	sign_twiddle = [1 if t else -1 for t in twiddle]
// 	Q = [0 if t else (shuffle[i] & ((k >> 1) - 1)) + 1 \
//		for i, t in enumerate(twiddle)]

fixed real_tmp[1024];
fixed imag_tmp[1024];
bool cached_twiddles = false;

uint16_t clog2(uint16_t v) {
	uint16_t p = 1;
	while(v > (1 << p)) p++;
	return p;
}

void task_fft1d() {
	fixed *src_real_ptr_base = MAT_PTR(src_real, row_idx, col_idx);
	fixed *src_imag_ptr_base = MAT_PTR(src_imag, row_idx, col_idx);
	fixed *dest_real_ptr_base = MAT_PTR(dest_real, row_idx, col_idx);
	fixed *dest_imag_ptr_base = MAT_PTR(dest_imag, row_idx, col_idx);

	fixed *src_real_ptr = src_real_ptr_base;
	fixed *src_imag_ptr = src_imag_ptr_base;
	fixed *dest_real_ptr = dest_real_ptr_base;
	fixed *dest_imag_ptr = dest_imag_ptr_base;

	if(len != num_elements) exit(0);

	uint16_t log2 = clog2(num_elements);
	uint16_t strided_step = len * stride;
	uint16_t new_stride = stride * (num_elements / len);
	if(new_stride == 0) new_stride = stride;
	for(uint16_t i = 0; i < num_elements; i += len) {
		uint16_t k = 0;
		uint16_t p = log2;

		// ===== WINDOW =====
		vcfg(num_elements, _kernel0);
		vtfrx(src_real_ptr, new_stride, FFT0_PANIC_VTFR0);
		vtfrx(src_imag_ptr, new_stride, FFT0_PANIC_VTFR1);
		vfence();
		// ===== WINDOW =====
		
		for(uint16_t j = 1; j < len; j <<= 1, k++, p--) {
			uint16_t shift = 1 << p;
			uint16_t shift_2 = shift >> 1;
			uint16_t shift_1 = shift - 1;
			uint16_t mask = ~shift_1;
			uint16_t p_1 = p - 1;

			// ===== WINDOW =====
			vcfg(num_elements, _kernel1);
			vtfr(shift_2, FFT1_PANIC_VTFR0);
			vtfr(shift_1, FFT1_PANIC_VTFR1);
			vtfr(mask, FFT1_PANIC_VTFR2);
			vtfr(shift_2, FFT1_PANIC_VTFR3);
			vtfr(p_1, FFT1_PANIC_VTFR4);
			vfence();
			// ===== WINDOW =====

			// ===== WINDOW =====
			vcfg(num_elements, _kernel2);
			vtfr(real_twiddle[k], FFT2_PANIC_VTFR0);
			vtfr(imag_twiddle[k], FFT2_PANIC_VTFR1);
			vfence();
			// ===== WINDOW =====
		}

		uint16_t shift = 1 << p;
		uint16_t shift_2 = shift >> 1;
		uint16_t mask = ~(shift - 1);

		// ===== WINDOW =====
		vcfg(num_elements, _kernel3);
		vtfr(permute[log2], FFT3_PANIC_VTFR0);
		vtfr(stride, FFT3_PANIC_VTFR1);
		vtfr(dest_real_ptr_base, FFT3_PANIC_VTFR2);
		vtfr(dest_imag_ptr_base, FFT3_PANIC_VTFR3);
		vfence();
		// ===== WINDOW =====
		if(len < num_elements) {
			src_real_ptr += stride;
			src_imag_ptr += stride;
			dest_real_ptr += stride;
			dest_imag_ptr += stride;
		}
	}

}
