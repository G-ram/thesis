void task_dfs() {
	
	uint32_t stack_pos = 0;
	uint32_t walk_pos = 0;

	// Generic helpers for @stack
	#define push(val) \
	({ \
		stack[stack_pos] = val; \
		stack_pos++; \
	})

	#define pop() \
	({ \
		stack_pos--; \
		uint16_t val = stack[stack_pos]; \
		val; \
	})

	#define empty() (stack_pos == 0)

	// Begin the DFS w/ @start, mark visited
	push(start);
	visited[start] = 1;

	// Walk in DFS order
	while(!empty()) {
		// Fetch the next vertex and add it to @walk
		uint16_t next = pop();
		walk[walk_pos] = next;
		walk_pos++;

		// Add unvisited neighbors to the stack
		uint16_t *neighbors = mat + (next * count); 
		for (uint16_t i = 0 ; i < count ; i++) {
			if (neighbors[i] && !visited[i]) {
				push(i);
				visited[i] = 1;
			}
		}
	}
}
