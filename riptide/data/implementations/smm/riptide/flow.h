#include "smm_flow.h"

void task_smm() {
	smm(filter->sparse.sizes, filter->sparse.offsets, filter->data, 
		src->sparse.sizes, src->sparse.offsets, src->data,
		dest->data, rows, cols);
	cwait();
}