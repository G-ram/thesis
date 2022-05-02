#include "fft.h"

#if INPUT_SIZE == 1
#include "shuffle_small.h"
#elif INPUT_SIZE == 2
#include "shuffle_medium.h"
#elif INPUT_SIZE == 3
#include "shuffle_large.h"
#else
#include "shuffle_huge.h"
#endif

void task_fft1d();

void task_fft1d() {
	fixed *src_real_ptr_base = MAT_PTR(src_real, row_idx, col_idx);
	fixed *src_imag_ptr_base = MAT_PTR(src_imag, row_idx, col_idx);
	fixed *dest_real_ptr_base = MAT_PTR(dest_real, row_idx, col_idx);
	fixed *dest_imag_ptr_base = MAT_PTR(dest_imag, row_idx, col_idx);

	fixed *dest_real_ptr = dest_real_ptr_base;
	fixed *dest_imag_ptr = dest_imag_ptr_base;
	for (uint16_t i = 0; i < num_elements; i++) {
		*dest_real_ptr = src_real_ptr_base[shuffle[i] * stride];
		*dest_imag_ptr = src_imag_ptr_base[shuffle[i] * stride];
		dest_real_ptr += stride;
		dest_imag_ptr += stride;
	}

	uint16_t Ls = 1;
	while (Ls < num_elements) {
		uint16_t step = (Ls << 1);
		uint16_t strided_step = step * stride;
		for (uint16_t j = 0; j < Ls; j++) {
			fixed theta = F_DIV(F_LIT(j), F_LIT(Ls));
			fixed wr = wrs[theta];
			fixed wi = F_MUL(F_LIT(-flag), wis[theta]);
			fixed *dest_real_ptr1 = dest_real_ptr_base + (j + Ls) * stride;
			fixed *dest_imag_ptr1 = dest_imag_ptr_base + (j + Ls) * stride;
			fixed *dest_real_ptr2 = dest_real_ptr_base + j * stride;
			fixed *dest_imag_ptr2 = dest_imag_ptr_base + j * stride;
			for (uint16_t k = j; k < num_elements; k += step) {
				fixed tr =
					F_SUB(F_MUL(wr, *dest_real_ptr1), F_MUL(wi, *dest_imag_ptr1));
				fixed ti =
					F_ADD(F_MUL(wr, *dest_imag_ptr1), F_MUL(wi, *dest_real_ptr1));
				*dest_real_ptr1 = F_SUB(*dest_real_ptr2, tr);
				*dest_imag_ptr1 = F_SUB(*dest_imag_ptr2, ti);
				*dest_real_ptr2 = F_ADD(*dest_real_ptr2, tr);
				*dest_imag_ptr2 = F_ADD(*dest_imag_ptr2, ti);
				dest_real_ptr1 += strided_step;
				dest_imag_ptr1 += strided_step;
				dest_real_ptr2 += strided_step;
				dest_imag_ptr2 += strided_step;
			}
		}
		Ls <<= 1;
	}

}