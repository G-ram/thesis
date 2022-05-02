#include "stdint.h"

#include "helpers.h"

void dmm(CONST_PTR(int16_t) A, CONST_PTR(int16_t) B, PTR(int16_t) Z, 
	uint32_t m, uint32_t n, uint32_t p) {
	for(uint32_t i = 0; i < m; i++) {
		for(uint32_t j = 0; j < p; j++) {
			int16_t w = 0;
			for(uint32_t k = 0; k < n; k++) {
				w += clip(A[i * n + k] * B[k * p + j], 5);
			}
			Z[i * p + j] = w;
		}
	}
}