#include "helpers.h"

void fft_shuffle(CONST_PTR(int16_t) src_real, CONST_PTR(int16_t) src_imag,
        PTR(int16_t) dst_real, PTR(int16_t) dst_imag, CONST_PTR(uint16_t) shuffle, 
        uint32_t size, uint32_t stride) {

        for(uint32_t i = 0; i < size; i++) {
                uint32_t s = shuffle[i];
                uint32_t idx = s * stride;
                *dst_real = src_real[idx];
                *dst_imag = src_imag[idx];
                dst_real += stride;
                dst_imag += stride;
        }
}
