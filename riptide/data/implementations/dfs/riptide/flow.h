#include "dfs_flow.h"

void task_dfs() {
	stack[0] = start;
	visited[start] = 1;	
	dfs(mat, count, start, stack, visited, walk);
	cwait();
}