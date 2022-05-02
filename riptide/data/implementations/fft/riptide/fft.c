#include "stdint.h"

#include "helpers.h"
#undef PTR
#define PTR(typ) typ *

void fft(PTR(int16_t) real_ptr, PTR(int16_t) imag_ptr, 
	CONST_PTR(int16_t) real_twiddle, CONST_PTR(int16_t) imag_twiddle,
	uint32_t size, uint32_t stride, uint32_t step, 
	uint32_t Ls, uint32_t theta,
	uint32_t strided_step, uint32_t Ls_stride) {

	for(uint32_t j = 0; j < Ls; j++) {
		uint32_t theta_idx = j + theta;
		int16_t wr = real_twiddle[theta_idx];
		int16_t wi = imag_twiddle[theta_idx];

		PTR(int16_t) real = real_ptr;
		PTR(int16_t) imag = imag_ptr;
		real_ptr += stride;
		imag_ptr += stride;

		for(uint32_t k = j; k < size; k += step) {

			int16_t re = real[Ls_stride];
			int16_t im = imag[Ls_stride];
			int16_t tr = clip(wr * re, 5) - clip(wi * im, 5);
			int16_t ti = clip(wr * im, 5) + clip(wi * re, 5);

			re = real[0];
			im = imag[0];
			real[Ls_stride] = re - tr;
			imag[Ls_stride] = im - ti;
			real[0] = re + tr;
			imag[0] = im + ti;

			real += strided_step;
			imag += strided_step;
		}
	}
} 

