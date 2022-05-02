#include "stdint.h"

#include "helpers.h"

#undef PTR
#define PTR(typ) typ *

void dfs(CONST_PTR(uint16_t) mat, uint16_t count, uint16_t start, 
	PTR(uint16_t) stack, PTR(uint16_t) visited, PTR(uint16_t) walk) {

	uint32_t stack_pos = 1;
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

	// Walk in DFS order
	while(!empty()) {
		
		// Fetch the next vertex and add it to @walk
		uint16_t next = pop();
		walk[walk_pos] = next;
		walk_pos++;

		// Add unvisited neighbors to the stack
		CONST_PTR(uint16_t) neighbors = mat + (next * count); 
		for (uint32_t i = 0 ; i < count ; i++) {
			uint32_t has_neighbor = neighbors[i] != 0;
			uint32_t is_visited = visited[i] == 1;
			visited[i] = has_neighbor || is_visited;
			stack[stack_pos] = i;
			stack_pos += has_neighbor && !is_visited;
		}
	}
}
