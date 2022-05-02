#include "fft_flow.h"
#include "fft_shuffle_flow.h"

#if INPUT_SIZE == 1
#include "shuffle_small.h"
#include "factor_small.h"
#elif INPUT_SIZE == 2
#include "shuffle_medium.h"
#include "factor_medium.h"
#elif INPUT_SIZE == 3
#include "shuffle_large.h"
#include "factor_large.h"
#else
#include "shuffle_huge.h"
#include "factor_huge.h"
#endif

void task_fft1d() {
	fixed *src_real_ptr = MAT_PTR(src_real, row_idx, col_idx);
	fixed *src_imag_ptr = MAT_PTR(src_imag, row_idx, col_idx);
	fixed *dst_real_ptr = MAT_PTR(dest_real, row_idx, col_idx);
	fixed *dst_imag_ptr = MAT_PTR(dest_imag, row_idx, col_idx);

	fft_shuffle(src_real_ptr, src_imag_ptr, 
		dst_real_ptr, dst_imag_ptr,
		shuffle, num_elements, stride);

	uint32_t p = 0;
	uint32_t next_p = 1;
	uint32_t theta = 0;
	uint32_t Ls = 1;
	while(Ls < num_elements) {
		uint32_t step = Ls << 1;
		uint32_t strided_step = stride << next_p;
		uint32_t Ls_stride = stride << p;

		fft(dst_real_ptr, dst_imag_ptr, real_twiddle, imag_twiddle, 
			num_elements, stride, step, Ls, theta, strided_step, Ls_stride);
		theta += Ls;
		Ls = step;
		p = next_p;
		++next_p;
	}

	cwait();
	cwait();
}
