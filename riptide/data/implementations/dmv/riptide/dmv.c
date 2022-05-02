#include "stdint.h"

#include "helpers.h"

void dmv(CONST_PTR(int16_t) A, CONST_PTR(int16_t) B, 
	PTR(int16_t) Z, uint32_t m, uint32_t n) {
	for(uint32_t i = 0; i < m; i++) {
		int16_t w = 0;
		for(uint32_t j = 0; j < n; j++) {
			w += clip(A[i * n + j] * B[j], 5);
		}
		Z[i] = w;
	}
}
