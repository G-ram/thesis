#include "dmv_flow.h"

void task_dmv() {
	dmv(filter->data, src->data, dest->data, rows, cols);
	cwait();
}