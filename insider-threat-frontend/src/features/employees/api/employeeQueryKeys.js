/**
 * Centralized React Query key factory for the Employees feature.
 * Keeping this in one place means Batch 3 (mutations) can invalidate
 * exactly the right caches without guessing key shapes.
 */
export const employeeQueryKeys = {
  all: ['employees'],
  lists: () => [...employeeQueryKeys.all, 'list'],
  list: (filters) => [...employeeQueryKeys.lists(), filters],
  details: () => [...employeeQueryKeys.all, 'detail'],
  detail: (id) => [...employeeQueryKeys.details(), id],
  activity: (id, params) => [...employeeQueryKeys.all, 'activity', id, params],
};
