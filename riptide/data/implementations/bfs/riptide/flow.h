#include "bfs_flow.h"

void task_bfs() {
	queue[0] = start;
	visited[start] = 1;
	bfs(rows, cols, count, queue, visited, walk);
	cwait();
}