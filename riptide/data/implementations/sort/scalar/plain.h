void task_sort();

int16_t partition(fixed *data, int16_t l, int16_t h) {
	int16_t x = data[h]; 
	int16_t i = (l - 1); 

	for(int16_t j = l; j <= h - 1; j++) {
		if (data[j] <= x) {
			i++;
			fixed tmp = data[i];
			data[i] = data[j];
			data[j] = tmp;
		}
	}
	fixed tmp = data[i + 1];
	data[i + 1] = data[h];
	data[h] = tmp;
	return (i + 1); 
}

void task_sort() {
	uint16_t count = MAT_GET_DIM(dest, 0);
	fixed *src_ptr = src->data;
	fixed *dest_ptr = dest->data;
	for(uint16_t i = 0; i < count; i++)
		dest_ptr[i] = src_ptr[i];

	uint16_t l = 0, h = count - 1;
	uint16_t stack[count];
	int16_t top = -1;

	stack[++top] = 0;
	stack[++top] = h; 

	while(top >= 0) {
		h = stack[top--]; 
		l = stack[top--]; 
		
		int16_t p = partition(dest_ptr, l, h); 

		if(p - 1 > l) {
			stack[++top] = l; 
			stack[++top] = p - 1; 
		} 

		if(p + 1 < h) {
			stack[++top] = p + 1; 
			stack[++top] = h; 
		}
	} 
}
