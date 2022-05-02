#include "dconv_flow.h"

void task_dconv() {
	uint32_t scols = cols + fcols - 1;
	uint32_t size = rows * cols;
	uint32_t fsize = frows * fcols;
	dconv(src->data, filter->data, dest->data, size, cols, scols, frows, fcols);
	cwait();
}